from src.enums.side import SideEnum
from src.enums.symbol import SymbolEnum
from src.models.rounds import Round
from src.models.transactions import Transaction
from src.services.repository import RepositoryService
from src.utils.singleton import Singleton


class TransactionsService(metaclass=Singleton):
    def __init__(self):
        self.repository = RepositoryService()

    def get_transactions(self, symbol: SymbolEnum, round_id) -> list[Transaction]:
        return self.repository.select_transactions(symbol, round_id)

    def get_last_transaction(self, symbol: SymbolEnum, round_id) -> Transaction | None:
        transactions = self.get_transactions(symbol, round_id)

        if not transactions:
            return None

        return max(transactions, key=lambda t: t.id)

    def new_transaction(self, side: SideEnum, current_round: Round, transaction_data: dict):
        if not transaction_data:
            return

        symbol = SymbolEnum(transaction_data['symbol'])
        transactions = self.get_transactions(symbol, current_round.id)
        max_id = max((t.id for t in transactions), default=0)

        transaction_data['id'] = max_id + 1
        transaction_data['round_id'] = current_round.id
        transaction_data['side'] = side.value

        transaction_data['price'] = transaction_data['fills'][0]['price']
        transaction_data['commission'] = transaction_data['fills'][0]['commission']
        transaction_data['commissionAsset'] = transaction_data['fills'][0]['commissionAsset']

        transaction = Transaction(**transaction_data)
        self.repository.insert_transaction(transaction)