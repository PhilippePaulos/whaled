from model.common.config import Config


class TradesConfig(Config):
    history = False
    output_path = 'trades.csv'
    filter_num_tokens = 0
    disable_price_check = False

    def __init__(self, settings_path=None):
        super().__init__(settings_path)
