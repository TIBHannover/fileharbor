import os
import csv
import time
import uuid
import grpc
import json
import shutil
import struct
import msgpack
import logging
import imageio
import functools

import multiprocessing as mp

from tqdm import tqdm
from multiprocessing.pool import ThreadPool

from analyser import utils

from interface import (
    analyser_pb2,
    analyser_pb2_grpc,
    collection_pb2,
    collection_pb2_grpc,
)
from analyser.utils import image_resize

import argparse
import sys

from analyser.server import Server


def id_to_path(id, image_paths):
    return os.path.join(image_paths, id[0:2], id[2:4], f"{id}.jpg")


def get_entry_with_path(entry, image_paths):
    if "path" not in entry:
        entry["path"] = id_to_path(entry["id"], image_paths)
    else:
        if not os.path.isabs(entry["path"]):
            entry["path"] = os.path.join(image_paths, entry["path"])
        if not os.path.exists(entry["path"]):
            entry["path"] = id_to_path(entry["id"], image_paths)

    if os.path.exists(entry["path"]):
        return entry
    elif "link" in entry.get("origin", {}):
        return entry
    else:
        entry_path = os.path.join(image_paths, f"{entry['id']}.jpg")

        if os.path.exists(entry_path):
            entry["id"] = uuid.uuid4().hex  # reset identifier
            entry["path"] = id_to_path(entry["id"], image_paths)

            os.makedirs(os.path.dirname(entry["path"]), exist_ok=True)

            try:
                shutil.copy(entry_path, entry["path"])
                os.remove(entry_path)

                return entry
            except:
                pass


def list_images(paths, name_as_hash=False):
    if not isinstance(paths, (list, set)):
        if os.path.isdir(paths):
            file_paths = []

            for root, dirs, files in os.walk(paths):
                for f in files:
                    file_path = os.path.abspath(os.path.join(root, f))
                    file_paths.append(file_path)

            paths = file_paths
        else:
            paths = [os.path.abspath(paths)]

    entries = [
        {
            "id": (
                os.path.splitext(os.path.basename(path))[0]
                if name_as_hash
                else uuid.uuid4().hex
            ),
            "filename": os.path.basename(path),
            "path": os.path.abspath(path),
            "meta": [],
            "origin": [],
        }
        for path in paths
    ]

    return entries


def list_json(paths, image_paths=None):
    entries = []

    with open(paths, "r", encoding="utf-8") as f:
        for entry in json.load(f):
            entry = get_entry_with_path(entry, image_paths)
            if entry:
                entries.append(entry)

        logging.info(f"{len(entries)}")

    return entries


def list_jsonl(paths, image_paths=None):
    entries = []

    with open(paths, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)

            entry = get_entry_with_path(entry, image_paths)
            if entry:
                entries.append(entry)

        logging.info(f"{len(entries)}")

    return entries


def list_csv(paths, image_paths=None):
    entries = []

    with open(paths, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            entry = {}

            for k, v in dict(row).items():
                e = entry

                for part in k.split("."):
                    prev, e = e, e.setdefault(part, {})

                if k != "id":
                    try:
                        v = int(v)
                    except:
                        pass

                prev[part] = v

            entry = get_entry_with_path(entry, image_paths)
            if entry:
                entries.append(entry)

        logging.info(f"{len(entries)}")

    return entries


def copy_image_hash(
    image_path,
    image_output,
    hash_value=None,
    resolutions=[{"min_dim": -1, "suffix": ""}],
):
    try:
        if hash_value is None:
            hash_value = uuid.uuid4().hex

        image_output_dir = os.path.join(image_output, hash_value[0:2], hash_value[2:4])

        if not os.path.exists(image_output_dir):
            os.makedirs(image_output_dir)

        image = imageio.imread(image_path)

        for res in resolutions:
            if "min_dim" in res:
                new_image = image_resize(image, min_dim=res["min_dim"])
            else:
                new_image = image

            image_output_file = os.path.join(
                image_output_dir, f"{hash_value}{res['suffix']}.jpg"
            )
            imageio.imwrite(image_output_file, new_image)

        image_output_file = os.path.abspath(
            os.path.join(image_output_dir, f"{hash_value}.jpg")
        )

        return hash, image_output_file
    except ValueError:
        return None
    except struct.error:
        return None


def copy_image(
    entry,
    image_output,
    image_paths=None,
    resolutions=[{"min_dim": 200, "suffix": "_m"}, {"suffix": ""}],
):
    path = entry["path"]
    copy_result = copy_image_hash(path, image_output, entry["id"], resolutions)

    if copy_result is not None:
        _, path = copy_result
        entry.update({"path": path})

        return entry

    return None


def copy_images(
    entries,
    image_output,
    image_paths=None,
    resolutions=[{"min_dim": 200, "suffix": "_m"}, {"suffix": ""}],
):
    entires_result = []

    with mp.Pool(8) as p:
        for entry in p.imap(
            functools.partial(
                copy_image,
                image_output=image_output,
                image_paths=image_paths,
                resolutions=resolutions,
            ),
            entries,
        ):
            if entry is not None:
                entires_result.append(entry)

    return entires_result


def split_batch(entries, batch_size=512):
    if batch_size < 1:
        return [entries]

    return [
        entries[x * batch_size : (x + 1) * batch_size]
        for x in range(len(entries) // batch_size + 1)
    ]


class Client:
    def __init__(self, config):
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 50051)

    def plugin_list(self):
        channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        stub = analyser_pb2_grpc.IndexerStub(channel)
        response = stub.list_plugins(analyser_pb2.ListPluginsRequest())

        result = {}

        for plugin in response.plugins:
            if plugin.type not in result:
                result[plugin.type] = []

            result[plugin.type].append(plugin.name)

        return result

    def analyse(self, inputs, parameters, plugin: str = None):
        channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        stub = analyser_pb2_grpc.IndexerStub(channel)
        request = analyser_pb2.AnalyseRequest()
        for i in inputs:
            input_field = request.inputs.add()
            if i["type"] == "image":
                input_field.name = "image"
                input_field.image.content = open(i["path"], "rb").read()
            elif i["type"] == "string":
                input_field.name = "text"
                input_field.string.text = i["text"]

        for p in parameters:
            parameter_field = request.parameters.add()
            parameter_field.name = p["name"]
            parameter_field.content = str(p["value"]).encode()

            if isinstance(p["value"], float):
                parameter_field.type = analyser_pb2.FLOAT_TYPE
            if isinstance(p["value"], int):
                parameter_field.type = analyser_pb2.INT_TYPE
            if isinstance(p["value"], str):
                parameter_field.type = analyser_pb2.STRING_TYPE

        request.plugin = plugin
        response = stub.analyse(request)
        return response

    def copy_images(self, paths, image_paths=None, image_output=None):
        if not isinstance(paths, (list, set)):
            ext = os.path.splitext(paths)[1]

            if ext == ".json":
                entries = list_json(paths, image_paths)
            elif ext == ".jsonl":
                entries = list_jsonl(paths, image_paths)
            elif ext == ".csv":
                entries = list_csv(paths, image_paths)
            else:
                raise
        else:
            entries = list_images(paths)

        logging.info(f"Client: Copying {len(entries)} images to {image_output}")

        if image_output:
            entries = copy_images(
                entries, image_paths=image_paths, image_output=image_output
            )

        return entries

    def indexing(
        self,
        paths,
        image_paths=None,
        plugins: list = None,
        download: bool = True,
        resolutions=[{"min_dim": 200, "suffix": "_m"}, {"suffix": ""}],
    ):
        if not isinstance(paths, (list, set)):
            ext = os.path.splitext(paths)[1]

            if ext == ".json":
                entries = list_json(paths, image_paths)
            elif ext == ".jsonl":
                entries = list_jsonl(paths, image_paths)
            elif ext == ".csv":
                entries = list_csv(paths, image_paths)
            else:
                raise
        else:
            entries = list_images(paths)

        if download:
            entries_to_download = [
                e for e in entries if ("path" not in e or not os.path.exists(e["path"]))
            ]
            entries_exists = [
                e for e in entries if ("path" in e and os.path.exists(e["path"]))
            ]

            logging.info(f"Client: Downloading {len(entries_to_download)} images")

            entries_to_download = utils.download_entries(
                entries_to_download, image_output=image_paths
            )
            entries = [*entries_exists, *entries_to_download]
        else:
            entries = [
                e for e in entries if ("path" in e and os.path.exists(e["path"]))
            ]

        logging.info(f"Client: Start indexing {len(entries)} images")

        def entry_generator(entries, blacklist):
            for entry in entries:
                if blacklist is not None and entry["id"] in blacklist:
                    continue

                request = analyser_pb2.IndexingRequest()
                request_image = request.image
                request_image.id = entry["id"]

                for k, v in entry["meta"].items():
                    if isinstance(v, (list, set)):
                        for v_1 in v:
                            meta_field = request_image.meta.add()
                            meta_field.key = k

                            if isinstance(v_1, int):
                                meta_field.int_val = v_1
                            if isinstance(v_1, float):
                                meta_field.float_val = v_1
                            if isinstance(v_1, str):
                                meta_field.string_val = v_1
                    else:
                        meta_field = request_image.meta.add()
                        meta_field.key = k

                        if isinstance(v, int):
                            meta_field.int_val = v
                        if isinstance(v, float):
                            meta_field.float_val = v
                        if isinstance(v, str):
                            meta_field.string_val = v

                if "origin" in entry:
                    for k, v in entry["origin"].items():
                        if isinstance(v, (list, set)):
                            for v_1 in v:
                                origin_field = request_image.origin.add()
                                origin_field.key = k

                                if isinstance(v_1, int):
                                    origin_field.int_val = v_1
                                if isinstance(v_1, float):
                                    origin_field.float_val = v_1
                                if isinstance(v_1, str):
                                    origin_field.string_val = v_1
                        else:
                            origin_field = request_image.origin.add()
                            origin_field.key = k

                            if isinstance(v, int):
                                origin_field.int_val = v
                            if isinstance(v, float):
                                origin_field.float_val = v
                            if isinstance(v, str):
                                origin_field.string_val = v

                if "collection" in entry:
                    collection = request_image.collection

                    if "id" in entry["collection"]:
                        collection.id = entry["collection"]["id"]
                    if "name" in entry["collection"]:
                        collection.name = entry["collection"]["name"]
                    if "is_public" in entry["collection"]:
                        collection.is_public = entry["collection"]["is_public"]

                request_image.encoded = open(entry["path"], "rb").read()

                yield request

        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
                ("grpc.keepalive_time_ms", 2**31 - 1),
            ],
        )
        stub = analyser_pb2_grpc.IndexerStub(channel)

        time_start = time.time()
        blacklist = set()
        try_count = 20
        count = 0

        with tqdm(desc="Indexing", total=len(entries)) as pbar:
            while try_count > 0:
                try:
                    gen_iter = entry_generator(entries, blacklist)

                    for i, entry in enumerate(stub.indexing(gen_iter)):
                        blacklist.add(entry.id)
                        pbar.update()
                        count += 1

                        if count % 1000 == 0:
                            speed = count / (time.time() - time_start)
                            logging.info(
                                f"Client: Indexing {count}/{len(entries)} (speed: {speed})"
                            )

                    try_count = 0
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logging.error(e)
                    try_count -= 1

    def status(self, job_id):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.IndexerStub(channel)
        request = analyser_pb2.StatusRequest()
        request.id = job_id

        response = stub.status(request)

        return response.status

    def build_suggester(self, field_name=None):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.IndexerStub(channel)
        request = analyser_pb2.SuggesterRequest()

        if field_name is None:
            field_name = [
                "meta.title",
                "meta.artist_name",
                "meta.location",
                "meta.institution",
                "meta.object_type",
                "meta.medium",
                "origin.name",
                "classifier.*",
            ]

        request.field_names.extend(field_name)
        response = stub.build_suggester(request)

        return response.id

    def search(self, query):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.IndexerStub(channel)
        request = analyser_pb2.SearchRequest()

        for q in query["queries"]:
            if "field" in q and q["field"] is not None:
                type_req = q["field"]

                if not isinstance(type_req, str):
                    return JsonResponse({"status": "error"})

                term = request.terms.add()
                term.text.query = q["query"]
                term.text.field = q["field"]
                term.text.flag = q["flag"]
            elif "query" in q and q["query"] is not None:
                term = request.terms.add()
                term.text.query = q["query"]

            if "reference" in q and q["reference"] is not None:
                request.sorting = "feature"
                term = request.terms.add()

                if os.path.exists(q["reference"]):
                    term.feature.image.encoded = open(q["reference"], "rb").read()
                else:
                    term.feature.image.id = q["reference"]

                if "features" in q:
                    plugins = q["features"]

                    if not isinstance(q["features"], (list, set)):
                        plugins = [q["features"]]

                    for p in plugins:
                        for k, v in p.items():
                            plugins = term.feature.plugins.add()
                            plugins.name = k.lower()
                            plugins.weight = v

        if "sorting" in query and query["sorting"] == "random":
            request.sorting = "random"

        if "mapping" in query and query["mapping"] == "umap":
            request.mapping = "umap"

        response = stub.search(request)

        status_request = analyser_pb2.ListSearchResultRequest(id=response.id)

        for x in range(600):
            try:
                response = stub.list_search_result(status_request)

                return response
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.FAILED_PRECONDITION:
                    pass  # {"status": "running"}
            return

            time.sleep(0.01)

        return {"error"}

    def get(self, id):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.IndexerStub(channel)
        request = analyser_pb2.GetRequest(id=id)

        response = stub.get(request)

        return response

    def build_indexer(self, rebuild=False, collections=None):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.IndexerStub(channel)
        request = analyser_pb2.BuildIndexerRequest(
            collections=collections, rebuild=rebuild
        )

        response = stub.build_indexer(request)

        return response

    def build_feature_cache(self):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.IndexerStub(channel)
        request = analyser_pb2.BuildFeatureCacheRequest()

        response = stub.build_feature_cache(request)

        return response

    def dump(self, output_path, origin):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.IndexerStub(channel)
        request = analyser_pb2.DumpRequest(origin=origin)

        with open(output_path, "wb") as f:
            for i, x in enumerate(stub.dump(request)):
                f.write(x.entry)

                if i % 1000 == 0:
                    print(i)

    def load(self, input_path):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.IndexerStub(channel)

        def entry_generator(path, blacklist=None):
            with open(path, "rb") as f:
                unpacker = msgpack.Unpacker(f)

                for entry in unpacker:
                    if blacklist is not None and entry["id"] in blacklist:
                        continue

                    yield analyser_pb2.LoadRequest(entry=msgpack.packb(entry))

        time_start = time.time()

        blacklist = set()
        try_count = 20
        count = 0

        with tqdm(desc="Loading") as pbar:
            while try_count > 0:
                try:
                    gen_iter = entry_generator(input_path, blacklist)

                    for i, entry in enumerate(stub.load(gen_iter)):
                        blacklist.add(entry.id)
                        pbar.update()
                        count += 1

                        if count % 1000 == 0:
                            speed = count / (time.time() - time_start)
                            logging.info(f"Client: Loading {count} (speed: {speed})")

                    try_count = 0
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logging.error(e)
                    try_count -= 1

    def aggregate(self, part, type, field_name, size):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.IndexerStub(channel)
        request = analyser_pb2.AggregateRequest(
            type=type, part=part, field_name=field_name, size=size
        )

        response = stub.aggregate(request)

        return response

    def create_collection(self, parameters):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = collection_pb2_grpc.CollectionStub(channel)
        request = collection_pb2.CollectionAddRequest()
        request.name = parameters.get("name")
        for index in parameters.get("indexes"):
            request_index = request.indexes.add()
            request_index.name = index.get("name")
            request_index.size = index.get("size")
            request_index.distance = index.get("distance", "Cosine")

        response = stub.add(request)

        return response

    def delete_collection(self, parameters):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = collection_pb2_grpc.CollectionStub(channel)
        request = collection_pb2.CollectionDeleteRequest()
        request.name = parameters.get("name")

        response = stub.delete(request)

        return response


def parse_args():
    parser = argparse.ArgumentParser(description="Indexing a set of images")

    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument("-d", "--debug", action="store_true", help="verbose output")
    # parser.add_argument('-l', '--list', help='list all plugins')

    parser.add_argument("--host", help="")
    parser.add_argument("--port", type=int, help="")
    parser.add_argument("--plugins", nargs="+", help="")
    parser.add_argument("--image_paths", help="")
    parser.add_argument("--analyse_inputs", help="")
    parser.add_argument("--analyse_parameters", help="")

    parser.add_argument("--parameters", help="")
    parser.add_argument("--query", help="")
    parser.add_argument("--batch", default=512, type=int, help="split images in batch")

    parser.add_argument(
        "--task",
        choices=[
            "list_plugins",
            "copy_images",
            "indexing",
            "bulk_indexing",
            "build_suggester",
            "get",
            "analyse",
            "search",
            "aggregate",
            "build_feature_cache",
            "build_indexer",
            "load",
            "dump",
            "create-collection",
            "delete-collection",
        ],
        help="verbose output",
    )

    parser.add_argument("--dump_path", help="path to image or folder to indexing")
    parser.add_argument("--dump_origin", help="name of a collection to dump")
    parser.add_argument("--path", help="path to image or folder to indexing")
    parser.add_argument("--id", help="id for entry query")
    parser.add_argument("--field_name", nargs="+", help="id for entry query")

    parser.add_argument("--output", help="copy image to new folder with hash id")
    parser.add_argument("--image_output", help="copy image to new folder with hash id")

    parser.add_argument("--aggr_part", help="id for entry query")
    parser.add_argument("--aggr_type", help="id for entry query")
    parser.add_argument("--aggr_field_name", help="id for entry query")
    parser.add_argument("--aggr_size", type=int, help="id for entry query")

    parser.add_argument("--rebuild", action="store_true", help="verbose output")
    parser.add_argument("--collections", nargs="+", help="id for entry query")
    parser.add_argument("--collection", help="id for entry query")

    parser.add_argument("-c", "--config", help="config path")

    args = parser.parse_args()
    return args


def read_config(path):
    with open(path, "r") as f:
        return json.load(f)
    return {}


def main():
    args = parse_args()
    level = logging.ERROR
    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO

    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=level,
    )

    if args.config is not None:
        config = read_config(args.config)
    else:
        config = {}

    if args.host is not None:
        config["host"] = args.host

    if args.port is not None:
        config["port"] = args.port

    client = Client(config)
    if args.task == "list_plugins":
        available_plugins = client.plugin_list()
        print(available_plugins)

    elif args.task == "indexing":
        available_plugins = client.plugin_list()
        plugins = []
        plugins_selected = None
        if args.plugins:
            plugins_selected = [x.lower() for x in args.plugins]
        for t, plugin_list in available_plugins.items():
            for plugin in plugin_list:
                if plugins_selected is not None:
                    if plugin.lower() in plugins_selected:
                        plugins.append(plugin)
                else:
                    plugins.append(plugin)

        client.indexing(
            paths=args.path,
            image_paths=args.image_paths,  # , collection=args.collection
        )

    elif args.task == "get":
        print(client.get(args.id))

    elif args.task == "search":
        # try:
        query = json.loads(args.query)
        # except:
        #     query = {"queries": [{"type": "meta", "query": args.query}]}
        time_start = time.time()
        client.search(query)
        time_stop = time.time()
        print(time_stop - time_start)

    elif args.task == "dump":
        client.dump(args.dump_path, args.dump_origin)

    elif args.task == "load":
        client.load(args.dump_path)

    elif args.task == "analyse":
        available_plugins = client.plugin_list()
        plugins = []
        plugins_selected = None
        if args.plugins:
            plugins_selected = [x.lower() for x in args.plugins]
        for t, plugin_list in available_plugins.items():
            for plugin in plugin_list:
                if plugins_selected is not None:
                    if plugin.lower() in plugins_selected:
                        plugins.append(plugin)
                else:
                    plugins.append(plugin)
        print(
            client.analyse(
                json.loads(args.analyse_inputs),
                json.loads(args.analyse_parameters),
                plugins[0],
            )
        )
    elif args.task == "create-collection":
        client.create_collection(
            json.loads(args.parameters),
        )
    elif args.task == "delete-collection":
        client.delete_collection(
            json.loads(args.parameters),
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
