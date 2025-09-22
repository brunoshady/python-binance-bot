from sqlalchemy import func
from sqlalchemy.orm import joinedload

from src.database import SessionLocal, Base, engine
from src.enums.symbol import SymbolEnum
from src.models.rounds import Round
from src.models.transactions import Transaction
from src.utils.singleton import Singleton

Base.metadata.create_all(bind=engine)


# noinspection SqlNoDataSourceInspection,SqlDialectInspection,PyMethodMayBeStatic
class RepositoryService(metaclass=Singleton):
    def __init__(self):
        pass

    def insert_round(self, data: Round):
        db = SessionLocal()

        # Verifica se já existe um Round com result = None para o símbolo
        existing = db.query(Round).filter(Round.symbol == data.symbol, Round.result == None).first()

        if existing:
            raise Exception(f"Já existe um Round com result = None para o símbolo {data.symbol} (id={existing.id})")

        max_id = db.query(func.max(Round.id)).filter(Round.symbol == data.symbol).scalar()

        data.id = (max_id or 0) + 1

        db.add(data)
        db.commit()
        db.refresh(data)
        db.close()
        return data

    def update_round(self, data: Round, new_transaction: Transaction | None):
        db = SessionLocal()
        data = db.query(Round).filter(Round.symbol == data.symbol, Round.id == data.id).first()

        if new_transaction:
            data.transactions.append(new_transaction)

        db.merge(data)
        db.commit()
        db.refresh(data)
        db.close()
        return data

    def select_round(self, symbol: SymbolEnum, round_id: int) -> Round | None:
        db = SessionLocal()
        result = (db.query(Round)
                  .options(joinedload(Round.transactions))
                  .filter(Round.symbol == symbol, Round.id == round_id)
                  .first())
        db.close()
        return result

    def select_rounds(self, symbol: SymbolEnum) -> list[Round]:
        db = SessionLocal()
        result = (db.query(Round)
                  .options(joinedload(Round.transactions))
                  .filter(Round.symbol == symbol)
                  .order_by(Round.id.desc())
                  .all())
        db.close()
        return result

