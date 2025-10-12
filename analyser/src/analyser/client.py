import os
import csv
import time
import uuid
import grpc
import json
import shutil
import struct
import logging
import mimetypes
import imageio.v3 as iio
import functools
from analyser.utils import flat_dict

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


from typing import Dict

import multiprocessing as mp

from tqdm import tqdm
from multiprocessing.pool import ThreadPool

from analyser import utils

from interface import (
    data_pb2,
    common_pb2,
    analyser_pb2,
    analyser_pb2_grpc,
    searcher_pb2,
    searcher_pb2_grpc,
    collection_pb2,
    collection_pb2_grpc,
)
from analyser.utils import image_resize

import argparse
import sys


from typing import Any, Generator, List


def id_to_path(id, image_paths):
    return os.path.join(image_paths, id[0:2], id[2:4], f"{id}.jpg")


def get_entry_with_path(entry, image_paths):
    for data_entry in entry["entries"]:
        if data_entry.get("type") == "image":
            image_id = uuid.uuid5(uuid.NAMESPACE_URL, data_entry["url"]).hex
            data_entry.update(
                {"id": image_id, "file_path": id_to_path(image_id, image_paths)}
            )
    return entry


def entries_to_request(
    entries: List[Dict], collection_name: str
) -> Generator[Any, Any, Any]:
    for entry in entries:
        if not isinstance(entry, dict):
            logging.error("Unkonwn format")
            exit()

        request = collection_pb2.AddPointsRequest()
        request.collection_name = collection_name
        request.id = entry.get("id")

        for data_entry in entry["entries"]:
            try:
                path = data_entry.get("path")
                if data_entry.get("type") == "string":
                    lang = data_entry.get("lang", "en")
                    text = data_entry.get("value")
                    if len(lang) == 0:
                        lang = "en"

                    pb_data_entry = request.data.add()

                    pb_data_entry.name = f"{path}/_{lang}"
                    pb_data_entry.text.text = text
                    pb_data_entry.text.language = lang

                if data_entry.get("type") == "url":
                    text = data_entry.get("url")

                    pb_data_entry = request.data.add()

                    pb_data_entry.name = f"{path}"
                    pb_data_entry.text.text = text

                if data_entry.get("type") == "image":
                    m = mimetypes.guess_type(data_entry["file_path"])[0]
                    if "image" in m:

                        pb_data_entry = request.data.add()
                        pb_data_entry.id = data_entry["id"]
                        pb_data_entry.name = path
                        pb_data_entry.image.content = open(
                            data_entry["file_path"], "rb"
                        ).read()
                        # TODO
                        if "jpeg" in m:
                            pb_data_entry.image.ext = "jpg"
                        else:
                            logging.error(f"Unsupported image type {m}")
                            exit()

                if data_entry.get("type") == "geo":

                    lat = data_entry.get("lat")
                    lon = data_entry.get("lon")

                    pb_data_entry = request.data.add()
                    pb_data_entry.name = path
                    pb_data_entry.geo.lat = lat
                    pb_data_entry.geo.lon = lon

                if data_entry.get("type") == "time":

                    value = data_entry.get("value")

                    pb_data_entry = request.data.add()
                    pb_data_entry.name = path
                    pb_data_entry.int.value = value
            except Exception as e:
                logging.error(f"Indexing error: {e}")
            # elif key == "id":
            #     request.id = str(value)
            # elif isinstance(value, str):
            #     if os.path.exists(value):
            #         m = mimetypes.guess_type(value)[0]
            #         if "image" in m:

            #             request_image = request.data.add()
            #             request_image.name = key
            #             request_image.image.content = open(value, "rb").read()

            #             # TODO
            #             if "jpeg" in m:
            #                 request_image.image.ext = "jpg"
            #             else:
            #                 logging.error(f"Unsupported image type {m}")
            #                 exit()
            #         print()

            # elif isinstance(value, int):
            #     data_entry = request.data.add()
            #     data_entry.name = key
            #     data_entry.int.value = value
            # elif isinstance(value, float):
            #     data_entry = request.data.add()
            #     data_entry.name = key
            #     data_entry.float.value = value
            # else:
            #     logging.error(f"Parsing error 3 {entry} {key} {value}")
            #     exit()
        yield request


def list_jsonl(paths, image_paths=None) -> Generator[Dict, Any, Any]:
    with open(paths, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)

            entry = get_entry_with_path(entry, image_paths)
            if entry:
                yield entry


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

        image = iio.imread(image_path)

        for res in resolutions:
            if "min_dim" in res:
                new_image = image_resize(image, min_dim=res["min_dim"])
            else:
                new_image = image

            image_output_file = os.path.join(
                image_output_dir, f"{hash_value}{res['suffix']}.jpg"
            )
            iio.imwrite(image_output_file, new_image)

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
        stub = analyser_pb2_grpc.AnalyserStub(channel)
        response = stub.list_plugins(analyser_pb2.ListPluginsRequest())

        result = {}

        for plugin in response.plugin_infos:
            if plugin.type not in result:
                result[plugin.type] = []

            result[plugin.type].append(plugin.name)

        return result

    def analyse(self, inputs, parameters, plugin: str = None):
        channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        stub = analyser_pb2_grpc.AnalyserStub(channel)
        request = analyser_pb2.AnalyseRequest()
        for i in inputs:
            input_field = request.plugin_run.inputs.add()
            if i["type"] == "image":
                input_field.name = "image"
                input_field.image.content = open(i["path"], "rb").read()
            elif i["type"] == "string":
                input_field.name = "text"
                input_field.string.text = i["text"]

        for p in parameters:
            parameter_field = request.plugin_run.parameters.add()
            parameter_field.name = p["name"]
            parameter_field.content = str(p["value"]).encode()

            if isinstance(p["value"], float):
                parameter_field.type = common_pb2.FLOAT_TYPE
            if isinstance(p["value"], int):
                parameter_field.type = common_pb2.INT_TYPE
            if isinstance(p["value"], str):
                parameter_field.type = common_pb2.STRING_TYPE

        request.plugin_run.plugin = plugin
        response = stub.analyse(request)
        return response

    def indexing(
        self,
        paths,
        image_paths=None,
        download: bool = True,
        resolutions=[{"min_dim": 200, "suffix": "_m"}, {"suffix": ""}],
        parameters: Dict = None,
    ):
        if not isinstance(paths, (list, set)):
            ext = os.path.splitext(paths)[1]

            if ext == ".jsonl":
                entries = list_jsonl(paths, image_paths)
            else:
                raise

        if download:

            entries = list(entries)

            entries_to_download = []

            for e in entries:
                for data_entry in e["entries"]:
                    if "file_path" in data_entry and "url" in data_entry:
                        entries_to_download.append(data_entry)

            entries_to_download = filter(
                lambda x: not os.path.exists(x["file_path"]), entries_to_download
            )
            entries_to_download = list(entries_to_download)

            logging.info(f"Client: Downloading {len(list(entries_to_download))} images")

            entries_to_download = utils.download_entries(
                entries_to_download, resolutions=resolutions
            )

        logging.info(f"Client: Start indexing {len(entries)} images")

        entries = entries_to_request(entries, parameters.get("collection_name"))

        def entry_generator(entries, blacklist):
            for entry in entries:
                if blacklist is not None and entry.id in blacklist:
                    continue
                yield entry

        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
                ("grpc.keepalive_time_ms", 2**31 - 1),
            ],
        )
        stub = collection_pb2_grpc.CollectionStub(channel)

        time_start = time.time()
        blacklist = set()
        count = 0

        entries = list(entries)

        with tqdm(desc="Indexing") as pbar:
            try:
                gen_iter = entry_generator(entries, blacklist)

                for i, entry in enumerate(stub.add_points(gen_iter)):
                    blacklist.add(entry.id)
                    pbar.update()
                    count += 1

                    if count % 1000 == 0:
                        speed = count / (time.time() - time_start)
                        logging.info(
                            f"Client: Indexing {count}/{len(entries)} (speed: {speed})"
                        )

            except KeyboardInterrupt:
                raise
            except Exception as e:
                logging.error(e)

    def status(self, job_id):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.AnalyserStub(channel)
        request = analyser_pb2.StatusRequest()
        request.id = job_id

        response = stub.status(request)

        return response.status

    def search(self, query):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = searcher_pb2_grpc.SearcherStub(channel)
        request = searcher_pb2.SearchRequest()

        # a = {
        #     "terms": [
        #         {
        #             "type": "plugin_vector",
        #             "params": {
        #                 "name": "ClipText",
        #                 "inputs": [
        #                     {"name": "text", "type": "string", "text": "landscape"}
        #                 ],
        #             "vector_index": ["clip_text", "clip_image"]
        #             },
        #         }
        #     ]
        # }

        for q in query["terms"]:
            print(q, flush=True)
            if q["type"] == "vector":
                vector_params = q.get("params")
                term = request.terms.add()

                for i in vector_params.get("inputs", []):
                    input_field = term.vector.inputs.add()
                    if i["type"] == "image":
                        input_field.name = "image"
                        input_field.image.content = open(i["path"], "rb").read()
                    elif i["type"] == "string":
                        input_field.name = "text"
                        input_field.text.text = i["text"]

                for i in vector_params.get("vector_indexes", []):
                    vector_index = term.vector.vector_indexes.add()
                    vector_index.name = i
                    vector_index.weight = 1.0

            if q["type"] == "plugin_vector":
                plugin_vector_params = q.get("params")
                term = request.terms.add()
                params = q["params"]
                term.plugin_vector.analyse.plugin = params["plugin"]

                for i in params.get("inputs", []):
                    input_field = term.plugin_vector.analyse.inputs.add()
                    if i["type"] == "image":
                        input_field.name = "image"
                        input_field.image.content = open(i["path"], "rb").read()
                    elif i["type"] == "string":
                        input_field.name = "text"
                        input_field.text.text = i["text"]

                for p in params.get("parameters", []):
                    parameter_field = term.plugin_vector.analyse.parameters.add()
                    parameter_field.name = p["name"]
                    parameter_field.content = str(p["value"]).encode()

                    if isinstance(p["value"], float):
                        parameter_field.type = common_pb2.FLOAT_TYPE
                    if isinstance(p["value"], int):
                        parameter_field.type = common_pb2.INT_TYPE
                    if isinstance(p["value"], str):
                        parameter_field.type = common_pb2.STRING_TYPE

                for i in params.get("vector_indexes", []):
                    vector_index = term.plugin_vector.vector_indexes.add()
                    vector_index.name = i
                    vector_index.weight = 1.0

            elif q["type"] == "text":
                text_params = q.get("params")

                term = request.terms.add()
                term.text.query = text_params["query"]
                term.text.field = text_params["field"]

                term.text.flag = searcher_pb2.TextSearchTerm.MUST
                if text_params["flag"] == "SHOULD":
                    term.text.flag = searcher_pb2.TextSearchTerm.SHOULD
                if text_params["flag"] == "NOT":
                    term.text.flag = searcher_pb2.TextSearchTerm.NOT
            # if "field" in q and q["field"] is not None:
            #     type_req = q["field"]

            #     if not isinstance(type_req, str):
            #         return JsonResponse({"status": "error"})

            #     term = request.terms.add()
            #     term.text.query = q["query"]
            #     term.text.field = q["field"]
            #     term.text.flag = q["flag"]
            # elif "query" in q and q["query"] is not None:
            #     term = request.terms.add()
            #     term.text.query = q["query"]

            # if "reference" in q and q["reference"] is not None:
            #     request.sorting = "feature"
            #     term = request.terms.add()

            #     if os.path.exists(q["reference"]):
            #         term.feature.image.encoded = open(q["reference"], "rb").read()
            #     else:
            #         term.feature.image.id = q["reference"]

            #     if "features" in q:
            #         plugins = q["features"]

            #         if not isinstance(q["features"], (list, set)):
            #             plugins = [q["features"]]

            #         for p in plugins:
            #             for k, v in p.items():
            #                 plugins = term.feature.plugins.add()
            #                 plugins.name = k.lower()
            #                 plugins.weight = v

        # if "sorting" in query and query["sorting"] == "random":
        #     request.sorting = "random"

        # if "mapping" in query and query["mapping"] == "umap":
        #     request.mapping = "umap"

        response = stub.search(request)

        status_request = searcher_pb2.ListSearchResultRequest(id=response.id)

        print(status_request, flush=True)

        for x in range(600):
            print("TRY")
            try:
                response = stub.list_search_result(status_request)
                print(response, flush=True)

                print("RESULT")
                return response
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.FAILED_PRECONDITION:
                    pass  # {"status": "running"}
                else:
                    print(e)

            time.sleep(0.1)

        return {"error"}

    def get(self, id):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = analyser_pb2_grpc.AnalyserStub(channel)
        request = analyser_pb2.GetRequest(id=id)

        response = stub.get(request)

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

    def list_collection(self):
        channel = grpc.insecure_channel(
            f"{self.host}:{self.port}",
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        stub = collection_pb2_grpc.CollectionStub(channel)
        request = collection_pb2.CollectionListRequest()

        response = stub.list(request)

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
            "list-collection",
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
            image_paths=args.image_paths,
            parameters=json.loads(args.parameters),
        )

    elif args.task == "get":
        print(client.get(args.id))

    elif args.task == "search":
        # try:
        query = json.loads(args.query)
        # except:
        #     query = {"queries": [{"type": "meta", "query": args.query}]}
        time_start = time.time()
        result = client.search(query)
        print(len(result.entries))
        time_stop = time.time()
        print(time_stop - time_start)

    elif args.task == "dump":
        client.dump(args.dump_path, args.dump_origin)

    elif args.task == "load":
        client.load(args.dump_path)

    elif args.task == "analyse":
        available_plugins = client.plugin_list()
        print(available_plugins)
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
        client.create_collection(json.loads(args.parameters))
    elif args.task == "list-collection":
        print(client.list_collection())

    elif args.task == "delete-collection":
        client.delete_collection(json.loads(args.parameters))

    return 0


if __name__ == "__main__":
    sys.exit(main())
