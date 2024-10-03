import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_daily_sharing_df(df):
    daily_sharing_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"
    })
    daily_sharing_df = daily_sharing_df.reset_index()
    daily_sharing_df.rename(columns={
        "cnt": "jumlah_penyewaan"
    }, inplace=True)
    
    return daily_sharing_df

def create_days_df(df):
    days_df = df.groupby(by="holiday").instant.nunique().reset_index()
    days_df.rename(columns={
        "cnt": "jumlah"
    }, inplace=True)
    
    return days_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="instant", as_index=False).agg({
        "dteday": "max", # mengambil tanggal penyewaan terakhir
        "cnt": "sum" # menghitung jumlah penyewaan yang dihasilkan
    })
    rfm_df.columns = ["instant", "max_order_timestamp", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# Load cleaned data
all_df = pd.read_csv("all_data.csv")

all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)

all_df['dteday'] = pd.to_datetime(all_df['dteday'])

# Filter data
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]

# st.dataframe(main_df)

# # Menyiapkan berbagai dataframe
daily_sharing_df = create_daily_sharing_df(main_df)
days_df = create_days_df(main_df)
rfm_df = create_rfm_df(main_df)


# plot Sum of bike Sharing per Month (2011-2012)
st.header('Bike Sharing Dashboard :sparkles:')
st.subheader('Daily Sharing')

total_sharing = daily_sharing_df.jumlah_penyewaan.sum()
st.metric("Total Sharing", value=total_sharing)

fig, ax = plt.subplots(figsize=(50, 15))
ax.plot(
    daily_sharing_df["dteday"],
    daily_sharing_df["jumlah_penyewaan"],
    marker='o',
    linewidth=3,
    color="#72BCD4"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Sharing demographic
st.subheader("Sharing Demographics")

fig, ax = plt.subplots(figsize=(20, 10))

sns.barplot(
    y="cnt",
    x="holiday",
    data=all_df,
    palette="pastel"
)
ax.set_title("Bicycle rental distribution on weekend power weekday", loc="center", fontsize=30)
ax.set_ylabel('Jumlah Penyewaan')
ax.set_xlabel('weekend=0 dan weekday=1')
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
st.pyplot(fig)


# Best Customer Based on RFM Parameters
st.subheader("Best Tenant Based on RFM Parameters")

col1, col2 = st.columns(2)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="instant", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="instant", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Monetary", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

st.caption('Copyright © Bike Sharing')