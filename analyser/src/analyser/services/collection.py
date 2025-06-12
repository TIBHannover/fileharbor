import grpc
import uuid
from concurrent import futures
import logging

from interface import collection_pb2, collection_pb2_grpc


class CollectionServicer(collection_pb2_grpc.CollectionServicer):
    def __init__(self, config, shared_object):
        self.config = config

        self.shared_object = shared_object
        # self.managers = init_plugins(config)
        # self.process_pool = futures.ProcessPoolExecutor(
        #     max_workers=1, initializer=init_process, initargs=(config,)
        # )
        # self.indexing_process_pool = futures.ProcessPoolExecutor(
        #     max_workers=8, initializer=IndexingJob().init_worker, initargs=(config,)
        # )
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
