from src.enums.symbol import SymbolEnum


class Transaction:
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.round_id = kwargs['round_id']
        self.date_time = kwargs['date_time']
        self.side = kwargs['side']
        self.symbol = SymbolEnum(kwargs['symbol'])
        self.price = kwargs['price']
        self.qty = kwargs['qty']
        self.amount = kwargs['amount']
        self.commission = kwargs['commission']
        self.commission_type = SymbolEnum(kwargs['commission_type'])
        self.total = kwargs['total']
