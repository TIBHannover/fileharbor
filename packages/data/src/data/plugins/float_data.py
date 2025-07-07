import logging
from typing import List
from dataclasses import dataclass, field

import numpy.typing as npt
import numpy as np

from ..manager import DataManager
from ..data import Data
from interface import data_pb2


@DataManager.export("FloatData", data_pb2.FLOAT_DATA)
@dataclass(kw_only=True)
class FloatData(Data):
    type: str = field(default="FloatData")
    value: float = None

    def load(self) -> None:
        super().load()
        assert self.check_fs(), "No filesystem handler installed"

        data = self.load_dict("float_data.yml")
        self.value = data.get("value")

    def save(self) -> None:
        super().save()
        assert self.check_fs(), "No filesystem handler installed"
        assert self.fs.mode == "w", "Data packet is open read only"

        self.save_dict(
            "float_data.yml",
            {
                "value": self.value,
            },
        )

    def to_dict(self) -> dict:
        return {"value": self.value}

    def to_proto(self) -> data_pb2.Data:
        return data_pb2.Data(id=self.id, float=data_pb2.FloatData(value=self.value))

    def to_scalar(self) -> float:
        return self.value

    def to_string(self) -> str:
        return str(self.value)
