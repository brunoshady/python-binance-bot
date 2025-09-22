from datetime import datetime

from src.enums.side import SideEnum
from src.enums.symbol import SymbolEnum
from src.models.rounds import Round
from src.models.transactions import Transaction
from src.services.repository import RepositoryService
from src.utils.singleton import Singleton


class TransactionsService(metaclass=Singleton):
    def __init__(self):
        self.repository = RepositoryService()

    def get_last_transaction(self, symbol: SymbolEnum, round_id) -> Transaction | None:
        _round = self.repository.select_round(symbol, round_id)

        if not _round.transactions:
            return None

        return max(_round.transactions, key=lambda t: t.id)

    def new_transaction(self, side: SideEnum, current_round: Round, transaction_data: dict):
        if not transaction_data:
            return None

        current_round = self.repository.select_round(current_round.symbol, current_round.id)
        max_id = max((t.id for t in current_round.transactions), default=0)

        new_transaction = Transaction(
            id=max_id + 1,
            round_id=current_round.id,
            side=side.value,
            symbol=current_round.symbol,
            order_id=transaction_data['orderId'],
            transaction_time=datetime.fromtimestamp(transaction_data['transactTime'] / 1000),
            order_qty=float(transaction_data['executedQty']),
            order_amount=float(transaction_data['cummulativeQuoteQty']),
            price=float(transaction_data['fills'][0]['price']),
            commission=float(transaction_data['fills'][0]['commission']),
            commision_symbol=transaction_data['fills'][0]['commissionAsset'],
            # qty=float(transaction_data['executedQty']) - (float(transaction_data['fills'][0]['commission']) if side == SideEnum.BUY else 0),
            total=float(transaction_data['cummulativeQuoteQty'])
        )

        if side == SideEnum.BUY:
            new_transaction.qty = new_transaction.order_qty - new_transaction.commission

        if side == SideEnum.SELL:
            new_transaction.qty = new_transaction.order_qty

        return self.repository.update_round(current_round, new_transaction)