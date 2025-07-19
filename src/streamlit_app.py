import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Walmart Dashboard", layout="wide")

@st.cache_data
def load_data():
    file_path = "src/walmart_clean_data.csv"
    if not os.path.exists(file_path):
        st.error("❌ File not found! Upload 'walmart_clean_data.csv' in 'src/' directory.")
        return pd.DataFrame()

    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df['hour'] = df['time'].dt.hour
    df['weekday'] = df['date'].dt.day_name()
    df.dropna(subset=['date', 'hour'], inplace=True)
   
    df['unit_price'] = df['unit_price'].astype(str).str.replace('$', '', regex=False)
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df.dropna(subset=['unit_price', 'quantity'], inplace=True)
    df['total'] = df['unit_price'] * df['quantity']
    return df

df = load_data()

if df.empty:
    st.warning("⚠️ No data loaded. Please upload a valid CSV file.")
    st.stop()

st.sidebar.header("🎛️ Filter Options")
branch = st.sidebar.multiselect("Branch", df['branch'].unique(), default=list(df['branch'].unique()))
category = st.sidebar.multiselect("Category", df['category'].unique(), default=list(df['category'].unique()))
date_bounds = [df['date'].min(), df['date'].max()]
date_range = st.sidebar.date_input("Date Range", value=date_bounds, min_value=date_bounds[0], max_value=date_bounds[1])

filtered_df = df[
    df['branch'].isin(branch) &
    df['category'].isin(category) &
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1]))
]

st.write("📋 Data Preview", filtered_df.head())
st.write(f"🔢 Rows Available: {len(filtered_df)}")

if filtered_df.empty:
    st.warning("⚠️ No data matches your filters. Try different selections.")
    st.stop()

st.title("🛒 Walmart Sales & Customer Insights Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total Revenue", f"₹{filtered_df['total'].sum():,.2f}")
col2.metric("⭐ Average Rating", f"{filtered_df['rating'].mean():.2f}")
col3.metric("📦 Transactions", f"{filtered_df.shape[0]}")

st.subheader("📦 Revenue by Category")
rev_by_cat = filtered_df.groupby('category')['total'].sum().reset_index()
fig1 = px.bar(rev_by_cat, x='category', y='total', color='category', title="Revenue by Category")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📅 Daily Sales Trend")
daily = filtered_df.groupby('date')['total'].sum().reset_index()
fig2 = px.line(daily, x='date', y='total', title="Daily Sales Over Time")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("⏰ Hourly & Weekday Sales Heatmap")
heatmap_data = filtered_df.groupby(['weekday', 'hour'])['total'].sum().reset_index()
heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values='total')
heatmap_pivot = heatmap_pivot.reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
st.dataframe(heatmap_pivot.style.background_gradient(cmap="Blues"))

st.subheader("💳 Sales by Payment Method")
pay_split = filtered_df.groupby('payment_method')['total'].sum().reset_index()
fig3 = px.pie(pay_split, names='payment_method', values='total', title='Payment Method Distribution')
st.plotly_chart(fig3, use_container_width=True)

st.subheader("⭐ Ratings by Branch")
fig4 = px.violin(filtered_df, x='branch', y='rating', box=True, points="all", color='branch')
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown("🔧 Made by **Ashutosh Kumar**")

