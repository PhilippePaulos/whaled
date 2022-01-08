import logging
import typing
from abc import ABC

import simplejson
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from model.common.utils import export_objects_to_csv, prepend_objects_to_csv, es_generate_bulk_data


class OutputWritter(ABC):

    @staticmethod
    def save_csv(path: str, objects: typing.List[object], prepend=False):
        if prepend:
            prepend_objects_to_csv(path, objects)
        else:
            export_objects_to_csv(path, objects)

    @staticmethod
    def save_list_es(index: str, objects: typing.List[object], es_host: str, es_port: int, id_field=None):
        if len(objects) > 0:
            index = index.lower()
            es = Elasticsearch([{'host': es_host, 'port': es_port}])
            if not es.indices.exists(index=index):
                logging.debug(f'Creating index {index}')
                es.indices.create(index=index)
            logging.debug(f'Insert data into index: {index}')
            bulk(es, es_generate_bulk_data(index, objects, id_field=id_field))
        else:
            logging.info('There is no data to save')

    @staticmethod
    def save_raw_es(index: str, raw: object, es_host: str, es_port: int, id=None):
        index = index.lower()
        es = Elasticsearch([{'host': es_host, 'port': es_port}])
        if not es.indices.exists(index=index):
            logging.debug(f'Creating index {index}')
            es.indices.create(index=index)
        logging.debug(f'Insert data into index: {index}')
        data = simplejson.dumps(raw.__dict__, use_decimal=True, default=str)
        if id is not None:
            es.index(index=index, body=data, id=id)
        else:
            es.index(index=index, body=data, id=id)

