from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from src.database import Base
from src.enums.symbol import SymbolEnum

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer)
    round_id = Column(Integer)

    side = Column(String)
    symbol = Column(Enum(SymbolEnum))
    order_id = Column(String)
    transaction_time = Column(DateTime)

    order_qty = Column(Float)
    order_amount = Column(Float)

    price = Column(Float)
    commission = Column(Float)
    commision_symbol = Column(String)

    qty = Column(Float)
    total = Column(Float)

    __table_args__ = (
        ForeignKeyConstraint(
            ['round_id', 'symbol'],
            ['rounds.id', 'rounds.symbol']
        ),
        PrimaryKeyConstraint('id', 'round_id', 'symbol'),
    )

    round = relationship("Round", back_populates="transactions")
