import os
import sys

import yaml

from definitions import ROOT_DIR

# Default values (overrided by config.yaml)
# Logging
logging_level = 'INFO'
logging_file = None

# trades_scrapper
trades_token_adress = None
trades_blockchain = 'bsc'


def load_settings():
    with open(os.path.join(ROOT_DIR, "resources/config.yaml"), "r") as stream:
        try:
            config_data = yaml.safe_load(stream)
            for module in config_data:
                for key, value in config_data[module].items():
                    setattr(sys.modules[__name__], f'{module}_{key}', config_data[module][key])
        except yaml.YAMLError as exc:
            print(exc)
