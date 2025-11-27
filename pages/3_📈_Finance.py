import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Finance", page_icon="📈", layout="wide")

st.title("📈 Finance Dashboard")

tab1, tab2, tab3 = st.tabs(["Crypto Tracker", "Stock Charts", "Loan Calculator"])

# --- Crypto Tracker ---
with tab1:
    st.header("🪙 Crypto Price Tracker")
    st.caption("Top 10 Cryptocurrencies by Market Cap (via CoinGecko)")
    
    if st.button("Refresh Prices"):
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false"
        try:
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                df = pd.DataFrame(data)
                df = df[["name", "symbol", "current_price", "market_cap", "price_change_percentage_24h"]]
                df.columns = ["Name", "Symbol", "Price (USD)", "Market Cap", "24h Change %"]
                
                # Colorize change
                def color_change(val):
                    color = 'green' if val > 0 else 'red'
                    return f'color: {color}'
                
                st.dataframe(df.style.applymap(color_change, subset=['24h Change %']), use_container_width=True)
            else:
                st.error("Rate limit exceeded or API error. Try again later.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Stock Charts ---
with tab2:
    st.header("📊 Stock Market Charts")
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, GOOG)", "AAPL")
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "5y", "max"])
    
    if st.button("Get Stock Data"):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if not hist.empty:
                st.subheader(f"{ticker.upper()} - {stock.info.get('shortName', ticker)}")
                st.metric("Current Price", f"${hist['Close'].iloc[-1]:.2f}")
                
                # Line Chart
                fig = px.line(hist, x=hist.index, y="Close", title=f"{ticker} Closing Price")
                st.plotly_chart(fig, use_container_width=True)
                
                # Data Table
                with st.expander("View Historical Data"):
                    st.dataframe(hist)
            else:
                st.error("No data found for this ticker.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Loan Calculator ---
with tab3:
    st.header("💸 Simple Loan Calculator")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        amount = st.number_input("Loan Amount ($)", min_value=1000, value=10000, step=500)
    with col2:
        rate = st.number_input("Interest Rate (% per year)", min_value=0.1, value=5.0, step=0.1)
    with col3:
        years = st.number_input("Loan Term (Years)", min_value=1, value=5)
        
    if st.button("Calculate"):
        # Monthly interest rate
        r = rate / 100 / 12
        # Total number of payments
        n = years * 12
        
        # Monthly payment formula
        if r > 0:
            monthly_payment = amount * (r * (1 + r)**n) / ((1 + r)**n - 1)
        else:
            monthly_payment = amount / n
            
        total_payment = monthly_payment * n
        total_interest = total_payment - amount
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Monthly Payment", f"${monthly_payment:,.2f}")
        c2.metric("Total Interest", f"${total_interest:,.2f}")
        c3.metric("Total Cost", f"${total_payment:,.2f}")
