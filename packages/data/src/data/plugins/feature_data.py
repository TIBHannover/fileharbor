import logging
from typing import List
from dataclasses import dataclass, field

import numpy.typing as npt
import numpy as np

from ..manager import DataManager
from ..data import Data
from interface import data_pb2


@dataclass(kw_only=True)
class PluginInfo:
    name: str
    version: str = field(default="1.0")

    def to_dict(self) -> dict:
        meta = super().to_dict()
        return {
            **meta,
            "name": self.name,
            "version": self.version,
        }

    def to_save(self) -> dict:
        meta = super().to_dict()
        return {
            **meta,
            "name": self.name,
            "version": self.version,
        }


@DataManager.export("Feature", data_pb2.FEATURE_DATA)
@dataclass(kw_only=True)
class FeatureData(Data):
    plugin: PluginInfo = None
    feature_type: str = None
    ref_id: str = None
    time: float = None
    delta_time: float = None
    embedding: npt.NDArray = None
    shape: list[int] = None

    def load(self) -> None:
        super().load()
        assert self.check_fs(), "No filesystem handler installed"

        data = self.load_dict("feature.yml")
        self.features = [FeatureData(**x) for x in data.get("features")]

        with self.fs.open_file("features.npz", "r") as f:
            features = np.load(f)
        if len(self.features) != features.shape[0]:
            logging.error(
                f"Data has invalid shape {len(self.features)} vs. {features.shape[0]}"
            )
            return

        for i in range(features.shape[0]):
            self.features[i].embedding = features[i]

    def save(self) -> None:
        super().save()
        assert self.check_fs(), "No filesystem handler installed"
        assert self.fs.mode == "w", "Data packet is open read only"

        self.save_dict(
            "feature.yml",
            {"features": [x.to_save() for x in self.features]},
        )

        with self.fs.open_file("features.npz", "w") as f:
            np.save(f, np.stack([x.embedding for x in self.features], axis=0))

    def to_dict(self) -> dict:
        meta = super().to_dict()
        return {
            **meta,
            "ref_id": self.ref_id,
            "time": self.time,
            "delta_time": self.delta_time,
            "embedding": self.embedding.tolist(),
        }

    def to_save(self) -> dict:
        meta = super().to_dict()
        return {
            **meta,
            "ref_id": self.ref_id,
            "time": self.time,
            "delta_time": self.delta_time,
        }

    def to_proto(self) -> data_pb2.Data:
        return data_pb2.Data(
            id=self.id, text=data_pb2.TextData(text=self.text, language=self.language)
        )


@DataManager.export("Features", data_pb2.FEATURES_DATA)
@dataclass(kw_only=True)
class FeaturesData(Data):
    type: str = field(default="Features")
    features: List[FeatureData] = field(default_factory=list)

    def load(self) -> None:
        super().load()
        assert self.check_fs(), "No filesystem handler installed"

        data = self.load_dict("features.yml")
        self.features = [FeatureData(**x) for x in data.get("features")]

        with self.fs.open_file("features.npz", "r") as f:
            features = np.load(f)
        if len(self.features) != features.shape[0]:
            logging.error(
                f"Data has invalid shape {len(self.features)} vs. {features.shape[0]}"
            )
            return

        for i in range(features.shape[0]):
            self.features[i].embedding = features[i]

    def save(self) -> None:
        super().save()
        assert self.check_fs(), "No filesystem handler installed"
        assert self.fs.mode == "w", "Data packet is open read only"

        self.save_dict(
            "features.yml",
            {"features": [x.to_save() for x in self.features]},
        )

        with self.fs.open_file("features.npz", "w") as f:
            np.save(f, np.stack([x.embedding for x in self.features], axis=0))

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "features": [x.to_dict() for x in self.features],
        }

    def to_proto(self) -> data_pb2.Data:
        return data_pb2.Data(
            id=self.id, text=data_pb2.TextData(text=self.text, language=self.language)
        )
