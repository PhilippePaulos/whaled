import logging
import typing
from elasticsearch import Elasticsearch
from abc import ABC
import simplejson as json
from model.common.utils import export_objects_to_csv, prepend_objects_to_csv


class OutputWritter(ABC):

    @staticmethod
    def save_csv(path: str, objects: typing.List[object], prepend=False):
        if prepend:
            prepend_objects_to_csv(path, objects)
        else:
            export_objects_to_csv(path, objects)

    @staticmethod
    def save_es(index: str, objects: typing.List[object], es_host: str, es_port: int):
        es = Elasticsearch([{'host': es_host, 'port': es_port}])
        if not es.indices.exists(index=index.lower()):
            logging.debug(f'Creating index {index.lower()}')
            es.indices.create(index=index.lower())
        for instance in objects:
            object_dict = instance.__dict__
            es.index(index=index.lower(), body=json.dumps(object_dict, use_decimal=True))
