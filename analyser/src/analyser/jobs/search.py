import logging

from inference import InferenceServerFactory
from plugins import IndexerPluginManager, ComputePluginManager
from plugins.cache import Cache
from data import DataManager
from fnmatch import fnmatch

from interface import searcher_pb2, common_pb2

from interface.utils import meta_to_proto
from google.protobuf.json_format import MessageToDict, ParseDict

from typing import Dict
from analyser.shared_object import SharedObject


class SearchJob:
    def __init__(self, shared_object: SharedObject, config: Dict = None):
        self.shared_object = shared_object
        if config is None:
            config = {}
        self.config = config

    def reranking(self, result_list):
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

    def search_collection(self, query, collection):

        collection_manager = self.shared_object.indexer_plugin_manager

        indexing_plugin_mappings = collection_manager.get_indexing_plugin_mappings(
            collection
        )

        search_plugin_mappings = collection_manager.get_search_plugin_mappings(
            collection
        )

        payload_mapping = collection_manager.get_payload_mapping(collection)

        print(f"indexing_plugin_mappings {indexing_plugin_mappings}", flush=True)
        print(f"search_plugin_mappings {search_plugin_mappings}", flush=True)
        print(f"payload_mapping {payload_mapping}", flush=True)

        filters = []
        for term in query.terms:

            term_type = term.WhichOneof("term")
            logging.error(term)

            if term_type == "text":

                flag = "MUST"
                if term.text.flag == searcher_pb2.TextSearchTerm.SHOULD:
                    flag = "SHOULD"
                if term.text.flag == searcher_pb2.TextSearchTerm.NOT:
                    flag = "NOT"
                filters.append(
                    {"field": term.text.field, "query": term.text.query, "flag": flag}
                )

            if term_type == "vector":
                vector_term = term.vector

                data_dict = {}
                for vector_input in vector_term.inputs:
                    input_type = vector_input.WhichOneof("data")
                    if input_type == "text":
                        data_dict[vector_input.name] = vector_input

                data_plugin_mapping = []
                for search_plugin_mapping in search_plugin_mappings:
                    for field in search_plugin_mapping.fields:
                        for name, data in data_dict.items():
                            if fnmatch(name, field):

                                data_plugin_mapping.append(
                                    (search_plugin_mapping, name, data)
                                )
                print(f"data_dict {data_dict}", flush=True)
                print(f"term {term}", flush=True)
                print(f"data_plugin_mapping {data_plugin_mapping}", flush=True)
                feature_list = []
                for data_plugin in data_plugin_mapping:
                    data = data_plugin[2]
                    index_name = data_plugin[0].index_name

                    for k, v in data_plugin[0].input_mapping.items():
                        if fnmatch(data_plugin[1], k):
                            data.name = v

                    request = common_pb2.PluginRun(
                        plugin=data_plugin[0].compute_plugin,
                        inputs=[data],
                    )

                    results = self.shared_object.inference_server_manager(
                        self.shared_object.compute_plugin_manager,
                        compute_plugin_name=data_plugin[0].compute_plugin,
                        request=request,
                    )

                    if not results or len(results.results) <= 0:
                        logging.warning("Not plugin output")
                        continue

                    # TODO multivector plugins
                    feature_vecs = list(results.results[0].result.feature.feature)
                    feature_list.append(
                        {"index_name": index_name, "value": feature_vecs}
                    )

                # print({"features": feature_dict}, flush=True)
            result = self.shared_object.indexer_plugin_manager.search(
                collection_name=collection, queries=feature_list, filters=filters
            )
            logging.info(f"Result: {len(result)}")
            return result
        # results = []
        # for term in request.terms:

        #     term_type = term.WhichOneof("term")
        #     logging.error(term_type)

        #     if term_type == "plugin_vector":
        #         plugin_results = cls.inference_server(
        #             cls.compute_manager, term.vector.analyse.plugin, term.vector.analyse
        #         )
        #         feature_vec = list(plugin_results.results[0].result.feature.feature)
        #         term_results = cls.indexer_manager.search(
        #             queries=[
        #                 {
        #                     "index_name": k.name,
        #                     "value": feature_vec,
        #                     "weight": k.weight,
        #                 }
        #                 for k in term.vector.vector_indexes
        #                 if k.name in collection_indexes_info_lut
        #             ],
        #             filters=filters,
        #         )
        #         results.extend(term_results)

    def __call__(self, query):
        # TODO customize the indexing path and plugin behind it
        logging.error(query)

        request = ParseDict(query["request"], searcher_pb2.SearchRequest())

        collection_manager = self.shared_object.indexer_plugin_manager

        collections = request.collections

        if len(request.collections) == 0:
            collections = collection_manager.list_collections()

        results = []
        for collection in collections:
            result = self.search_collection(request, collection)
            results.extend(result)

        results = self.reranking(results)

        proto_results = searcher_pb2.ListSearchResultReply()
        for x in results:
            entry = proto_results.entries.add()
            entry.id = x["id"]
            meta_to_proto(entry.meta, x["meta"])
            # print("SEARCHENTRY", entry, flush=True)

        return MessageToDict(proto_results)
