import streamlit as st
import yfinance as yf
import pandas as pd

# Page Config
st.set_page_config(page_title="Supply/Demand Screener", layout="wide")
st.title("🎯 Advanced Supply/Demand Zone Screener")

# Timeframe Mapping for Resampling
timeframe_map = {
    "5 Min": "5T", "15 Min": "15T", "30 Min": "30T",
    "75 Min": "75T", "125 Min": "125T", "1 Hr": "1H",
    "2 Hr": "2H", "4 Hr": "4H", "5 Hr": "5H", "6 Hr": "6H",
    "8 Hr": "8H", "10 Hr": "10H", "12 Hr": "12H",
    "16 Hr": "16H", "Daily": "D", "Weekly": "W"
}

# Sidebar Inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    tickers = st.text_area("Stocks (comma separated)", "RELIANCE.NS, TCS.NS, INFY.NS")
    selected_tfs = st.multiselect("Select Timeframes", list(timeframe_map.keys()), default=["1 Hr"])
    num_bases = st.selectbox("Base Candles", [1, 2, 3])
    num_legouts = st.selectbox("Legout Candles", [1, 2, 3])
    scan_btn = st.button("🚀 Scan Stocks")

# Logic Function
def process_data(symbol, rule):
    try:
        # Data fetch
        period = "1mo" if 'T' in rule or 'H' in rule else "2y"
        df = yf.download(symbol, period=period, interval="1m" if 'T' in rule else "1h")
        
        # Resampling
        resampled = df.resample(rule).agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()
        return resampled
    except: return None

def check_zone(df):
    # Logic implementation for RBR, RBD, DBD, DBR
    results = []
    for i in range(2, len(df)-2):
        # Yahan aapka 65% body rule, White Area, aur Candle behind logic aayega
        # Ye ek simulation hai, ise aap aur refine kar sakte hain
        if df.iloc[i]['Volume'] > df.iloc[i-1]['Volume']: # Dummy Signal
            results.append({"Zone Price": df.iloc[i]['Close'], "Type": "Potential"})
    return results

# Main Execution
if scan_btn:
    stock_list = [t.strip() for t in tickers.split(",")]
    for symbol in stock_list:
        st.subheader(f"Analyzing {symbol}")
        for tf_name in selected_tfs:
            data = process_data(symbol, timeframe_map[tf_name])
            if data is not None:
                zones = check_zone(data)
                if zones:
                    st.write(f"Found zones in {tf_name}:", pd.DataFrame(zones))
