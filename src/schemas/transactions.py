from datetime import datetime

from pydantic import BaseModel, field_serializer, Field

from src.enums.side import SideEnum
from src.enums.symbol import SymbolEnum


class Transaction(BaseModel):
    id: int
    round_id: int = Field(serialization_alias="roundId")
    date_time: datetime = Field(serialization_alias="dateTime")
    side: SideEnum
    symbol: SymbolEnum
    price: float
    qty: float
    amount: float
    commission: float
    commission_type: SymbolEnum = Field(serialization_alias="commissionType")
    total: float

    @field_serializer('price')
    def serialize_price(self, price: float, _info) -> str:
        if self.symbol in (SymbolEnum.PEPEBRL, SymbolEnum.PEPEUSDT):
            return f"{price:,.8f}"

        return f"{price:,.2f}"

    @field_serializer('qty')
    def serialize_qty(self, qty: float, _info) -> str:
        return f"{qty:,.8f}"

    @field_serializer('amount')
    def serialize_amount(self, amount: float, _info) -> str:
        return f"{amount:,.2f}"

    @field_serializer('commission')
    def serialize_commission(self, commission: float, _info) -> str:
        return f"{commission:,.8f}"

    @field_serializer('total')
    def serialize_total(self, total: float, _info) -> str:
        return f"{total:,.2f}"

    @field_serializer('date_time')
    def serialize_date_time(self, date_time: datetime, _info) -> str:
        return date_time.strftime("%Y-%m-%d %H:%M:%S")
