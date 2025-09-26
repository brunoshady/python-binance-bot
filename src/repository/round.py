from src.database import SessionLocal
from src.enums.symbol import SymbolEnum
from src.models.rounds import Round
from src.repository.base import BaseRepository


class RoundRepository(BaseRepository[Round]):
    def __init__(self):
        super().__init__(Round, SessionLocal())

    def create_by_symbol(self, symbol: SymbolEnum):
        last_round = self.select_last_by_symbol(symbol)
        next_round_id = last_round[0].id + 1 if last_round else 1
        new_round = Round(id=next_round_id, symbol=symbol)
        return self.add(new_round)

    def select_by_id(self, symbol: SymbolEnum, round_id: int):
        return self.select_first_by_filter(symbol=symbol, id=round_id)

    def select_all_by_symbol(self, symbol: SymbolEnum):
        return self.select_all_by_filter(symbol=symbol)

    def select_current_by_symbol(self, symbol: SymbolEnum):
        return self.select_first_by_filter(symbol=symbol, result=None)

    def select_last_by_symbol(self, symbol: SymbolEnum):
        query = self.session.query(self.model).filter_by(symbol=symbol).order_by(Round.id.desc()).limit(1)
        return query.all()