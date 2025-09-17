from src.enums.symbol import SymbolEnum
from src.models.rounds import Round
from src.models.transactions import Transaction
from src.utils.singleton import Singleton


class RepositoryService(metaclass=Singleton):
    def __init__(self):
        self.rounds = []
        self.transactions = []

    def insert_round(self, _round: Round):
        self.rounds.append(_round)

    def select_rounds(self, symbol: SymbolEnum | None) -> list[Round]:
        rounds = self.rounds

        if symbol:
            rounds = [r for r in rounds if r.symbol == symbol]

        for _round in rounds:
            _round.transactions = [t for t in self.transactions if t.round_id == _round.id]

        return rounds

    def insert_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def select_transaction(self, symbol: SymbolEnum, _id: int) -> Transaction | None:
        return next((t for t in self.transactions if t.id == _id and t.symbol == symbol), None)

    def select_transactions(self, symbol: SymbolEnum, round_id: int) -> list[Transaction]:
        return [t for t in self.transactions if t.round_id == round_id and t.symbol == symbol]
