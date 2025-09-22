from sqlalchemy import Column, Integer, PrimaryKeyConstraint, Float, Enum
from sqlalchemy.orm import relationship

from src.database import Base
from src.enums.symbol import SymbolEnum


from src.settings import SETTINGS


class Round(Base):
    __tablename__ = "rounds"

    id = Column(Integer)
    symbol = Column(Enum(SymbolEnum))
    trailing_stop_price = Column(Float, nullable=True)
    result = Column(Float, nullable=True)
    transactions = relationship("Transaction", back_populates="round")

    __table_args__ = (PrimaryKeyConstraint('id', 'symbol'),)

    # Propriedades calculadas (não salvas no banco)
    @property
    def avg_price(self):
        if not self.transactions:
            return None

        total_qty = sum(t.qty for t in self.transactions)
        total_amount = sum(t.total for t in self.transactions)
        return total_amount / total_qty if total_qty else None

    @property
    def target_price(self):
        target_percentage = SETTINGS[self.symbol]['target_percentage']
        return self.avg_price * (1 - (target_percentage / 100)) if self.avg_price else None

    @property
    def take_profit_price(self):
        take_profit_percentage = SETTINGS[self.symbol]['take_profit_percentage']
        return self.avg_price * (1 + (take_profit_percentage / 100)) if self.avg_price else None

    @property
    def last_price(self):
        return None

    @property
    def last_transaction_datetime(self):
        if not self.transactions:
            return None

        return max(t.transaction_time for t in self.transactions)

    @property
    def total_qty(self):
        return sum(t.qty for t in self.transactions)

    @property
    def total_amount(self):
        return sum(t.total for t in self.transactions)
