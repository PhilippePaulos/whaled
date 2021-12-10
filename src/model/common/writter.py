import typing
from elasticsearch import Elasticsearch
from abc import ABC

from model.common.utils import export_objects_to_csv, prepend_objects_to_csv


class OutputWritter(ABC):

    @staticmethod
    def save_csv(path: str, objects: typing.List[object], prepend=False):
        if prepend:
            prepend_objects_to_csv(path, objects)
        else:
            export_objects_to_csv(path, objects)

    def save_es(self, index: str, objects: typing.List[object]):
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

