import aiohttp

from src.enums.symbol import SymbolEnum
from src.models.rounds import Round
from src.utils.singleton import Singleton


class BinanceService(metaclass=Singleton):
    def __init__(self):
        self.symbols = {}
        self.symbols_str = {}
        # Abaixo definimos quais pares trabalhar e suas configs
        self.settings = {
            SymbolEnum.BTCUSDT: {
                'amount': 50,
                'target_percentage': 0.5,
                'take_profit_percentage': 3,
                'trailing_stop_percentage': 0.5,
                'timedelta': 10
            },
            SymbolEnum.PEPEUSDT: {
                'amount': 10,
                'target_percentage': 0.5,
                'take_profit_percentage': 3,
                'trailing_stop_percentage': 0.5,
                'timedelta': 10
            }
        }

    async def get_price(self, symbol: SymbolEnum):
        if symbol == SymbolEnum.BRL:
            return

        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol.value}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response = await response.json()
                self.symbols[symbol] = float(response["lastPrice"])
                self.symbols_str[symbol] = f'{float(response["lastPrice"]):.2f} ({float(response["priceChangePercent"]):.2f}%)'

                if symbol in (SymbolEnum.PEPEBRL, SymbolEnum.PEPEUSDT):
                    self.symbols_str[symbol] = f'{float(response["lastPrice"]):.8f} ({float(response["priceChangePercent"]):.2f}%)'

    async def buy(self, current_round: Round) -> dict:
        symbol = current_round.symbol
        amount = self.settings[symbol]['amount']
        response = {
              "symbol": symbol.value,
              "orderId": 28,
              "orderListId": -1, # Unless it's part of an order list, value will be -1
              "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
              "transactTime": 1507725176595,
              "price": self.symbols[symbol] * 0.5,
              "origQty": amount,
              "executedQty": "10.00000000",
              "origQuoteOrderQty": "0.000000",
              "cummulativeQuoteQty": "10.00000000",
              "status": "FILLED",
              "timeInForce": "GTC",
              "type": "MARKET",
              "side": "BUY",
              "workingTime": 1507725176595,
              "selfTradePreventionMode": "NONE",
                "fills": [
                    {
                        "price": self.symbols[symbol],
                        "qty": amount / (self.symbols[symbol]),
                        "commission": (amount / (self.symbols[symbol])) * 0.01,
                        "commissionAsset": symbol.value,
                    }]
            }

        return response


    async def sell(self, current_round: Round):
        symbol = current_round.symbol
        qty = sum([t.qty for t in current_round.transactions])
        response = {
            "symbol": symbol.value,
            "orderId": 28,
            "orderListId": -1,  # Unless it's part of an order list, value will be -1
            "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
            "transactTime": 1507725176595,
            "price": self.symbols[symbol],
            "origQty": qty,
            "executedQty": "10.00000000",
            "origQuoteOrderQty": "0.000000",
            "cummulativeQuoteQty": "10.00000000",
            "status": "FILLED",
            "timeInForce": "GTC",
            "type": "MARKET",
            "side": "SELL",
            "workingTime": 1507725176595,
            "selfTradePreventionMode": "NONE",
            "fills": [
                {
                    "price": self.symbols[symbol],
                    "qty": qty,
                    "commission": qty * 0.01,
                    "commissionAsset": symbol.value,
                }]
        }

        return response