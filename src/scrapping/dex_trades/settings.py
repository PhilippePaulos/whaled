# Default values (overrided by trades.yaml)
# Logging
import sys

import yaml

logging_level = 'INFO'
logging_file = None

# trades_scrapper
token_adress = None
blockchain = 'bsc'

output_format = 'csv'
output_path = 'trades.csv'
history = False
check_interval = 30


def load_settings(settings_path):
    with open(settings_path, "r") as stream:
        try:
            config_data = yaml.safe_load(stream)
            for module in config_data:
                if type(config_data[module]) is dict:
                    for key, value in config_data[module].items():
                        setattr(sys.modules[__name__], f'{module}_{key}', config_data[module][key])
                else:
                    setattr(sys.modules[__name__], f'{module}', config_data[module])
        except yaml.YAMLError as exc:
            print(exc)
