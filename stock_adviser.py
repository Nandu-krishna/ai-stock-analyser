import streamlit as st
import requests
import numpy as np
import yfinance as yf

# Alpha Vantage API Key 
API_KEY = "SCV41BJPD9WLYFOU"
# Gemini API Key 
GEMINI_API_KEY = "AIzaSyDj6944bKkdHHZnUhg9TzyaSAK9NSonXxg"


# Function to fetch stock prices
def get_stock_price(ticker):
    try:
        if ticker.endswith(".BSE") or ticker.endswith(".NS"):
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            if not data.empty:
                stock_price_inr = round(data["Close"].iloc[-1], 2)
                return f"{ticker}: ₹{stock_price_inr} (INR)"
            else:
                return f"{ticker}: No recent price data available. It might be delisted or incorrect."
        else:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}&outputsize=compact"
            response = requests.get(url).json()
            time_series = response.get("Time Series (Daily)")
            if time_series:
                latest_date = max(time_series.keys())
                stock_price = round(float(time_series[latest_date]["4. close"]), 2)
                return f"{ticker}: ${stock_price} (USD)"
            else:
                return f"{ticker}: No recent price data available. It might be delisted or incorrect."
    except Exception as e:
        return f"{ticker}: Error fetching data: {e}"


# Function to calculate stock volatility (risk)
def calculate_stock_risk(ticker):
    try:
        if ticker.endswith(".BSE") or ticker.endswith(".NS"):
            stock = yf.Ticker(ticker)
            data = stock.history(period="6mo")
            if not data.empty:
                returns = data['Close'].pct_change().dropna()
                risk = np.std(returns)
                return round(risk, 4), round(risk * 100, 2)
            else:
                return "Risk Data Not Available", "N/A"
        else:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}&outputsize=full"
            response = requests.get(url).json()
            time_series = response.get("Time Series (Daily)")
            if time_series:
                prices = [float(data["4. close"]) for date, data in sorted(time_series.items(), reverse=True)[:180]]
                returns = np.diff(prices) / prices[:-1]
                risk = np.std(returns)
                return round(risk, 4), round(risk * 100, 2)
            else:
                return "Risk Data Not Available", "N/A"
    except Exception as e:
        return f"Error calculating risk: {e}", "N/A"


# Function to analyze portfolio
def analyze_portfolio(tickers):
    portfolio_returns = []
    for ticker in tickers:
        try:
            if ticker.endswith(".BSE") or ticker.endswith(".NS"):
                stock = yf.Ticker(ticker)
                data = stock.history(period="6mo")
                if not data.empty:
                    returns = data['Close'].pct_change().dropna()
                    portfolio_returns.append(returns)
            else:
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}&outputsize=full"
                response = requests.get(url).json()
                time_series = response.get("Time Series (Daily)")
                if time_series:
                    prices = [float(data["4. close"]) for date, data in sorted(time_series.items(), reverse=True)[:180]]
                    returns = np.diff(prices) / prices[:-1]
                    portfolio_returns.append(returns)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")  
            continue

    if portfolio_returns:
        portfolio_returns = np.concatenate(portfolio_returns)
        portfolio_volatility = np.std(portfolio_returns)
        expected_return = np.mean(portfolio_returns)
        risk_free_rate = 0.04 / 252  
        sharpe_ratio = (expected_return - risk_free_rate) / portfolio_volatility if portfolio_volatility != 0 else "N/A"
        return (
            round(portfolio_volatility, 4), round(portfolio_volatility * 100, 2),
            round(expected_return, 4), round(expected_return * 100, 2),
            round(sharpe_ratio, 4) if sharpe_ratio != "N/A" else "N/A"
        )
    else:
        return "No Data Available", "N/A", "No Data Available", "N/A", "No Data Available"



def ask_ai(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)  
        response.raise_for_status()
        response_json = response.json()
        try:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "Error: Unexpected response format from Gemini AI."
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to fetch response from Gemini AI: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred while processing the AI response: {e}"



st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        background: white;
        color: black;
    }

    .stApp {
        background: white;
    }

    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 18px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }

    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.9);
        color: black;
        border-radius: 5px;
        padding: 10px;
        border: 1px solid rgba(0, 0, 0, 0.3);
        font-size: 18px;
        font-weight: bold;
    }

    .stTextInput>div>div>input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 5px rgba(76, 175, 80, 0.5);
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: black;
        font-size: 24px;
        font-weight: bold;
        animation: fadeIn 1s ease-in-out;
    }

    .stMarkdown p {
        color: black;
        font-size: 18px;
        font-weight: bold;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit App
st.title("📈 Stock Analysis and AI Investment Advisor 🤖")

st.markdown(
    """
    **Disclaimer:** The information provided by this app, including AI-generated responses, is for informational purposes only and is based on *historical data*.  It is *not* financial advice. Investment decisions should be made based on thorough research and consultation with a qualified financial advisor. Past performance is not indicative of future results.  Stock market investments carry risk, including the potential loss of principal.
    """
)

# Default stock symbols
default_tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

# User input for additional stocks
user_input = st.text_input("Enter stock symbols (comma-separated, e.g., TATASTEEL.NS, AAPL):").upper().strip()
user_tickers = [ticker.strip() + (".NS" if not ticker.endswith(".BSE") and not ticker.endswith(".NS") else "") for ticker in user_input.split(",")] if user_input else []

# Store stock results and portfolio analysis
stock_results = ""
portfolio_analysis_results = ""

# Fetch and display stock prices
if st.button("Get Stock Prices"):
    st.subheader("📌 Stock Prices:")
    for ticker in default_tickers + user_tickers:
        result = get_stock_price(ticker)
        st.write(result)
        stock_results += result + "\n"  

# Risk Analysis for user stocks
if user_tickers:
    st.subheader("📊 Stock Risk Analysis:")
    for ticker in user_tickers:
        risk_value, risk_percentage = calculate_stock_risk(ticker)
        st.write(f"{ticker}: Risk Level = {risk_percentage}%")
        stock_results += f"{ticker}: Risk Level = {risk_percentage}%\n"  

# Portfolio Analysis
if user_tickers:
    portfolio_volatility, portfolio_volatility_pct, expected_return, expected_return_pct, sharpe_ratio = analyze_portfolio(
        user_tickers)
    st.subheader("📈 Portfolio Analysis:")
    st.write(f"Portfolio Risk (Volatility): {portfolio_volatility_pct}%")
    st.write(f"Expected Return (based on past 6 months): {expected_return_pct}%")
    st.write(f"Sharpe Ratio: {sharpe_ratio}")

    portfolio_analysis_results = (
        f"Portfolio Risk (Volatility): {portfolio_volatility_pct}%\n"
        f"Expected Return (based on past 6 months): {expected_return_pct}%\n"
        f"Sharpe Ratio: {sharpe_ratio}\n"
    )
    stock_results += f"\n📈 Portfolio Analysis:\n{portfolio_analysis_results}"  

# AI Investment Advice
if st.button("Get AI Investment Insights"):
    with st.spinner("AI is analyzing the portfolio and generating investment insights..."):
        ai_prompt = f"""
        I have analyzed a portfolio with the following characteristics (based on the past 6 months of data, which is NOT a guarantee of future results):
        - Tickers: {user_tickers}
        - Portfolio Volatility: {portfolio_volatility_pct}%
        - Expected Return: {expected_return_pct}%
        - Sharpe Ratio: {sharpe_ratio}

        This data is for informational purposes only and does not constitute financial advice.

        Based on this historical data, **identify three potential strengths and three potential weaknesses of this portfolio.  For each strength and weakness, provide a brief explanation and a suggested action item for improvement (if applicable). Structure your response as two numbered lists.** REMEMBER TO EMPHASIZE THE IMPORTANCE OF DIVERSIFICATION and the need to consult a financial advisor.
        """ # Modified Prompt
        ai_response = ask_ai(ai_prompt)
    st.markdown("") 
    st.write(ai_response)

# User can ask additional questions
user_query = st.text_input("Ask AI about investments:")
if st.button("Ask AI"):
    with st.spinner("AI is analyzing your question and generating a response..."):
        
        if any(ticker in user_query.upper() for ticker in user_tickers + default_tickers) or "PORTFOLIO" in user_query.upper() or "RISK" in user_query.upper() or "RETURN" in user_query.upper(): 
            ai_followup_prompt = f"""Here is some information about stock prices, risk analysis, and portfolio analysis:
            {stock_results}

            User Question: {user_query}

            **Assuming I have a moderate risk tolerance, what are three specific adjustments I could make to this portfolio to potentially increase its Sharpe ratio, given the data above?  For each adjustment, explain the rationale behind it and estimate the potential impact on risk and return.  Structure your response as a bulleted list.** Remember that this is not financial advice.
            """ 
        else: 
            ai_followup_prompt = f"""User Question: {user_query}

            **Explain three common investment strategies suitable for someone with a long-term investment horizon (e.g., over 10 years).  For each strategy, describe its risk profile and potential benefits.** Emphasize the importance of diversification and consulting with a qualified financial advisor. **Structure your response as a numbered list.** Remember that this is not financial advice.
            """ 

        ai_followup_response = ask_ai(ai_followup_prompt)
    st.subheader("🤖 AI Response:")
    st.write(ai_followup_response)