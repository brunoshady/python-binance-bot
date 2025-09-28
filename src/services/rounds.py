from datetime import datetime

from src.enums.side import SideEnum
from src.enums.symbol import SymbolEnum
from src.models.rounds import Round
from src.models.transactions import Transaction
from src.repository.round import RoundRepository
from src.services.binance import BinanceService
from src.settings import SETTINGS


class RoundsService:
    def __init__(self):
        self.binance = BinanceService()
        self.repository = RoundRepository()

    def get_current_round(self, symbol: SymbolEnum) -> Round | None:
        return self.repository.select_current_by_symbol(symbol)

    def get_or_create_current_round(self, symbol: SymbolEnum) -> Round:
        current_round = self.repository.select_current_by_symbol(symbol)

        if not current_round:
            current_round =  self.repository.create_by_symbol(symbol)

        return current_round

    def get_round(self, symbol: SymbolEnum, round_id: int) -> Round:
        return self.repository.select_by_id(symbol, round_id)

    def get_rounds(self, symbol: SymbolEnum) -> list[Round]:
        return self.repository.select_all_by_symbol(symbol)

    def update_values(self, current_round: Round):
        current_round.last_price = self.binance.symbols.get(current_round.symbol) or 0
        sell_total = sum([transaction.total for transaction in current_round.transactions if transaction.side == SideEnum.SELL.value])

        if sell_total:
            current_round.last_price = [transaction for transaction in current_round.transactions if transaction.side == SideEnum.SELL.value][-1].price

        current_round.total_qty = sum(transaction.qty for transaction in current_round.transactions if transaction.side == SideEnum.BUY.value)
        current_round.total_amount = sum(transaction.total for transaction in current_round.transactions if transaction.side == SideEnum.BUY.value)
        current_round.avg_price = current_round.total_amount / current_round.total_qty if current_round.total_qty else None

        target_percentage = SETTINGS[current_round.symbol]['target_percentage']
        current_round.target_price = current_round.avg_price * (1 - (target_percentage / 100)) if current_round.avg_price else None

        take_profit_percentage = SETTINGS[current_round.symbol]['take_profit_percentage']
        current_round.take_profit_price = current_round.avg_price * (1 + (take_profit_percentage / 100)) if current_round.avg_price else None

        current_round.last_transaction_datetime = max((transaction.transaction_time for transaction in current_round.transactions), default=None)

        trailing_stop_percentage = SETTINGS[current_round.symbol]['trailing_stop_percentage']
        if current_round.trailing_stop_price or (current_round.take_profit_price and current_round.last_price >= current_round.take_profit_price):
            trailing_stop_price = current_round.last_price * (1 - (trailing_stop_percentage / 100))

            if current_round.trailing_stop_price is None:
                current_round.trailing_stop_price = 0

            if trailing_stop_price > current_round.trailing_stop_price:
                current_round.trailing_stop_price = trailing_stop_price

                if current_round.result:
                    return

                self.repository.update(current_round)

    def add_transaction(self, current_round: Round, side: SideEnum, response: dict) -> Round:
        next_round_id = current_round.transactions[-1].id + 1 if current_round.transactions else 1

        new_transaction = Transaction(
            id=next_round_id,
            round_id=current_round.id,
            side=side.value,
            symbol=current_round.symbol,
            order_id=response['orderId'],
            transaction_time=datetime.fromtimestamp(response['transactTime'] / 1000),
            order_qty=float(response['executedQty']),
            order_amount=float(response['cummulativeQuoteQty']),
            price=float(response['fills'][0]['price']),
            commission=float(response['fills'][0]['commission']),
            commision_symbol=response['fills'][0]['commissionAsset'],
            total=float(response['cummulativeQuoteQty'])
        )

        if side == SideEnum.BUY:
            new_transaction.qty = new_transaction.order_qty - new_transaction.commission

        if side == SideEnum.SELL:
            new_transaction.qty = new_transaction.order_qty

        current_round.transactions.append(new_transaction)
        return self.repository.update(current_round)

    def close_round(self, current_round: Round):
        buy_total = sum([transaction.total for transaction in current_round.transactions if transaction.side == SideEnum.BUY.value])
        sell_total = sum([transaction.total for transaction in current_round.transactions if transaction.side == SideEnum.SELL.value])

        current_round.result = sell_total - buy_total
        self.repository.update(current_round)
