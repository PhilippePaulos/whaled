# Default values (overrided by trades.yaml)
# Logging
import sys

import yaml

logging_level = 'INFO'
logging_file = None

# prices_scrapper
prices_token_adress = None
prices_blockchain = 'bsc'


def load_settings(settings_path):
    with open(settings_path, "r") as stream:
        try:
            config_data = yaml.safe_load(stream)
            for module in config_data:
                for key, value in config_data[module].items():
                    setattr(sys.modules[__name__], f'{module}_{key}', config_data[module][key])
        except yaml.YAMLError as exc:
            print(exc)
