import asyncio
import datetime

from src.enums.side import SideEnum
from src.enums.symbol import SymbolEnum
from src.services.binance import BinanceService
from src.services.rounds import RoundsService
from src.services.transactions import TransactionsService


def start_background_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(brackground_worker())


async def brackground_worker():
    print("Background Worker -> Thread iniciada no startup")

    binance_service = BinanceService()
    rounds_service = RoundsService()
    transactions_service = TransactionsService()

    while True:
        try:
            while True:
                for symbol in SymbolEnum:
                    await binance_service.get_price(symbol)

                for symbol in binance_service.settings.keys():
                    current_round = rounds_service.get_current_round(symbol, True)
                    current_transaction = transactions_service.get_last_transaction(symbol, current_round.id)

                    if not current_transaction:
                        response = await binance_service.buy(current_round)
                        transactions_service.new_transaction(SideEnum.BUY, current_round, response)
                        current_round = rounds_service.get_current_round(symbol)

                    last_price = current_round.last_price
                    target_price = current_round.target_price

                    # Verificar se o preço atual está abaixo do avg - desvio
                    # Se estiver, comprar mais
                    timedelta = binance_service.settings[symbol]['timedelta']
                    if last_price < target_price and (current_round.last_transaction_datetime + datetime.timedelta(minutes=timedelta)) < datetime.datetime.now():
                        response = await binance_service.buy(current_round)
                        transactions_service.new_transaction(SideEnum.BUY, current_round, response)

                    # Verificar se o preço atual está acima do avg + take profit
                    # Se estiver, vender tudo
                    # Se vender tudo, fechar a rodada
                    trailing_stop_price = current_round.trailing_stop_price
                    if trailing_stop_price and last_price <= trailing_stop_price:
                        response = await binance_service.sell(current_round)
                        transactions_service.new_transaction(SideEnum.SELL, current_round, response)
                        rounds_service.close_round(current_round)

                await asyncio.sleep(0.5)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)
