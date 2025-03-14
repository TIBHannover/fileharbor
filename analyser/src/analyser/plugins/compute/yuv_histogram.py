import math
import uuid

import numpy as np

from interface import analyser_pb2
from analyser.plugins import ComputePlugin, ComputePluginManager, ComputePluginResult
from analyser.utils import image_from_proto, image_resize

import time


# @ComputePluginManager.export("YUVHistogramFeature")
class YUVHistogramFeature(ComputePlugin):
    default_config = {
        "host": "localhost",
        "port": 6379,
        "model_name": "yuv_histogram",
        "model_file": "/home/matthias/yuv_histogram.pt",
        "max_dim": 244,
        "min_dim": 244,
        "max_tries": 5,
    }

    default_version = "0.1"

    def __init__(self, **kwargs):
        super(YUVHistogramFeature, self).__init__(**kwargs)
        self.host = self.config["host"]
        self.port = self.config["port"]
        self.model_name = self.config["model_name"]
        self.model_file = self.config["model_file"]

        self.max_dim = self.config["max_dim"]
        self.min_dim = self.config["min_dim"]

        # self.max_tries = self.config["max_tries"]

        # try_count = self.max_tries
        # while try_count > 0:
        #     try:
        #         self.con = rai.Client(host=self.host, port=self.port)

        #         if not self.check_rai():
        #             self.register_rai()
        #         return
        #     except:
        #         try_count -= 1
        #         time.sleep(4)

    def register_rai(self):
        model = ml2rt.load_model(self.model_file)

        self.con.modelset(
            self.model_name,
            backend="torch",
            device="cpu",
            data=model,
        )

    def check_rai(self):
        result = self.con.modelscan()
        if self.model_name in [x[0] for x in result]:
            return True
        return False

    def call(self, entries):
        result_entries = []
        result_annotations = []
        for entry in entries:
            entry_annotation = []
            # image = image_from_proto(entry)
            image = entry
            image = image_resize(image, max_dim=self.max_dim)
            image = image.astype(np.float32)

            job_id = uuid.uuid4().hex

            self.con.tensorset(f"image_{job_id}", image)
            result = self.con.modelrun(
                self.model_name, f"image_{job_id}", f"output_{job_id}"
            )
            output = self.con.tensorget(f"output_{job_id}")
            uv_histogram_norm_bin = "".join(
                [str(int(x > 0)) for x in (output / np.mean(output)).tolist()]
            )

            self.con.delete(f"image_{job_id}")
            self.con.delete(f"output_{job_id}")

            # hash_splits_list = []
            # for x in range(math.ceil(len(uv_histogram_norm_bin) / 16)):
            #     # print(uv_histogram_norm_bin[x * 16:(x + 1) * 16])
            #     hash_splits_list.append(uv_histogram_norm_bin[x * 16 : (x + 1) * 16])

            # TODO split yuv and lab color.rgb2lab
            entry_annotation.append(
                analyser_pb2.ComputePluginResult(
                    plugin=self.name,
                    type=self._type,
                    version=str(self._version),
                    feature=analyser_pb2.FeatureResult(
                        type="color",
                        binary=uv_histogram_norm_bin,
                        feature=output.tolist(),
                    ),
                )
            )

            result_annotations.append(entry_annotation)
            result_entries.append(entry)

        return ComputePluginResult(self, result_entries, result_annotations)
