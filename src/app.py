import threading
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.responses import HTMLResponse

from src.enums.symbol import SymbolEnum
from src.schemas.rounds import Round, RoundWithTransactions
from src.schemas.status import Status
from src.services.background import start_background_loop
from src.services.binance import BinanceService
from src.services.rounds import RoundsService
from src.settings import SETTINGS


@asynccontextmanager
async def lifespan(_app: FastAPI):
    thread = threading.Thread(target=start_background_loop, daemon=True)
    thread.start()
    print("Thread iniciada no startup")
    yield
    print("FastAPI está sendo finalizado")


app = FastAPI(lifespan=lifespan)
round_service = RoundsService()


# GET /{symbol}/rounds              → Lista de rounds para um símbolo
# GET /{symbol}/rounds/current      → Round atual para um símbolo
# GET /{symbol}/rounds/{round_id}   → Round específico para um símbolo


@app.get("/status", response_model=Status, response_class=UJSONResponse)
async def get_status():
    rounds = []
    for symbol in SETTINGS.keys():
        current_round = round_service.get_current_round(symbol)

        if current_round:
            round_service.update_values(current_round)
            rounds.append(current_round)

    return {'symbols': BinanceService().symbols_str, 'rounds': rounds}


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
        <html>
            <body>
                <pre id="status">Carregando...</pre>
                <script>
                    async function atualizarStatus() {
                        try {
                            const res = await fetch('/status');
                            const data = await res.json();
                            document.getElementById('status').innerText = JSON.stringify(data, null, 2);
                        } catch (err) {
                            document.getElementById('status').innerText = "Erro ao buscar status";
                        }
                    }
                    setInterval(atualizarStatus, 500); // Atualiza a cada 2 segundos
                    atualizarStatus(); // Atualiza imediatamente ao carregar
                </script>
            </body>
        </html>
        """


@app.get("/{symbol}/rounds", response_model=List[Round], response_class=UJSONResponse)
async def get_rounds(symbol: str):
    rounds = round_service.get_rounds(SymbolEnum(symbol.upper()))

    for _round in rounds:
        round_service.update_values(_round)

    rounds.reverse()
    return rounds


@app.get("/{symbol}/rounds/{round_id}", response_model=Optional[RoundWithTransactions], response_class=UJSONResponse)
async def get_round(round_id: int | str, symbol: str):
    if round_id == "current":
        current_round = round_service.get_current_round(SymbolEnum(symbol.upper()))
        round_service.update_values(current_round)
        return current_round

    _round = round_service.get_round(SymbolEnum(symbol.upper()), int(round_id))
    round_service.update_values(_round)
    return _round


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=9090,
        log_level="warning",
        use_colors=True,
        access_log=True,
        workers=1,
        timeout_keep_alive=50,
        reload=True,
    )

