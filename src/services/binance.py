import asyncio
import os
import time

from binance.error import ClientError
from binance.spot import Spot

from src.enums.symbol import SymbolEnum
from src.models.rounds import Round
from src.utils.singleton import Singleton

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

class BinanceService(metaclass=Singleton):
    def __init__(self):
        self.client = Spot(api_key=API_KEY, api_secret=API_SECRET)
        self.symbols = {}
        self.symbols_str = {}
        # Abaixo definimos quais pares trabalhar e suas configs
        self.settings = {
            SymbolEnum.BTCBRL: {
                'amount': 50,
                'target_percentage': 1.1,
                'take_profit_percentage': 2,
                'trailing_stop_percentage': 0.5,
                'timedelta': 5
            },
            SymbolEnum.PEPEUSDT: {
                'amount': 11,
                'target_percentage': 1.1,
                'take_profit_percentage': 3,
                'trailing_stop_percentage': 1,
                'timedelta': 1
            }
        }

    async def get_price(self, symbol: SymbolEnum):
        if symbol in (SymbolEnum.BRL, SymbolEnum.PEPE, SymbolEnum.BTC):
            return

        try:
            response = self.client.ticker_24hr(symbol=symbol.value)
        except ClientError as e:
            print(e.error_message)
            return
        except Exception as e:
            print(e)
            return

        self.symbols[symbol] = float(response["lastPrice"])
        self.symbols_str[symbol] = f'{float(response["lastPrice"]):.2f} ({float(response["priceChangePercent"]):.2f}%)'

        if symbol in (SymbolEnum.PEPEBRL, SymbolEnum.PEPEUSDT):
            self.symbols_str[symbol] = f'{float(response["lastPrice"]):.8f} ({float(response["priceChangePercent"]):.2f}%)'

    async def buy(self, current_round: Round) -> dict | None:
        symbol = current_round.symbol

        try:
            response = self.client.new_order_test(
                symbol=symbol.value,
                side="BUY",
                type="MARKET",
                quoteOrderQty=self.settings[symbol]['amount'],
                newOrderRespType="FULL",
            )

            # if response["status"] != "FILLED":
            #     return None

        except ClientError as e:
            print(e.error_message)
            return None
        except Exception as e:
            print(e)
            return None

        qty = self.settings[symbol]['amount'] / self.symbols[symbol]

        response = {
            "symbol":symbol.value,
            "orderId":111075203,
            "orderListId":-1,
            "clientOrderId":"oMTfICVk1MKcaOqAhzAvcX",
            "transactTime":int(time.time()) * 1000,
            "price":"0.00000000",
            "origQty":f"{qty:.8f}",
            "executedQty":f"{qty:.8f}",
            "origQuoteOrderQty":"0.00000000",
            "cummulativeQuoteQty":f"{qty * self.symbols[symbol]:.8f}",
            "status":"FILLED",
            "timeInForce":"GTC",
            "type":"MARKET",
            "side":"BUY",
            "workingTime":1758347004330,
            "fills":[
                {
                    "price":f"{self.symbols[symbol]:.8f}",
                    "qty":f"{qty:.8f}",
                    "commission":f"{qty * 0.01:.8f}",
                    "commissionAsset":"PEPE" if symbol in (SymbolEnum.PEPEUSDT, SymbolEnum.PEPEBRL) else "BTC",
                    "tradeId":1440387
                }
            ],
            "selfTradePreventionMode":"EXPIRE_MAKER"
        }

        return response

    async def sell(self, current_round: Round):
        symbol = current_round.symbol
        qty = sum([t.qty for t in current_round.transactions])

        try:
            response = self.client.new_order_test(
                symbol=symbol.value,
                side="SELL",
                type="MARKET",
                quantity=f"{qty:.0f}"
            )
        except ClientError as e:
            print(e.error_message)
            return None
        except Exception as e:
            print(e)
            return None

        order_total = qty * self.symbols[symbol]
        comission = order_total * 0.01

        response = {
            "clientOrderId":"NVNWsWaCfVQ5utp5Ba9waV",
            "cummulativeQuoteQty":f"{order_total - comission:.8f}",
            "executedQty":f"{qty:.0f}",
            "fills":[
                {
                    "commission":f"{comission:.8f}",
                    "commissionAsset":"BRL",
                    "price":f"{self.symbols[symbol]:.8f}",
                    "qty":f"{qty:.0f}",
                    "tradeId":1441347
                }
            ],
            "orderId":111155573,
            "orderListId":-1,
            "origQty":"189923.00",
            "origQuoteOrderQty":"0.00000000",
            "price":"0.00000000",
            "selfTradePreventionMode":"EXPIRE_MAKER",
            "side":"SELL",
            "status":"FILLED",
            "symbol":symbol.value,
            "timeInForce":"GTC",
            "transactTime":int(time.time()) * 1000,
            "type":"MARKET",
            "workingTime":1758420451610
        }

        return response