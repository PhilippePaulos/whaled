import yaml

from model.common.singleton import Singleton


class Config(metaclass=Singleton):
    logging_level = 'INFO'
    logging_file = None
    check_interval = 30
    output_format = 'csv'
    output_path = None
    token_adress = None
    es_host = 'localhost'
    es_port = 9200
    blockchain = None

    def __init__(self, settings_path=None):
        if settings_path is not None:
            self.load_settings(settings_path)

    def load_settings(self, settings_path):
        with open(settings_path, "r") as stream:
            try:
                config_data = yaml.safe_load(stream)
                for module in config_data:
                    if type(config_data[module]) is dict:
                        for key, value in config_data[module].items():
                            setattr(self, f'{module}_{key}', config_data[module][key])
                    else:
                        setattr(self, f'{module}', config_data[module])
            except yaml.YAMLError as exc:
                print(f"Coundn't not parse yaml config from {settings_path}'")
                raise exc
