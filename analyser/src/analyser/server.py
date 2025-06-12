import copy
import grpc
import sys
import time
import json
import uuid
import tomllib

import argparse
import imageio.v3 as iio
import logging
import traceback

from data import DataManager
from interface import (
    analyser_pb2,
    analyser_pb2_grpc,
    searcher_pb2,
    searcher_pb2_grpc,
    collection_pb2,
    collection_pb2_grpc,
)

from typing import Dict

from concurrent import futures

from shared_object import SharedObject
from plugins import IndexerFactory
from interface.utils import meta_from_proto

from jobs import IndexingJob, SearchJob

from services import AnalyserServicer, CollectionServicer, SearcherServicer
from inference import InferenceServerFactory, InferenceServerManager
from plugins import ComputePluginFactory, ComputePluginManager


class Server:
    def __init__(self, config):
        self.config = config
        inference_server_manager = InferenceServerManager(config)
        compute_plugin_manager = ComputePluginManager(
            config, inference_server_manager=inference_server_manager
        )

        indexes = self.check_and_init_indexes(compute_plugin_manager)

        self.shared_object = SharedObject(
            config,
            inference_server_manager=inference_server_manager,
            compute_plugin_manager=compute_plugin_manager,
            indexes=indexes,
        )

        self.indexer_servicer = AnalyserServicer(config, self.shared_object)
        self.collection_servicer = CollectionServicer(config, self.shared_object)
        self.searcher_servicer = SearcherServicer(config, self.shared_object)

        self.server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10),
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        searcher_pb2_grpc.add_SearcherServicer_to_server(
            self.searcher_servicer,
            self.server,
        )

        analyser_pb2_grpc.add_AnalyserServicer_to_server(
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

        logging.info("Start all inference servers")
        inference_server_manager.start()

    def init_indexes(
        self,
        indexer_plugin,
        compute_plugin_manager: ComputePluginManager,
        index,
        # target_index_configuration,
        # current_index_configuration=None,
    ):

        # check what the configuration wants
        target_index_configuration = []
        for indexing_plugin in index.get("indexing_plugin", []):
            compute_plugin = compute_plugin_manager[
                indexing_plugin.get("compute_plugin")
            ]

            target_index_configuration.append(
                {
                    "name": indexing_plugin.get("index_name"),
                    "size": compute_plugin["compute_plugin"].embedding_size,
                }
            )

        # check if the collection exists and what are the indexes
        current_index_configuration = indexer_plugin.get_collection_indexes(
            index.get("name")
        )

        # there is nothing so we will create an index
        if current_index_configuration is None:
            logging.info(f'Create new collection "{index.get("name")}"')
            indexer_plugin.create_collection(
                name=index.get("name"),
                indexes=target_index_configuration,
            )
            return

        # check if the existing index is compatible with the target index from the config
        current_index_configuration = {
            x["name"]: x["size"] for x in current_index_configuration
        }
        match = True
        for x in target_index_configuration:
            if x["name"] in current_index_configuration:
                if x["size"] != current_index_configuration[x["name"]]:
                    logging.error(
                        f'Size different between existing index and configuration for index "{x['name']}" ({x['size']} vs {current_index_configuration[x['name']]}).'
                    )
                    match = False

            else:
                logging.error(
                    f'Target index "{x['name']}" didn\'t exists in current collection.'
                )
                match = False

        if not match:
            logging.error(
                f'Target index "{x['name']}" is not compatible with the existing index'
            )
            # TODO fix
            exit()

    def check_and_init_indexes(self, compute_plugin_manager: ComputePluginManager):

        indexer_plugin_factory = IndexerFactory()

        # Build an dict with index name to indexer plugin and config
        indexes = {}
        for index in self.config.get("index", []):
            index_name = index.get("name")
            if index_name is None and not isinstance(index_name, str):
                logging.error("Index has no name field or it is not a string.")
                exit(-1)

            indexer_plugin_config = index.get("indexer_plugin")
            if indexer_plugin_config is None or not isinstance(
                indexer_plugin_config, dict
            ):
                logging.error(
                    f'Index "{index_name}" has no indexer_plugin field or it is not a dictionary.'
                )
                exit(-1)

            indexer_plugin_type = indexer_plugin_config.get("type")
            if indexer_plugin_type is None or not isinstance(indexer_plugin_type, str):
                logging.error(
                    f'Index "{index_name}" has no type field or it is not a dictionary.'
                )
                exit(-1)

            indexer_plugin = indexer_plugin_factory.build(
                indexer_plugin_type, config=indexer_plugin_config.get("params", {})
            )

            if index_name in indexes:
                logging.error(
                    f'There is more than one index with the name "{index_name}".'
                )

            self.init_indexes(indexer_plugin, compute_plugin_manager, index)

            indexes[index_name] = {"indexer_plugin": indexer_plugin, "config": index}

        return indexes

    def run(self):
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
    with open(path, "rb") as f:
        return tomllib.load(f)
    return {}


def main():
    args = parse_args()
    level = logging.ERROR
    if args.debug:
        print("LOGGING::DEBUG")
        level = logging.DEBUG
    elif args.verbose:
        print("LOGGING::INFO")
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
