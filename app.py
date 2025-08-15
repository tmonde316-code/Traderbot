import streamlit as st
from datetime import datetime
import bot_core as bot

st.set_page_config(page_title="Forex EMA Bot", layout="wide")
st.title("📈 Forex EMA Crossover Trading Bot")

# Connect to MT5
if bot.connect_mt5():
    st.success("Connected to MetaTrader 5 ✅")
else:
    st.error("Failed to connect to MT5 ❌")
    st.stop()

df = bot.get_data()
signal = bot.check_signal(df)
positions = bot.get_positions()

st.subheader("Latest Signal")
if signal:
    st.info(f"Signal detected: **{signal}**")
    if st.button(f"Place {signal} Trade"):
        result = bot.place_order(signal)
        if result.retcode == 10009:
            st.success(f"{signal} order placed.")
        else:
            st.error(f"Trade failed: {result.comment}")
else:
    st.warning("No new signal found.")

st.subheader("Open Positions")
if positions:
    for p in positions:
        st.write({
            "Type": "BUY" if p.type == 0 else "SELL",
            "Price": p.price_open,
            "Profit": p.profit,
            "Volume": p.volume,
            "Time": datetime.fromtimestamp(p.time),
        })
else:
    st.write("No open positions.")

if st.button("Disconnect"):
    bot.shutdown_mt5()
    st.success("Disconnected from MT5.")
  
