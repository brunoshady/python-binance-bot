from datetime import datetime

from pydantic import BaseModel, field_serializer, Field

from src.enums.side import SideEnum
from src.enums.symbol import SymbolEnum


class Transaction(BaseModel):
    id: int
    round_id: int = Field(serialization_alias="roundId")
    side: SideEnum
    symbol: SymbolEnum
    order_id: int = Field(serialization_alias="orderId")
    transaction_time: datetime = Field(serialization_alias="TransactionTime")
    price: float
    qty: float
    order_amount: float = Field(serialization_alias="orderAmount")
    commission: float
    commision_symbol: SymbolEnum = Field(serialization_alias="commissionSymbol")
    total: float

    @field_serializer('price')
    def serialize_price(self, price: float, _info) -> str:
        if self.symbol in (SymbolEnum.PEPEBRL, SymbolEnum.PEPEUSDT):
            return f"{price:,.8f}"

        return f"{price:,.2f}"

    @field_serializer('qty')
    def serialize_qty(self, qty: float, _info) -> str:
        return f"{qty:,.8f}"

    @field_serializer('order_amount')
    def serialize_order_amount(self, order_amount: float, _info) -> str:
        return f"{order_amount:,.8f}"

    @field_serializer('commission')
    def serialize_commission(self, commission: float, _info) -> str:
        return f"{commission:,.8f}"

    @field_serializer('total')
    def serialize_total(self, total: float, _info) -> str:
        return f"{total:,.8f}"

    @field_serializer('transaction_time')
    def serialize_transaction_time(self, transaction_time: datetime, _info) -> str:
        return transaction_time.strftime("%Y-%m-%d %H:%M:%S")
