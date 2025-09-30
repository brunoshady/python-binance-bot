from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_serializer

from src.enums.symbol import SymbolEnum
from src.schemas.transactions import Transaction


class Round(BaseModel):
    id: int
    symbol: SymbolEnum
    result: float | None
    avg_price: float | None = Field(default=None, serialization_alias="avgPrice")
    target_price: float | None = Field(default=None, serialization_alias="targetPrice")
    take_profit_price: float | None = Field(default=None, serialization_alias="takeProfitPrice")
    current_profit: float | None = Field(default=None, serialization_alias="currentProfit")
    trailing_stop_price: float | None = Field(default=None, serialization_alias="trailingStopPrice")
    last_price: float | None = Field(default=None, serialization_alias="lastPrice")
    last_transaction_datetime: datetime | None = Field(default=None, serialization_alias="lastTransactionDateTime")
    total_qty: float | None = Field(default=None, serialization_alias="totalQty")
    total_amount: float | None = Field(default=None, serialization_alias="totalAmount")

    class Config:
        validate_by_name = True
        from_attributes = True

    @field_serializer('avg_price')
    def serialize_avg_price(self, avg_price: float, _info) -> str:
        if self.symbol in (SymbolEnum.PEPEBRL, SymbolEnum.PEPEUSDT):
            return f"{avg_price:,.8f}" if avg_price else None

        return f"{avg_price:,.2f}" if avg_price else None

    @field_serializer('target_price')
    def serialize_target_price(self, target_price: float, _info) -> str:
        if self.symbol in (SymbolEnum.PEPEBRL, SymbolEnum.PEPEUSDT):
            return f"{target_price:,.8f}" if target_price else None

        return f"{target_price:,.2f}" if target_price else None

    @field_serializer('take_profit_price')
    def serialize_take_profit_price(self, take_profit_price: float, _info) -> str:
        if self.symbol in (SymbolEnum.PEPEBRL, SymbolEnum.PEPEUSDT):
            return f"{take_profit_price:,.8f}" if take_profit_price else None

        return f"{take_profit_price:,.2f}" if take_profit_price else None

    @field_serializer('current_profit')
    def serialize_current_profit(self, current_profit: float, _info) -> str:
        return f"{current_profit:,.2f}" if current_profit else None

    @field_serializer('trailing_stop_price')
    def serialize_trailing_stop_price(self, trailing_stop_price: float, _info) -> str | None:
        if not trailing_stop_price:
            return None

        if self.symbol in (SymbolEnum.PEPEBRL, SymbolEnum.PEPEUSDT):
            return f"{trailing_stop_price:,.8f}"

        return f"{trailing_stop_price:,.2f}"

    @field_serializer('last_price')
    def serialize_last_price(self, last_price: float, _info) -> str:
        if self.symbol in (SymbolEnum.PEPEBRL, SymbolEnum.PEPEUSDT):
            return f"{last_price:,.8f}" if last_price else None

        return f"{last_price:,.2f}" if last_price else None

    @field_serializer('result')
    def serialize_result(self, result: float, _info) -> str:
        return f"{result:,.2f}" if result else None

    @field_serializer('total_qty')
    def serialize_total_qty(self, total_qty: float, _info) -> str:
        return f"{total_qty:,.8f}" if total_qty else None

    @field_serializer('total_amount')
    def serialize_total_amount(self, total_amount: float, _info) -> str:
        return f"{total_amount:,.8f}" if total_amount else None

    @field_serializer('last_transaction_datetime')
    def serialize_last_transaction_datetime(self, last_transaction_datetime: datetime, _info) -> str | None:
        if not last_transaction_datetime:
            return None

        return last_transaction_datetime.strftime("%Y-%m-%d %H:%M:%S")


class RoundWithTransactions(Round):
    transactions: List[Transaction] = []
