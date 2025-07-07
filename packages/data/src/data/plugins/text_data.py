import logging
from typing import List
from dataclasses import dataclass, field

import numpy.typing as npt
import numpy as np

from ..manager import DataManager
from ..data import Data
from interface import data_pb2


@DataManager.export("TextData", data_pb2.TEXT_DATA)
@dataclass(kw_only=True)
class TextData(Data):
    type: str = field(default="TextData")
    text: str = None
    language: str = field(default="en")

    def load(self) -> None:
        super().load()
        assert self.check_fs(), "No filesystem handler installed"

        data = self.load_dict("text_data.yml")
        self.text = data.get("text")

    def save(self) -> None:
        super().save()
        assert self.check_fs(), "No filesystem handler installed"
        assert self.fs.mode == "w", "Data packet is open read only"

        self.save_dict(
            "text_data.yml",
            {
                "text": self.text,
            },
        )

    def to_dict(self) -> dict:
        return {"text": self.text}

    def to_proto(self) -> data_pb2.Data:
        return data_pb2.Data(
            id=self.id, text=data_pb2.TextData(text=self.text, language=self.language)
        )

    def to_scalar(self) -> str:
        return self.text

    def to_string(self) -> str:
        return str(self.text)
