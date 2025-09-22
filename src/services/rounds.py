from src.enums.side import SideEnum
from src.enums.symbol import SymbolEnum
from src.models.rounds import Round
from src.services.binance import BinanceService
from src.services.repository import RepositoryService
from src.utils.singleton import Singleton


class RoundsService(metaclass=Singleton):
    def __init__(self):
        self.binance = BinanceService()
        self.repository = RepositoryService()

    def get_rounds(self, symbol: SymbolEnum) -> list[Round]:
        _rounds = self.repository.select_rounds(symbol)
        return _rounds

    def get_round(self, symbol: SymbolEnum, round_id) -> Round | None:
        return next((r for r in self.get_rounds(symbol) if r.id == round_id), None)

    def get_current_round(self, symbol: SymbolEnum, create_new: bool = False) -> Round:
        rounds = self.get_rounds(symbol)
        current_round = next((r for r in rounds if r.result is None), None)

        if not current_round and create_new:
            current_round = self.new_round(symbol)

        return current_round

    def new_round(self, symbol: SymbolEnum) -> Round:
        new_round = Round(symbol=symbol.value)
        return self.repository.insert_round(new_round)

    def close_round(self, current_round):
        _round = self.get_round(current_round.symbol, current_round.id)

        _buy_amount = sum([t.total for t in _round.transactions if t.side == SideEnum.BUY.value])
        _sell_amount = sum([t.total for t in _round.transactions if t.side == SideEnum.SELL.value])

        _round.result = _sell_amount - _buy_amount
