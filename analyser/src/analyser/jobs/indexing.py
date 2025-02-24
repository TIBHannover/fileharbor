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


class IndexingJob:
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
    def build_string_plugin_data(cls, input):
        request = analyser_pb2.AnalyseRequest()
        input_field = request.inputs.add()
        input_field.name = "text"
        input_field.string.text = input
        return request

    @classmethod
    def build_image_plugin_data(cls, input):
        request = analyser_pb2.AnalyseRequest()
        input_field = request.inputs.add()
        input_field.name = "image"
        input_field.image.content = input
        return request

    @classmethod
    def __call__(cls, entry):
        # TODO customize the indexing path and plugin behind it
        logging.error(entry)

        with (
            cls.data_manager.load(entry["object_id"]) as objects,
            cls.data_manager.load(entry["meta_id"]) as meta_list,
        ):
            meta_lut = {}

            for i, x in meta_list:
                with x as x:
                    clip_text_feature_vecs = []
                    logging.error(x)

                    meta_dict = {}
                    # MetaData(id='e44cac9ec1fd4645a367f431a03c3a84', version='1.0', type='MetaData', name=None, ref_id='8285ee76f9b13a58a27a65db574871cb',
                    # meta={
                    # 'collection': {'id': '25acc1c22c7a4014b56306dc685d00a2', 'is_public': True, 'name': 'wikidata'},
                    # 'meta': [
                    # {'name': 'wikidata', 'value_str': 'Q20789843'},
                    # {'name': 'license', 'value_str': 'http://creativecommons.org/publicdomain/zero/1.0/'},
                    # {'name': 'location', 'value_str': 'Museum of Fine Arts'}, {'name': 'object_type', 'value_str': 'painting'},
                    # {'name': 'artist_name', 'value_str': 'George Fuller'},
                    # {'name': 'medium', 'value_str': 'oil paint'},
                    # {'name': 'medium', 'value_str': 'canvas'}
                    # ],
                    # 'origin': [
                    # {'name': 'name', 'value_str': 'wikidata'},
                    # {'name': 'link', 'value_str': 'http://commons.wikimedia.org/wiki/Special:FilePath/George%20Fuller%20-%20Arethusa%20-%2087.22%20-%20Museum%20of%20Fine%20Arts.jpg'},
                    # {'name': 'id', 'value_str': '0acb046e21783295980164ab49ab87f5'}
                    # ]})
                    collection = x.meta.get("collection")
                    if (
                        collection.get("id")
                        and collection.get("name")
                        and collection.get("is_public")
                    ):
                        meta_dict.update(
                            {
                                "collection_id": collection.get("id"),
                                "collection_name": collection.get("name"),
                                "collection_is_public": collection.get("is_public"),
                            }
                        )

                    for y in x.meta.get("origin", []):
                        if y["name"] == "name":
                            meta_dict.update({"origin_name": y["value_str"]})
                        if y["name"] == "id":
                            meta_dict.update({"origin_id": y["value_str"]})
                        if y["name"] == "link":
                            meta_dict.update({"origin_link": y["value_str"]})

                    for y in x.meta.get("meta", []):
                        if y["name"] in [
                            "title",
                            "artist_name",
                            "title",
                            "object_type",
                            "location",
                            "medium",
                            "genre",
                        ]:
                            request = cls.build_string_plugin_data(y["value_str"])

                            results = cls.inference_server(
                                cls.compute_manager, "ClipTextEmbeddingFeature", request
                            )

                            feature_vec = list(
                                results.results[0].result.feature.feature
                            )
                            meta_dict.update({y["name"]: y["value_str"]})
                            clip_text_feature_vecs.append(feature_vec)

                        if y["name"] == "license":
                            meta_dict.update({"license": y["value_str"]})

                    meta_lut[x.ref_id] = {
                        "clip_text": clip_text_feature_vecs,
                        "meta": meta_dict,
                    }

            for x in objects:
                with x as x:
                    clip_image_feature_vecs = []
                    meta_lut[x.id]

                    request = cls.build_image_plugin_data(objects.load_raw(x))
                    results = cls.inference_server(
                        cls.compute_manager, "ClipImageEmbeddingFeature", request
                    )
                    feature_vec = list(results.results[0].result.feature.feature)
                    clip_image_feature_vecs.append(feature_vec)

                    cls.indexer_manager.add_points(
                        collection_name="default",
                        points=[
                            {
                                "id": x.id,
                                "meta": meta_lut[x.id]["meta"],
                                "features": {
                                    "clip_text": meta_lut[x.id]["clip_text"],
                                    "clip_image": clip_image_feature_vecs,
                                },
                            }
                        ],
                    )

        return
        classifier_manager = getattr(cls, "classifier_manager")
        feature_manager = getattr(cls, "feature_manager")
        try:
            image = imageio.imread(entry["image_data"])
            image = image_normalize(image)
        except Exception as e:
            logging.error(traceback.format_exc())
            return "error", {"id": entry["id"]}
        plugins = []
        for c in entry["cache"]["classifier"]:
            plugins.append({"plugin": c["plugin"], "version": c["version"]})

        classifications = list(classifier_manager.run([image], [plugins]))[0]

        plugins = []
        for c in entry["cache"]["feature"]:
            plugins.append({"plugin": c["plugin"], "version": c["version"]})
        features = list(feature_manager.run([image], [plugins]))[0]

        doc = {
            "id": entry["id"],
            "meta": entry["meta"],
            "origin": entry["origin"],
            "collection": entry["collection"],
        }

        annotations = []
        for f in features["plugins"]:
            for anno in f._annotations:
                for result in anno:
                    plugin_annotations = []

                    binary_vec = result.feature.binary
                    feature_vec = list(result.feature.feature)

                    plugin_annotations.append(
                        {
                            "type": result.feature.type,
                            "value": feature_vec,
                        }
                    )

                    feature_result = {
                        "plugin": result.plugin,
                        "version": result.version,
                        "annotations": plugin_annotations,
                    }
                    annotations.append(feature_result)

        if len(annotations) > 0:
            doc["feature"] = annotations

        annotations = []
        for c in classifications["plugins"]:
            for anno in c._annotations:
                for result in anno:
                    plugin_annotations = []
                    for concept in result.classifier.concepts:
                        plugin_annotations.append(
                            {
                                "name": concept.concept,
                                "type": concept.type,
                                "value": concept.prob,
                            }
                        )

                    classifier_result = {
                        "plugin": result.plugin,
                        "version": result.version,
                        "annotations": plugin_annotations,
                    }
                    annotations.append(classifier_result)

        if len(annotations) > 0:
            doc["classifier"] = annotations

        # copy predictions from cache
        for exist_c in entry["cache"]["classifier"]:
            if "classifier" not in doc:
                doc["classifier"] = []

            founded = False
            for computed_c in doc["classifier"]:
                if computed_c["plugin"] == exist_c["plugin"] and version.parse(
                    str(computed_c["version"])
                ) > version.parse(str(exist_c["version"])):
                    founded = True

            if not founded:
                doc["classifier"].append(exist_c)

        for exist_f in entry["cache"]["feature"]:
            if "feature" not in doc:
                doc["feature"] = []
            if "version" in exist_f:
                exist_f_version = version.parse(str(exist_f["version"]))
            else:
                exist_f_version = version.parse("0.0.0")

            founded = False
            for computed_f in doc["feature"]:
                computed_f_version = version.parse(str(computed_f["version"]))
                if (
                    computed_f["plugin"] == exist_f["plugin"]
                    and computed_f_version >= exist_f_version
                ):
                    founded = True
            if not founded:
                exist_f = {
                    "plugin": exist_f["plugin"],
                    "version": exist_f["version"],
                    "annotations": [
                        {
                            "type": exist_f["type"],
                            "value": exist_f["value"],
                        }
                    ],
                }
                doc["feature"].append(exist_f)
        return "ok", doc
