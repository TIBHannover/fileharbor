import uuid

import numpy as np

import pickle
import logging

from interface import analyser_pb2
from analyser.plugins import ComputePlugin, ComputePluginManager, ComputePluginResult
from analyser.utils import image_from_proto, image_resize, image_crop

import time


# @ComputePluginManager.export("ImageNetInceptionFeature")
class ImageNetInceptionFeature(ComputePlugin):
    default_config = {
        "host": "localhost",
        "port": 6379,
        "model_name": "imagenet_inception",
        "model_device": "gpu",
        "model_file": "/nfs/data/iart/models/web/imagenet_inception/imagenet_inception.pb",
        "pca_model_name": "imagenet_inception_pca_128",
        "pca_model_file": "/nfs/data/iart/models/web/imagenet_inception/PCA_PARAMS.pkl",
        "multicrop": True,
        "max_dim": None,
        "min_dim": 224,
        "max_tries": 5,
    }

    default_version = "1.1"

    def __init__(self, **kwargs):
        super(ImageNetInceptionFeature, self).__init__(**kwargs)
        self.host = self.config["host"]
        self.port = self.config["port"]

        self.model_name = self.config["model_name"]
        self.model_device = self.config["model_device"]
        self.model_file = self.config["model_file"]

        self.pca_model_name = self.config["pca_model_name"]
        self.pca_model_file = self.config["pca_model_file"]

        self.max_dim = self.config["max_dim"]
        self.min_dim = self.config["min_dim"]

        logging.info(f"Loading pca files {self.pca_model_file}")
        with open(self.pca_model_file, "rb") as f:
            self.pca_params = pickle.load(f)

        self.max_tries = self.config["max_tries"]

        try_count = self.max_tries
        while try_count > 0:
            try:
                self.con = rai.Client(host=self.host, port=self.port)

                if not self.check_rai():
                    self.register_rai()
                return
            except:
                try_count -= 1
                time.sleep(4)

    def register_rai(self):
        model = ml2rt.load_model(self.model_file)

        self.con.modelset(
            self.model_name,
            backend="torch",
            device=self.model_device,
            data=model,
            batch=16,
        )

        model = ml2rt.load_model(self.pca_model_file)

        # self.con.modelset(
        #     self.pca_model_name,
        #     backend="onnx",
        #     device="cpu",
        #     data=model,
        # )

    def check_rai(self):
        result = self.con.modelscan()

        if self.model_name not in [x[0] for x in result]:
            return False

        # if self.pca_model_name not in [x[0] for x in result]:
        #     return False

        return True

    def call(self, entries):
        result_entries = []
        result_annotations = []
        for entry in entries:
            entry_annotation = []
            # image = image_from_proto(entry)
            image = entry
            image = image_resize(image, max_dim=self.max_dim, min_dim=self.min_dim)
            # image = image_crop(image, [224, 224])

            # image = np.expand_dims(image, axis=0)  # / 256
            # image = image.astype(np.float32)

            job_id = uuid.uuid4().hex

            self.con.tensorset(f"image_{job_id}", image)
            result = self.con.modelrun(
                self.model_name, f"image_{job_id}", f"embedding_{job_id}"
            )
            embedding = self.con.tensorget(f"embedding_{job_id}")[0, ...]

            embedding = np.squeeze(embedding)

            # print(embedding.shape)
            features = embedding - self.pca_params.mean_
            reduc_dim_features = np.dot(features, self.pca_params.components_.T)
            reduc_dim_features /= np.sqrt(self.pca_params.explained_variance_)
            # print(reduc_dim_features.shape)

            # self.con.tensorset(f"embedding_{job_id}", embedding)
            # result = self.con.modelrun(self.pca_model_name, f"embedding_{job_id}", f"feature_{job_id}")
            # output = self.con.tensorget(f"feature_{job_id}")[0, ...]
            output = reduc_dim_features
            output_bin = (output > 0).astype(np.int32).tolist()
            output_bin_str = "".join([str(x) for x in output_bin])

            self.con.delete(f"image_{job_id}")
            self.con.delete(f"embedding_{job_id}")
            self.con.delete(f"feature_{job_id}")

            entry_annotation.append(
                analyser_pb2.ComputePluginResult(
                    plugin=self.name,
                    type=self._type,
                    version=str(self._version),
                    feature=analyser_pb2.FeatureResult(
                        type="imagenet_embedding",
                        binary=output_bin_str,
                        feature=output.tolist(),
                    ),
                )
            )

            result_annotations.append(entry_annotation)
            result_entries.append(entry)

        return ComputePluginResult(self, result_entries, result_annotations)
