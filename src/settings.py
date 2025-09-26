# Abaixo definimos quais pares trabalhar e suas configs
from src.enums.symbol import SymbolEnum

SETTINGS = {
    # SymbolEnum.BTCBRL: {
    #     'amount': 10,
    #     'target_percentage': 1.1,
    #     'take_profit_percentage': 2,
    #     'trailing_stop_percentage': 0.5,
    #     'timedelta': 30
    # },
    SymbolEnum.PEPEUSDT: {
        'amount': 1,
        'target_percentage': 1.5,
        'take_profit_percentage': 3,
        'trailing_stop_percentage': 1,
        'timedelta': 1
    }
}