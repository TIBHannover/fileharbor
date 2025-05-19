import logging
import imageio
import traceback
from packaging import version

from analyser.utils import image_normalize
from inference import InferenceServerFactory
from plugins import IndexerPluginManager, MappingPluginManager, ComputePluginManager
from plugins.cache import Cache
from data import DataManager

from interface import analyser_pb2

from interface.utils import (
    meta_from_proto,
    meta_to_proto,
    classifier_to_proto,
    feature_to_proto,
)
from google.protobuf.json_format import MessageToJson, MessageToDict, ParseDict


class SearchJob:
    def __init__(self, config=None):
        if config is not None:
            self.init_worker(config)

    @classmethod
    def init_worker(cls, config):
        inference_server_config = config.get("inference_server", {})
        inference_server = InferenceServerFactory.build(
            inference_server_config["type"], config=inference_server_config["params"]
        )
        setattr(cls, "inference_server", inference_server)

        compute_manager = ComputePluginManager(
            configs=config.get("compute_plugins", [])
        )
        setattr(cls, "compute_manager", compute_manager)

        indexer_manager = IndexerPluginManager(configs=config.get("indexes", []))
        indexer_manager.find()
        setattr(cls, "indexer_manager", indexer_manager)

        cache = Cache(
            cache_dir=config.get("cache", {"cache_dir": None})["cache_dir"], mode="r"
        )
        setattr(cls, "cache", indexer_manager)

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
        setattr(cls, "data_manager", data_manager)

    @classmethod
    def reranking(cls, result_list):
        # build lut key, [results]
        lut = {}
        for x in result_list:
            lut.setdefault(x["id"], [])
            lut[x["id"]].append(x)

        # compute max score
        result = []
        for _, v in lut.items():
            # s = max([x["score"] for x in v])
            s = sum([x["score"] for x in v]) / len(v)

            result.append([v[0], s])

        # sort after lowest key
        result_list = [x[0] for x in sorted(result, key=lambda x: -x[1])]

        return result_list

    @classmethod
    def __call__(cls, query):
        # TODO customize the indexing path and plugin behind it
        logging.error(query)

        request = ParseDict(query["request"], analyser_pb2.SearchRequest())

        filters = []
        for term in request.terms:

            term_type = term.WhichOneof("term")
            logging.error(term_type)

            if term_type == "text":

                flag = "MUST"
                if term.text.flag == analyser_pb2.TextSearchTerm.SHOULD:
                    flag = "SHOULD"
                if term.text.flag == analyser_pb2.TextSearchTerm.NOT:
                    flag = "NOT"
                filters.append(
                    {"field": term.text.field, "query": term.text.query, "flag": flag}
                )

        # test if the index exist in this collection
        collection_indexes_info = cls.indexer_manager.get_collection_indexes()

        collection_indexes_info_lut = {
            x["name"]: x["size"] for x in collection_indexes_info
        }
        print("#################################")
        print(collection_indexes_info, flush=True)
        print(collection_indexes_info_lut, flush=True)
        print("#################################")

        results = []
        for term in request.terms:
            print(term.vector.vector_indexes, flush=True)

            term_type = term.WhichOneof("term")
            logging.error(term_type)

            if term_type == "vector":
                plugin_results = cls.inference_server(
                    cls.compute_manager, term.vector.analyse.plugin, term.vector.analyse
                )
                feature_vec = list(plugin_results.results[0].result.feature.feature)
                term_results = cls.indexer_manager.search(
                    queries=[
                        {"index_name": k.name, "value": feature_vec}
                        for k in term.vector.vector_indexes
                        if k.name in collection_indexes_info_lut
                    ],
                    filters=filters,
                )
                results.extend(term_results)

        # Reranking

        results = cls.reranking(results)

        proto_results = analyser_pb2.ListSearchResultReply()
        for x in results:
            entry = proto_results.entries.add()
            entry.id = x["id"]
            meta_to_proto(entry.meta, x["meta"])
            print("SEARCHENTRY", entry, flush=True)

        return MessageToDict(proto_results)
