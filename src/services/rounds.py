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

        for r in _rounds:
            r.transactions = self.repository.select_transactions(r.symbol, r.id)

            if not r.transactions:
                continue

            r.last_transaction_datetime = r.transactions[-1].transaction_time

            _amount_sum = sum([t.total for t in r.transactions if t.side == SideEnum.BUY.value])
            _qty_sum = sum([t.qty for t in r.transactions if t.side == SideEnum.BUY.value])
            r.total_qty = _qty_sum
            r.total_amount = _amount_sum
            r.avg_price = _amount_sum / _qty_sum

            target_percentage = self.binance.settings[r.symbol]['target_percentage']
            r.target_price = r.avg_price * (1 - (target_percentage/100))

            take_profit_percentage = self.binance.settings[r.symbol]['take_profit_percentage']
            r.take_profit_price = r.avg_price * (1 + (take_profit_percentage/100))
            r.last_price = self.binance.symbols[r.symbol]

            # Regra do Trailing Stop
            trailing_stop_percentage = self.binance.settings[r.symbol]['trailing_stop_percentage']
            if r.last_price >= r.take_profit_price or r.trailing_stop_price:
                trailing_stop_price = r.last_price * (1 - (trailing_stop_percentage/100))

                if trailing_stop_price > r.trailing_stop_price:
                    r.trailing_stop_price = trailing_stop_price

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
        rounds = self.get_rounds(symbol)
        max_id = max((r.id for r in rounds), default=0)
        new_round = Round(id=max_id + 1, symbol=symbol)
        self.repository.insert_round(new_round)
        return new_round

    def close_round(self, current_round):
        _round = self.get_round(current_round.symbol, current_round.id)

        _buy_amount = sum([t.amount for t in _round.transactions if t.side == SideEnum.BUY.value])
        _sell_amount = sum([t.amount for t in _round.transactions if t.side == SideEnum.SELL.value])

        _round.result = _sell_amount - _buy_amount
