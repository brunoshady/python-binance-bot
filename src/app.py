import threading
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.responses import HTMLResponse

from src.enums.symbol import SymbolEnum
from src.schemas.rounds import Round
from src.schemas.status import Status
from src.services.background import start_background_loop
from src.services.binance import BinanceService
from src.services.rounds import RoundsService


@asynccontextmanager
async def lifespan(_app: FastAPI):
    thread = threading.Thread(target=start_background_loop, daemon=True)
    thread.start()
    print("Thread iniciada no startup")
    yield
    print("FastAPI está sendo finalizado")


app = FastAPI(lifespan=lifespan)


# GET /{symbol}/rounds              → Lista de rounds para um símbolo
# GET /{symbol}/rounds/current      → Round atual para um símbolo
# GET /{symbol}/rounds/{round_id}   → Round específico para um símbolo


@app.get("/status", response_model=Status, response_class=UJSONResponse)
async def get_status():
    rounds = []
    for symbol in SymbolEnum:
        if symbol == SymbolEnum.BRL:
            continue

        _round = RoundsService().get_current_round(symbol)

        if _round:
            rounds.append(_round)

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
    return RoundsService().get_rounds(SymbolEnum(symbol.upper()))


@app.get("/{symbol}/rounds/{round_id}", response_model=Optional[Round], response_class=UJSONResponse)
async def get_round(round_id: int | str, symbol: str):
    if round_id == "current":
        return RoundsService().get_current_round(SymbolEnum(symbol.upper()))

    return RoundsService().get_round(SymbolEnum(symbol.upper()), int(round_id))


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8080,
        log_level="debug",
        access_log=True,
        workers=1,
        timeout_keep_alive=50,
        reload=True,
    )

