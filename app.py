import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Supply/Demand Screener", layout="wide")
st.title("🎯 Advanced Supply/Demand Zone Screener")

# Timeframe Mapping
timeframe_map = {
    "5 Min": "5T", "15 Min": "15T", "30 Min": "30T", "75 Min": "75T",
    "125 Min": "125T", "1 Hr": "1H", "2 Hr": "2H", "4 Hr": "4H",
    "5 Hr": "5H", "6 Hr": "6H", "8 Hr": "8H", "10 Hr": "10H",
    "12 Hr": "12H", "16 Hr": "16H", "Daily": "D", "Weekly": "W"
}

# --- LOGIC FUNCTIONS ---
@st.cache_data(ttl=3600)
def get_data(symbol, interval):
    time.sleep(1.5) # Anti-ban delay
    return yf.download(symbol, period="1mo" if 'T' in interval else "1y", interval=interval, threads=True)

def check_zone(df):
    results = []
    # 3-candle strategy logic (Legin, Base, Legout)
    for i in range(2, len(df) - 1):
        legin, base, legout = df.iloc[i-1], df.iloc[i], df.iloc[i+1]
        
        # 1. Legin Body > 65%
        legin_body = abs(legin['Close'] - legin['Open'])
        if (legin_body / (legin['High'] - legin['Low'] + 0.0001)) < 0.65: continue
            
        # 2. Base Body < 50% of Legin
        if abs(base['Close'] - base['Open']) > (legin_body * 0.5): continue
            
        # 3. Legout validation (Body & Volume)
        if not (abs(legout['Close'] - legout['Open']) > legin_body and legout['Volume'] > legin['Volume']): continue
        
        # 6. White Area & 7. Candle behind (Simplified)
        if not (legout['Open'] > base['Close'] if legout['Close'] > legout['Open'] else legout['Open'] < base['Close']): continue
        
        results.append({"Price": legout['Open'], "Type": "Demand" if legout['Close'] > legout['Open'] else "Supply"})
    return results

# --- UI SECTION ---
with st.sidebar:
    tickers = st.text_area("Stocks (comma separated)", "RELIANCE.NS, TCS.NS, INFY.NS")
    selected_tfs = st.multiselect("Select Timeframes", list(timeframe_map.keys()), default=["1 Hr"])
    scan_btn = st.button("🚀 Start Scan")

if scan_btn:
    for symbol in tickers.split(","):
        symbol = symbol.strip()
        st.subheader(f"Results for {symbol}")
        for tf in selected_tfs:
            raw_data = get_data(symbol, "1m" if 'T' in timeframe_map[tf] else "1h")
            df = raw_data.resample(timeframe_map[tf]).agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()
            
            zones = check_zone(df)
            if zones:
                st.write(f"✅ Zones found in {tf}:", pd.DataFrame(zones))
            else:
                st.write(f"❌ No zones in {tf}")
