from sqlalchemy import Column, Integer, PrimaryKeyConstraint, Float, Enum
from sqlalchemy.orm import relationship

from src.database import Base
from src.enums.symbol import SymbolEnum


class Round(Base):
    __tablename__ = "rounds"

    id = Column(Integer)
    symbol = Column(Enum(SymbolEnum))
    trailing_stop_price = Column(Float, nullable=True)
    result = Column(Float, nullable=True)
    transactions = relationship("Transaction", back_populates="round")

    __table_args__ = (PrimaryKeyConstraint('id', 'symbol'),)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_transaction_datetime = None
        self.target_price = None
        self.last_price = None