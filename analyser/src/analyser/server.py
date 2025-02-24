import re
import copy
import grpc
import sys
import time
import json
import uuid

import argparse
import imageio.v3 as iio
import logging
import traceback

from data import DataManager
from interface import (
    analyser_pb2,
    analyser_pb2_grpc,
    collection_pb2,
    collection_pb2_grpc,
)

from inference import InferenceServerFactory

from concurrent import futures
from google.protobuf.json_format import MessageToJson, MessageToDict, ParseDict

from plugins import IndexerPluginManager, MappingPluginManager, ComputePluginManager
from utils import (
    meta_from_proto,
    meta_to_proto,
    classifier_to_proto,
    feature_to_proto,
)

from jobs import IndexingJob
from search import Searcher

from plugins.cache import Cache

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def search(args):
    logging.info("Search: Start")

    try:
        start_time = time.time()

        query = ParseDict(args["query"], analyser_pb2.SearchRequest())
        config = args["config"]

        database = ElasticSearchDatabase(config=config.get("elasticsearch", {}))

        compute_manager = globals().get("compute_manager")
        mapping_plugin_manager = globals().get("mapping_manager")
        indexer_plugin_manager = globals().get("indexer_manager")

        classifier_plugin_manager = None
        # indexer_plugin_manager = None

        aggregator = Aggregator(database)
        searcher = Searcher(
            database,
            compute_manager,
            classifier_plugin_manager,
            indexer_plugin_manager,
            mapping_plugin_manager,
            aggregator=aggregator,
        )

        logging.info(f"Init done: {time.time() - start_time}")

        search_result = searcher(query)
        logging.info(f"Search done: {time.time() - start_time}")

        result = analyser_pb2.ListSearchResultReply()

        for e in search_result["entries"]:
            entry = result.entries.add()
            entry.id = e["id"]
            entry.padded = e["padded"]

            if "meta" in e:
                meta_to_proto(entry.meta, e["meta"])
            if "origin" in e:
                meta_to_proto(entry.origin, e["origin"])
            if "classifier" in e:
                classifier_to_proto(entry.classifier, e["classifier"])
            if "feature" in e:
                feature_to_proto(entry.feature, e["feature"])
            if "coordinates" in e:
                entry.coordinates.extend(e["coordinates"])
            if "distance" in e:
                entry.distance = e["distance"]
            if "cluster" in e:
                entry.cluster = e["cluster"]
            if "collection" in e:
                entry.collection.id = e["collection"]["id"]
                entry.collection.name = e["collection"]["name"]
                entry.collection.is_public = e["collection"]["is_public"]

        if "aggregations" in search_result:
            for e in search_result["aggregations"]:
                aggr = result.aggregate.add()
                aggr.field_name = e["field_name"]

                for y in e["entries"]:
                    value_field = aggr.entries.add()
                    value_field.key = y["name"]
                    value_field.int_val = y["value"]

        result_dict = MessageToDict(result)

        return result_dict
    except Exception as e:
        logging.error(f"Indexer: {repr(e)}")
        exc_type, exc_value, exc_traceback = sys.exc_info()

        traceback.print_exception(
            exc_type,
            exc_value,
            exc_traceback,
            limit=2,
            file=sys.stdout,
        )

    return None


def init_plugins(config):
    data_dict = {}

    inference_server_config = config.get("inference_server", {})
    inference_server = InferenceServerFactory.build(
        inference_server_config["type"], config=inference_server_config["params"]
    )
    data_dict["inference_server"] = inference_server

    compute_manager = ComputePluginManager(configs=config.get("compute_plugins", []))

    data_dict["compute_manager"] = compute_manager

    indexer_manager = IndexerPluginManager(configs=config.get("indexes", []))
    indexer_manager.find()

    data_dict["indexer_manager"] = indexer_manager

    mapping_manager = MappingPluginManager(configs=config.get("mappings", []))
    mapping_manager.find()

    data_dict["mapping_manager"] = mapping_manager

    cache = Cache(
        cache_dir=config.get("cache", {"cache_dir": None})["cache_dir"], mode="r"
    )

    data_dict["cache"] = cache

    data_config = config.get("data", None)
    data_dir = None
    if data_config is not None:
        data_dir = data_config.get("data_dir", None)
        cache_config = data_config.get("cache")
        if cache_config is not None:
            cache = CacheManager.build(
                name=cache_config["type"], config=cache_config["params"]
            )

    data_manager = DataManager(data_dir=data_dir, cache=cache)
    data_dict["data_manager"] = data_manager

    return data_dict


def init_process(config):
    globals().update(init_plugins(config))


class IndexerServicer(analyser_pb2_grpc.IndexerServicer):
    def __init__(self, config):
        self.config = config
        self.managers = init_plugins(config)
        self.process_pool = futures.ProcessPoolExecutor(
            max_workers=1, initializer=init_process, initargs=(config,)
        )
        self.indexing_process_pool = futures.ProcessPoolExecutor(
            max_workers=8, initializer=IndexingJob().init_worker, initargs=(config,)
        )
        self.futures = []

        self.max_results = config.get("indexer", {}).get("max_results", 100)

    def analyse(self, request, context):
        logging.info(f"Received analyse request, plugins: {request.plugin}")

        results = self.managers["inference_server"](
            self.managers["compute_manager"], request.plugin, request
        )

        # results = list(self.managers["compute_manager"].run([image], [plugins], plugins=plugins))
        print(results, flush=True)

        return results

    def list_plugins(self, request, context):
        reply = analyser_pb2.ListPluginsReply()

        for plugin_name, plugin_class in (
            self.managers["compute_manager"].plugins().items()
        ):
            pluginInfo = reply.plugins.add()
            pluginInfo.name = plugin_name

        return reply

    def indexing(self, request_iterator, context):
        logging.info(f"[Server] Indexing: start indexing")
        job_id = uuid.uuid4().hex

        with (
            self.managers["data_manager"].create_data("ImagesData") as images_data,
            self.managers["data_manager"].create_data("ListData") as list_data,
        ):

            for data_point in request_iterator:
                # TODO check if key already exists
                data_id = (
                    data_point.image.id if data_point.image.id else uuid.uuid4().hex
                )
                meta = meta_from_proto(data_point.image.meta)
                origin = meta_from_proto(data_point.image.origin)

                collection = {}

                if data_point.image.collection.id != "":
                    collection["id"] = data_point.image.collection.id
                    collection["name"] = data_point.image.collection.name
                    collection["is_public"] = data_point.image.collection.is_public

                index_data = {
                    # "image_data": data_point.image.encoded,
                    "meta": meta,
                    "origin": origin,
                    "collection": collection,
                }
                try:
                    image = iio.imread(data_point.image.encoded)
                    logging.error(image.shape)
                except Exception as e:

                    yield analyser_pb2.IndexingReply(
                        status="error", id=data_id, indexing_job_id=job_id
                    )
                    print(e)
                    continue

                yield analyser_pb2.IndexingReply(
                    status="ok", id=data_id, indexing_job_id=job_id
                )

                with list_data.create_data("MetaData") as meta_data:
                    meta_data.meta = index_data
                    meta_data.ref_id = data_id

                images_data.save_image(image, id=data_id)
        logging.error(images_data.id)

        #
        variable = {
            "future": None,
            "id": job_id,
            "object_id": images_data.id,
            "meta_id": list_data.id,
        }

        indexing_job = IndexingJob()
        indexing_job.init_worker(self.config)
        indexing_job(copy.deepcopy(variable))

        # future = self.indexing_process_pool.submit(
        #     IndexingJob(), copy.deepcopy(variable)
        # )
        # variable["future"] = future
        # self.futures.append(variable)

    def status(self, request, context):
        futures_lut = {x["id"]: i for i, x in enumerate(self.futures)}

        if request.id in futures_lut:
            job_data = self.futures[futures_lut[request.id]]
            done = job_data["future"].done()

            if not done:
                return analyser_pb2.StatusReply(status="running")

            result = job_data["future"].result()

            if result is None:
                return analyser_pb2.StatusReply(status="error")

            return analyser_pb2.StatusReply(status="done", indexing=result)

        return analyser_pb2.StatusReply(status="error")

    def get(self, request, context):
        database = ElasticSearchDatabase(config=self.config.get("elasticsearch", {}))

        entry = database.get_entry(request.id)

        if entry is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Entry unknown")

            return analyser_pb2.GetReply()

        result = analyser_pb2.GetReply()
        result.id = entry["id"]

        if "meta" in entry:
            meta_to_proto(result.meta, entry["meta"])
        if "collection" in entry:
            logging.info(entry["collection"])
            result.collection.id = entry["collection"]["id"]
            result.collection.name = entry["collection"]["name"]
            result.collection.is_public = entry["collection"]["is_public"]
        if "origin" in entry:
            meta_to_proto(result.origin, entry["origin"])
        if "classifier" in entry:
            classifier_to_proto(result.classifier, entry["classifier"])
        if "feature" in entry:
            feature_to_proto(result.feature, entry["feature"])

        return result

    def search(self, request, context):
        jsonObj = MessageToDict(request)
        logging.info(jsonObj)

        job_id = uuid.uuid4().hex
        variable = {
            "query": jsonObj,
            "config": self.config,
            "future": None,
            "id": job_id,
        }

        future = self.process_pool.submit(search, copy.deepcopy(variable))
        variable["future"] = future
        self.futures.append(variable)

        return analyser_pb2.SearchReply(id=job_id)

    def list_search_result(self, request, context):
        futures_lut = {x["id"]: i for i, x in enumerate(self.futures)}

        if request.id in futures_lut:
            job_data = self.futures[futures_lut[request.id]]
            done = job_data["future"].done()

            if not done:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("Still running")
                return analyser_pb2.ListSearchResultReply()
            try:
                result = job_data["future"].result()
                result = ParseDict(result, analyser_pb2.ListSearchResultReply())
            except Exception as e:
                logging.error(f"Indexer: {repr(e)}")
                logging.error(traceback.format_exc())
                result = None

            if result is None:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Search error")
                return analyser_pb2.ListSearchResultReply()

            return result

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Job unknown")

        return analyser_pb2.ListSearchResultReply()

    def aggregate(self, request, context):
        jsonObj = MessageToJson(request)
        logging.info(jsonObj)
        database = ElasticSearchDatabase(config=self.config.get("elasticsearch", {}))
        aggregator = Aggregator(database)

        size = 5 if request.size <= 0 else request.size
        result_list = []

        if request.part == "meta" and request.type == "count":
            result_list = aggregator.meta_text_count(
                field_name=request.field_name, size=size
            )
        elif request.part == "origin" and request.type == "count":
            result_list = aggregator.origin_test_count(
                field_name=request.field_name, size=size
            )
        elif request.part == "feature" and request.type == "count":
            result_list = aggregator.feature_count(size=size)
        elif request.part == "classifier" and request.type == "count":
            result_list = aggregator.classifier_tag_count(size=size)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Job unknown")

        result = analyser_pb2.AggregateReply()

        for x in result_list:
            f = result.field.add()
            f.key = x["name"]
            f.int_val = x["value"]

        return result

    def collection_delete(self, request, context):
        logging.info("[Server] collection_delete")
        logging.info(request.id)

        database = ElasticSearchDatabase(config=self.config.get("elasticsearch", {}))
        result = database.raw_delete(
            {
                "query": {
                    "nested": {
                        "path": "collection",
                        "query": {"terms": {"collection.id": [request.id]}},
                    }
                }
            }
        )

        logging.info(f"[Server] {result}")

        result = analyser_pb2.CollectionDeleteReply()  # collections,ids)

        # start indexing all
        self.managers["indexer_manager"].delete([request.id])

        return result


class CollectionServicer(collection_pb2_grpc.CollectionServicer):
    def __init__(self, config):
        self.config = config
        self.managers = init_plugins(config)
        self.process_pool = futures.ProcessPoolExecutor(
            max_workers=1, initializer=init_process, initargs=(config,)
        )
        self.indexing_process_pool = futures.ProcessPoolExecutor(
            max_workers=8, initializer=IndexingJob().init_worker, initargs=(config,)
        )
        self.futures = []

        self.max_results = config.get("indexer", {}).get("max_results", 100)

    def add(self, request, context):
        logging.info(f"Received analyse request, plugins: {request}")

        self.managers["indexer_manager"].create_collection(
            name=request.name,
            indexes=[{"name": x.name, "size": x.size} for x in request.indexes],
        )

        return collection_pb2.CollectionAddResponse()

    def delete(self, request, context):
        logging.info(f"Received analyse request, plugins: {request}")

        self.managers["indexer_manager"].delete_collection(
            name=request.name,
        )

        return collection_pb2.CollectionDeleteResponse()

    def list(self, request, context):
        logging.info(f"Received analyse request, plugins: {request.plugin}")

        return results

    def query(self, request, context):
        logging.info(f"Received analyse request, plugins: {request.plugin}")

        return results


class Server:
    def __init__(self, config):
        self.config = config
        self.indexer_servicer = IndexerServicer(config)
        self.collection_servicer = CollectionServicer(config)

        self.server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10),
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        analyser_pb2_grpc.add_IndexerServicer_to_server(
            self.indexer_servicer,
            self.server,
        )

        collection_pb2_grpc.add_CollectionServicer_to_server(
            self.collection_servicer,
            self.server,
        )

        grpc_config = config.get("grpc", {})
        port = grpc_config.get("port", 50051)
        self.server.add_insecure_port(f"[::]:{port}")

        self.compute_manager = ComputePluginManager(
            configs=config.get("compute_plugins", [])
        )

        print(self.compute_manager.plugin_list, flush=True)

        inference_server_config = config.get("inference_server", {})
        self.inference_server = InferenceServerFactory.build(
            inference_server_config["type"], config=inference_server_config["params"]
        )

    def run(self):
        self.inference_server.start(self.compute_manager)
        self.server.start()
        logging.info("[Server] Ready")

        try:
            while True:
                num_jobs = len(self.indexer_servicer.futures)
                num_jobs_done = len(
                    [x for x in self.indexer_servicer.futures if x["future"].done()]
                )
                logging.info(
                    f"[Server] num_jobs:{num_jobs} num_jobs_done:{num_jobs_done}"
                )

                time.sleep(60 * 60)
        except KeyboardInterrupt:
            self.server.stop(0)


def parse_args():
    parser = argparse.ArgumentParser(description="Indexing a set of images")

    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument("-d", "--debug", action="store_true", help="verbose output")

    parser.add_argument("--port", type=int, help="")

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

    server = Server(config)
    server.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
