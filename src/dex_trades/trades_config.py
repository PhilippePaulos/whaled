from model.common.config import Config


class TradesConfig(Config):
    history = False
    filter_num_tokens = 0

    def __init__(self, settings_path=None):
        super().__init__(settings_path)
