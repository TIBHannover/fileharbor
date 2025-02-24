import logging
import yaml
from typing import List, Union
from collections.abc import Iterator, Iterable

from dataclasses import dataclass, field, fields
import imageio.v3 as iio

import numpy.typing as npt
import numpy as np

from ..manager import DataManager
from ..data import Data
from interface import data_pb2


@DataManager.export("MetaData", data_pb2.META_DATA)
@dataclass(kw_only=True)
class MetaData(Data):
    type: str = field(default="MetaData")
    meta: dict = None

    def load(self) -> None:
        super().load()
        assert self.check_fs(), "No filesystem handler installed"

        self.meta = self.load_dict("meta_data.yml")

    def save(self) -> None:
        super().save()
        assert self.check_fs(), "No filesystem handler installed"
        assert self.fs.mode == "w", "Data packet is open read only"

        self.save_dict("meta_data.yml", self.meta)

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            **self.meta,
        }
