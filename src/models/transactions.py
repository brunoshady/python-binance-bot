from datetime import datetime

from src.enums.symbol import SymbolEnum


class Transaction:
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.round_id = kwargs['round_id']
        self.side = kwargs['side']

        self.symbol = SymbolEnum(kwargs['symbol'])
        self.order_id = kwargs['orderId']
        self.transaction_time = datetime.fromtimestamp(kwargs['transactTime'] / 1000)

        self.order_qty = float(kwargs['executedQty'])
        self.order_amount = float(kwargs['cummulativeQuoteQty'])


        self.price = float(kwargs['price'])
        self.commission = float(kwargs['commission'])
        self.commision_symbol = kwargs['commissionAsset']

        if self.side == 'BUY':
            self.qty = self.order_qty - self.commission

        if self.side == 'SELL':
            self.qty = self.order_qty

        self.total = self.order_amount