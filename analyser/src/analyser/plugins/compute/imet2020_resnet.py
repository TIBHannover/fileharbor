import re
import uuid

import numpy as np
import csv

from analyser.plugins import ComputePlugin, ComputePluginManager, ComputePluginResult
from analyser.utils import image_from_proto, image_resize
from interface import analyser_pb2


# @ComputePluginManager.export("IMet2020ResnetClassifier")
class IMet2020ResnetClassifier(ComputePlugin):
    default_config = {
        "host": "localhost",
        "port": 6379,
        "model_name": "imet2020_resnet",
        "model_device": "gpu",
        "model_file": "/nfs/data/iart/models/web/imet2020_resnet/imet2020_resnet.pt",
        "mapping_file": "/nfs/data/iart/models/web/imet2020_resnet/imagenet_mapping.json",
        "remove_prefix": True,
        "multicrop": True,
        "max_dim": None,
        "min_dim": 244,
        "threshold": 0.25,
    }

    default_version = "0.1"

    def __init__(self, **kwargs):
        super(IMet2020ResnetClassifier, self).__init__(**kwargs)
        self.host = self.config["host"]
        self.port = self.config["port"]
        self.model_name = self.config["model_name"]
        self.model_device = self.config["model_device"]
        self.model_file = self.config["model_file"]
        self.mapping_file = self.config["mapping_file"]
        self.remove_prefix = self.config["remove_prefix"]
        self.multicrop = self.config["multicrop"]
        self.max_dim = self.config["max_dim"]
        self.min_dim = self.config["min_dim"]
        self.threshold = self.config["threshold"]

        self.concept_lookup = []

        with open(self.mapping_file, "r") as f:
            spamreader = csv.reader(f)
            next(spamreader)
            for row in spamreader:
                self.concept_lookup.append(row[1])

        if self.remove_prefix:
            self.concept_lookup_filter = []

            for x in self.concept_lookup:
                m = re.match(r"^(.+?)::(.+?)$", x)
                if m:
                    self.concept_lookup_filter.append(m.group(2))
                else:
                    self.concept_lookup_filter.append(x)
            self.concept_lookup = self.concept_lookup_filter
        self.con = rai.Client(host=self.host, port=self.port)

        if not self.check_rai():
            self.register_rai()

    def register_rai(self):
        model = ml2rt.load_model(self.model_file)

        self.con.modelset(
            self.model_name,
            backend="torch",
            device=self.model_device,
            data=model,
            batch=16,
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
            image = image_resize(image, max_dim=self.max_dim, min_dim=self.min_dim)
            # image = np.expand_dims(image, 0)

            job_id = uuid.uuid4().hex

            self.con.tensorset(f"image_{job_id}", image)
            result = self.con.modelrun(
                self.model_name, f"image_{job_id}", f"probabilities_{job_id}"
            )

            probabilities = self.con.tensorget(f"probabilities_{job_id}")

            concepts = []

            result_list = np.argwhere(probabilities[0] > self.threshold)
            for x in result_list:
                index = x[0]
                prob = probabilities[0, index]
                name = self.concept_lookup[index]
                concepts.append(
                    analyser_pb2.Concept(concept=name, type="concept", prob=prob)
                )

            self.con.delete(f"image_{job_id}")
            self.con.delete(f"probabilities_{job_id}")

            entry_annotation.append(
                analyser_pb2.ComputePluginResult(
                    plugin=self.name,
                    type=self._type,
                    version=str(self._version),
                    classifier=analyser_pb2.ClassifierResult(concepts=concepts),
                )
            )

            result_annotations.append(entry_annotation)
            result_entries.append(entry)

        return ComputePluginResult(self, result_entries, result_annotations)
