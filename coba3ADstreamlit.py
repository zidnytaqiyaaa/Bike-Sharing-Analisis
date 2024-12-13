import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore

# Load dataset
data = pd.read_csv("hour.csv")

# Preprocessing
data['z_scores'] = zscore(data['cnt'])
threshold = 3
data_no_outliers = data[data['z_scores'].abs() <= threshold]
datafix = data_no_outliers.drop(columns=['z_scores'])
datafix['dteday'] = pd.to_datetime(datafix['dteday'])

# Header Function
def create_header():
    st.markdown(
        """
        <div style="background-color:#AEC6CF;padding:10px;border-radius:10px;">
            <h1 style="color:#2F4F4F;text-align:center;">Dashboard Bike Sharing</h1>
            <p style="color:#2F4F4F;text-align:center;">Analisis dan Visualisasi Data Penggunaan Sepeda</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Boxplot Function
def plot_boxplot(data):
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")

    palette = sns.color_palette("pastel", n_colors=4)
    sns.boxplot(
        x='season',
        y='cnt',
        data=data,
        palette=palette,
        showmeans=True,
        meanprops={"marker": "o", "markerfacecolor": "red", "markeredgecolor": "black"}
    )
    plt.title('Pengaruh Musim terhadap Penggunaan Sepeda', fontsize=16, fontweight='bold')
    plt.xlabel('Musim (1: Spring, 2: Summer, 3: Fall, 4: Winter)', fontsize=12)
    plt.ylabel('Jumlah Pengguna Sepeda', fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(plt)

# Scatter Plot Function
def plot_scatter(data):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='temp', y='cnt', data=data, alpha=0.7, edgecolor='k', s=50)
    sns.regplot(x='temp', y='cnt', data=data, scatter=False, color='red', line_kws={'linewidth': 2})
    plt.title('Hubungan antara Suhu dan Jumlah Pengguna Sepeda', fontsize=16, weight='bold')
    plt.xlabel('Suhu (Ternormalisasi)', fontsize=12)
    plt.ylabel('Jumlah Penggunaan Sepeda', fontsize=12)
    plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    plt.tight_layout()
    st.pyplot(plt)

# Bar Chart Function
def plot_barchart(data):
    def classify_time(hour):
        if 0 <= hour < 6:
            return 'Dini Hari'
        elif 6 <= hour < 12:
            return 'Pagi'
        elif 12 <= hour < 18:
            return 'Siang'
        else:
            return 'Malam'

    data['time_of_day'] = data['hr'].apply(classify_time)
    time_of_day_trend = data.groupby('time_of_day')['cnt'].mean().reset_index()
    time_of_day_trend['time_of_day'] = pd.Categorical(
        time_of_day_trend['time_of_day'],
        categories=['Dini Hari', 'Pagi', 'Siang', 'Malam'],
        ordered=True
    )
    time_of_day_trend = time_of_day_trend.sort_values('time_of_day')

    plt.figure(figsize=(10, 6))
    sns.barplot(data=time_of_day_trend, x='time_of_day', y='cnt', palette='Set2')
    plt.title('Rata-rata Penyewaan Sepeda Berdasarkan Waktu dalam Sehari', fontsize=16, weight='bold')
    plt.xlabel('Waktu dalam Sehari', fontsize=12)
    plt.ylabel('Rata-rata Jumlah Penyewaan Sepeda', fontsize=12)
    plt.grid(axis='y', color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    plt.tight_layout()
    st.pyplot(plt)

# Line Plot Function
def plot_lineplot(data):
    monthly_data = data.groupby(['yr', 'mnth'])['cnt'].sum().reset_index()
    data_2011 = monthly_data[monthly_data['yr'] == 0]
    data_2012 = monthly_data[monthly_data['yr'] == 1]

    plt.figure(figsize=(12, 6))
    plt.plot(data_2011['mnth'], data_2011['cnt'], marker='o', label='Tahun Pertama (2011)', color='#A1C6EA', linewidth=3)
    plt.plot(data_2012['mnth'], data_2012['cnt'], marker='o', label='Tahun Kedua (2012)', color='#F4A9A8', linewidth=3)
    plt.title('Tren Penyewaan Sepeda Berdasarkan Bulan di Tahun Pertama dan Kedua', fontsize=14, weight='bold')
    plt.xlabel('Bulan', fontsize=12)
    plt.ylabel('Jumlah Penyewaan (Cnt)', fontsize=12)
    plt.xticks(range(1, 13))
    plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)

# RFM Analysis Function
def calculate_rfm(data):
    today_date = data['dteday'].max()
    rfm_season = data.groupby('season').agg(
        Recency=('dteday', lambda x: (today_date - x.max()).days),
        Frequency=('instant', 'count'),
        Monetary=('cnt', 'sum')
    ).reset_index()
    season_mapping = {1: 'Musim Semi', 2: 'Musim Panas', 3: 'Musim Gugur', 4: 'Musim Dingin'}
    rfm_season['season'] = rfm_season['season'].map(season_mapping)
    return rfm_season

def plot_rfm(rfm):
    fig, axes = plt.subplots(1, 3, figsize=(24, 6), sharey=False)
    fig.patch.set_facecolor('#333333')
    plt.subplots_adjust(wspace=0.5)

    sns.barplot(x=rfm['season'], y=rfm['Recency'], ax=axes[0], palette='Blues')
    axes[0].set_title('Recency (days) per Season', fontsize=14, color='white')
    axes[0].set_xlabel('Season', fontsize=12, color='white')
    axes[0].set_ylabel('Recency (days)', fontsize=12, color='white')
    axes[0].tick_params(colors='white')

    sns.barplot(x=rfm['season'], y=rfm['Frequency'], ax=axes[1], palette='Greens')
    axes[1].set_title('Frequency per Season', fontsize=14, color='white')
    axes[1].set_xlabel('Season', fontsize=12, color='white')
    axes[1].tick_params(colors='white')

    sns.barplot(x=rfm['season'], y=rfm['Monetary'], ax=axes[2], palette='Reds')
    axes[2].set_title('Monetary per Season', fontsize=14, color='white')
    axes[2].set_xlabel('Season', fontsize=12, color='white')
    axes[2].tick_params(colors='white')

    for ax in axes:
        ax.set_facecolor('#333333')
    fig.suptitle('Rata-rata RFM Berdasarkan Musim', fontsize=16, color='white')
    st.pyplot(fig)

# Main Function
def main():
    create_header()

    st.subheader("Pengaruh Musim terhadap Penggunaan Sepeda")
    plot_boxplot(datafix)

    st.subheader("Hubungan antara Suhu dan Jumlah Pengguna Sepeda")
    plot_scatter(datafix)

    st.subheader("Rata-rata Penyewaan Sepeda Berdasarkan Waktu dalam Sehari")
    plot_barchart(datafix)

    st.subheader("Tren Penyewaan Sepeda Berdasarkan Bulan di Tahun Pertama dan Kedua")
    plot_lineplot(datafix)

    st.subheader("Analisis RFM Berdasarkan Musim")
    rfm = calculate_rfm(datafix)
    plot_rfm(rfm)

if __name__ == "__main__":
    main()
