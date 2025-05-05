import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Tokyo Stock Explorer", layout="wide")

# Styling to remove background and enforce clean look
def remove_bg():
    st.markdown(
         """
         <style>
         .stApp {{
             background-color: white;
             color: black;
         }}
         h1, h2, h3, h4, h5, h6, p {{
             color: black;
         }}
         .stSidebar {{
             background-color: rgba(255, 255, 255, 0.9);
             color: black;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

remove_bg()

# App title
st.title("📈 Tokyo Stock Price Explorer")
st.write("Explore major Japanese companies' stock prices between April 2023 and April 2025.")

# Date range
start_date = datetime.datetime(2023, 4, 1)
end_date = datetime.datetime(2025, 4, 27)

# Sidebar - CSV Upload
st.sidebar.header("Upload or Use Live Data")
uploaded_file = st.sidebar.file_uploader("tokyo_index.csv", type=["csv"])

@st.cache_data
def load_data():
    companies = {
        'SONY': '6758.T',
        'TOYOTA': '7203.T',
        'HONDA': '7267.T',
        'MITSUBISHI CORP': '8058.T',
        'NISSAN MOTOR CORP': '7201.T',
        'NIPPON STEEL CORP': '5401.T',
        'HITACHI': '6501.T',
        'NINTENDO': '7974.T',
        'FUJITSU': '6702.T',
        'JAPAN AIRLINES': '9201.T'
    }

    frames = []
    for name, ticker in companies.items():
        data = yf.download(ticker, start=start_date, end=end_date)
        data.columns = data.columns.get_level_values(0)
        data = data.reset_index()
        data['Symbol'] = name
        frames.append(data)

    df = pd.concat(frames, axis=0)
    df['Price_change'] = df['Close'] - df['Open']
    df['High_Low_Spread'] = df['High'] - df['Low']
    df['Close_Open_Spread'] = df['Close'] - df['Open']
    return df

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Load dataset
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    st.success("✅ Uploaded CSV loaded successfully!")
else:
    with st.spinner('Fetching stock data from Yahoo Finance...'):
        df = load_data()
        st.info("ℹ️ Using live data from Yahoo Finance.")

# Sidebar - Stock selection
st.sidebar.header("Select Stock")
symbols = df['Symbol'].unique()
selected_stock = st.sidebar.selectbox("Choose a stock to visualize:", symbols)

# Sidebar - Chart settings
st.sidebar.header("Chart Settings")
chart_type = st.sidebar.radio("Choose chart type:", ['Static (Seaborn)', 'Interactive (Plotly)'])

# Sidebar - Download data
st.sidebar.header("Download Data")
csv = convert_df(df)
st.sidebar.download_button(
    label="Download dataset as CSV",
    data=csv,
    file_name='tokyo_index.csv',
    mime='text/csv',
)

# Filter selected stock
stk = df[df.Symbol == selected_stock]

# Main Area - Plotting
st.subheader(f"📊 Closing Price Trend for {selected_stock}")

if chart_type == 'Static (Seaborn)':
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=stk['Date'], y=stk['Close'], ax=ax)
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Close Price (JPY)")
    plt.title(f"{selected_stock} Stock Price Over Time")
    st.pyplot(fig)
else:
    fig = px.line(stk, x='Date', y='Close', title=f"{selected_stock} Stock Price Over Time (Interactive)")
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True)

# Checkbox - Show Full Dataset
if st.checkbox("Show Full Dataset"):
    st.dataframe(df)
