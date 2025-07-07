import logging
import sys
import traceback
from packaging import version

from analyser.utils import image_normalize


from interface import analyser_pb2, common_pb2, data_pb2
from fnmatch import fnmatch

from typing import Dict
from analyser.shared_object import SharedObject


class IndexingJob:
    def __init__(self, shared_object: SharedObject, config: Dict = None):
        self.shared_object = shared_object
        if config is None:
            config = {}
        self.config = config

    def __call__(self, args):
        # TODO customize the indexing path and plugin behind it
        logging.error(args)

        collection_name = args.get("collection_name")

        collection_manager = self.shared_object.indexer_plugin_manager

        if collection_name not in collection_manager:
            logging.error(f"[IndexingJob] Unknown collection '{collection_name}'")
            return

        indexing_plugin_mappings = collection_manager.get_indexing_plugin_mappings(
            collection_name
        )

        payload_mapping = collection_manager.get_payload_mapping(collection_name)

        try:

            with self.shared_object.data_manager.load(
                args["points_list"]
            ) as points_list:
                meta_lut = {}

                for i, point in points_list:
                    with point as point:

                        data_dict = {}
                        scalar_dict = {}
                        for name, data in point:
                            with data as data:
                                if data.type in ("BoolData", "FloatData", "IntData"):
                                    data_dict.update({name: data.to_proto()})
                                if data.type in ("TextData"):
                                    data_dict.update({name: data.to_proto()})
                                if data.type in ("ImageData"):
                                    data_dict.update({name: data.to_proto()})

                                if hasattr(data, "to_scalar"):
                                    scalar_dict.update({name: data.to_scalar()})

            # extrect payload fields

            meta_dict = {}
            for field in payload_mapping.fields:
                for name, data in scalar_dict.items():

                    if fnmatch(name, field):
                        meta_dict[name] = data

            # map (name, data) list to the (index, plugin)
            data_plugin_mapping = []
            for indexing_plugin_mapping in indexing_plugin_mappings:
                for field in indexing_plugin_mapping.fields:
                    for name, data in data_dict.items():
                        if fnmatch(name, field):
                            data_plugin_mapping.append(
                                (indexing_plugin_mapping, name, data)
                            )

            feature_dict = {}
            for data_plugin in data_plugin_mapping:
                data = data_plugin[2]
                index_name = data_plugin[0].index_name
                feature_dict.setdefault(index_name, [])

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
                feature_dict[index_name].append(feature_vecs)

            print(
                {
                    "id": point.id,
                    "meta": meta_dict,
                    "features": feature_dict,
                },
                flush=True,
            )

            collection_manager.add_points(
                collection_name="default",
                points=[
                    {
                        "id": point.id,
                        "meta": meta_dict,
                        "features": feature_dict,
                    }
                ],
            )
            #                 print(data, flush=True)
            #                 print(data.type, flush=True)
            #             # data_dict.update()
            #         print(data_dict, flush=True)
            #         clip_text_feature_vecs = []
            #         logging.error(x)

            #         for y in x.meta.get("meta", []):
            #             if y["name"] in [
            #                 "title",
            #                 "artist_name",
            #                 "title",
            #                 "object_type",
            #                 "location",
            #                 "medium",
            #                 "genre",
            #             ]:
            #                 request = cls.build_string_plugin_data(y["value_str"])

            #                 results = cls.inference_server(
            #                     cls.compute_manager,
            #                     "ClipTextEmbeddingFeature",
            #                     request,
            #                 )

            #                 feature_vec = list(
            #                     results.results[0].result.feature.feature
            #                 )
            #                 meta_dict.update({y["name"]: y["value_str"]})
            #                 clip_text_feature_vecs.append(feature_vec)

            #             if y["name"] == "license":
            #                 meta_dict.update({"license": y["value_str"]})

            #         meta_lut[x.ref_id] = {
            #             "clip_text": clip_text_feature_vecs,
            #             "meta": meta_dict,
            #         }

            # for x in objects:
            #     with x as x:
            #         clip_image_feature_vecs = []
            #         meta_lut[x.id]

            #         request = cls.build_image_plugin_data(objects.load_raw(x))
            #         results = cls.inference_server(
            #             cls.compute_manager, "ClipImageEmbeddingFeature", request
            #         )
            #         feature_vec = list(results.results[0].result.feature.feature)
            #         clip_image_feature_vecs.append(feature_vec)

            #         cls.indexer_manager.add_points(
            #             collection_name="default",
            #             points=[
            #                 {
            #                     "id": x.id,
            #                     "meta": meta_lut[x.id]["meta"],
            #                     "features": {
            #                         "clip_text": meta_lut[x.id]["clip_text"],
            #                         "clip_image": clip_image_feature_vecs,
            #                     },
            #                 }
            #             ],
            #         )

            return
        except Exception as e:

            # raise e
            logging.error(f"[Analyser] {e}")
            exc_type, exc_value, exc_traceback = sys.exc_info()

            traceback.print_exception(
                exc_type,
                exc_value,
                exc_traceback,
                limit=2,
                file=sys.stdout,
            )
            print("Hello, World!", flush=True)
