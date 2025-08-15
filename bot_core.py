import MetaTrader5 as mt5
import pandas as pd
import pytz
from datetime import datetime

SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M15
LOT_SIZE = 0.1
SL_PIPS = 20
TP_PIPS = 60
MAGIC_NUMBER = 123456
EMAS = (10, 50)

def connect_mt5():
    return mt5.initialize()

def shutdown_mt5():
    mt5.shutdown()

def get_data(symbol=SYMBOL, timeframe=TIMEFRAME, bars=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

def check_signal(df):
    df['ema_short'] = calculate_ema(df, EMAS[0])
    df['ema_long'] = calculate_ema(df, EMAS[1])
    if df['ema_short'].iloc[-2] < df['ema_long'].iloc[-2] and df['ema_short'].iloc[-1] > df['ema_long'].iloc[-1]:
        return "BUY"
    elif df['ema_short'].iloc[-2] > df['ema_long'].iloc[-2] and df['ema_short'].iloc[-1] < df['ema_long'].iloc[-1]:
        return "SELL"
    return None

def place_order(signal):
    info = mt5.symbol_info_tick(SYMBOL)
    point = mt5.symbol_info(SYMBOL).point
    price = info.ask if signal == "BUY" else info.bid
    sl = price - SL_PIPS * point if signal == "BUY" else price + SL_PIPS * point
    tp = price + TP_PIPS * point if signal == "BUY" else price - TP_PIPS * point
    order_type = mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": MAGIC_NUMBER,
        "comment": "Streamlit Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    return result

def get_positions():
    return mt5.positions_get(symbol=SYMBOL)
  
