

class Round:
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.symbol = kwargs['symbol']
        self.result = None
        self.avg_price = None
        self.target_price = None
        self.take_profit_price = None
        self.trailing_stop_price = 0
        self.last_price = None
        self.last_transaction_datetime = None
        self.total_qty = None
        self.total_amount = None
        self.transactions = []