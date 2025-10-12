import logging
from typing import List
from dataclasses import dataclass, field

import numpy.typing as npt
import numpy as np

from ..manager import DataManager
from ..data import Data
from interface import data_pb2


@DataManager.export("GeoData", data_pb2.GEO_DATA)
@dataclass(kw_only=True)
class GeoData(Data):
    type: str = field(default="GeoData")
    lat: float = None
    lon: float = None

    def load(self) -> None:
        super().load()
        assert self.check_fs(), "No filesystem handler installed"

        data = self.load_dict("geo_data.yml")
        self.lat = data.get("lat")
        self.lon = data.get("lon")

    def save(self) -> None:
        super().save()
        assert self.check_fs(), "No filesystem handler installed"
        assert self.fs.mode == "w", "Data packet is open read only"

        self.save_dict(
            "geo_data.yml",
            {
                "lat": self.lat,
                "lon": self.lon,
            },
        )

    def to_dict(self) -> dict:
        return {
            "lat": self.lat,
            "lon": self.lon,
        }

    def to_proto(self) -> data_pb2.Data:
        return data_pb2.Data(
            id=self.id, geo=data_pb2.GeoData(lat=self.lat, lon=self.lon)
        )

    def to_string(self) -> str:
        return str(self.lat) + ":" + str(self.lon)
