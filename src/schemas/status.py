from typing import Dict, List

from pydantic import BaseModel

from src.enums.symbol import SymbolEnum
from src.schemas.rounds import RoundWithTransactions


class Status(BaseModel):
    symbols: Dict[SymbolEnum, str] | None
    rounds: List[RoundWithTransactions | None] | None

