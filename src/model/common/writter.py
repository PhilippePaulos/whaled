import typing
from abc import ABC

from model.common.utils import export_objects_to_csv


class OutputWritter(ABC):

    @staticmethod
    def save_csv(path: str, objects: typing.List[object]):
        export_objects_to_csv(path, objects)

    def save_es(self, index: str):
        pass
