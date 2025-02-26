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
    def __call__(cls, query):
        # TODO customize the indexing path and plugin behind it
        logging.error(query)

        filters = []
        for term in query["request"].terms:

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

        results = []
        for term in query["request"].terms:

            term_type = term.WhichOneof("term")
            logging.error(term_type)

            if term_type == "vector":
                plugin_results = cls.inference_server(
                    cls.compute_manager, term.vector.analyse.plugin, term.vector.analyse
                )
                feature_vec = list(plugin_results.results[0].result.feature.feature)
                term_results = cls.indexer_manager.search(
                    queries=[
                        {"index_name": k, "value": feature_vec}
                        for k in term.vector.vector_indexes
                    ],
                    filters=filters,
                )
                results.extend(term_results)

        proto_results = analyser_pb2.ListSearchResultReply()
        for x in results:
            entry = proto_results.entries.add()
            entry.id =  x["id"]
            meta_to_proto(entry.meta , x["meta"])



        return results
