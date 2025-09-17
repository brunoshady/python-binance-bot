from typing import Dict, List

from pydantic import BaseModel

from src.enums.symbol import SymbolEnum
from src.schemas.rounds import Round


class Status(BaseModel):
    symbols: Dict[SymbolEnum, str] | None
    rounds: List[Round | None] | None

