import os
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard Analisis Penyewaan Sepeda", page_icon="📊", layout="wide")
sns.set(style="whitegrid")

st.markdown("""
<style>
  .block-container {padding-top: 1rem; padding-bottom: .5rem;}
  [data-testid="stSidebar"] {background:#1f2530;}
  [data-testid="stSidebar"] * {color:#f0f2f6 !important;}
</style>
""", unsafe_allow_html=True)

# ------------------ Load data (tanpa input path di UI) ------------------
BASE = Path(__file__).parent
CSV_PATH = BASE / "hour_cleaned.csv"

@st.cache_data
def load_csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p)

df = None
if CSV_PATH.exists():
    df = load_csv(CSV_PATH)
else:
    st.sidebar.warning("Letakkan `hour_cleaned.csv` di folder ini, atau unggah file di bawah.")
    up = st.sidebar.file_uploader("Unggah hour_cleaned.csv", type=["csv"])
    if up:
        df = pd.read_csv(up)

if df is None:
    st.error("Data belum tersedia.")
    st.stop()

# Kolom & label sesuai Colab
if "dteday" not in df.columns:
    st.error("Kolom 'dteday' tidak ada di dataset.")
    st.stop()
df["dteday"] = pd.to_datetime(df["dteday"])

weather_label = {1:"Clear", 2:"Mist/Cloudy", 3:"Light Rain/Snow", 4:"Heavy Rain/Snow"}
weekday_labels = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
month_labels   = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
season_labels  = {1:"Spring", 2:"Summer", 3:"Fall", 4:"Winter"}

if "weathersit" in df.columns: df["weather_name"] = df["weathersit"].map(weather_label)
if "weekday"   in df.columns: df["weekday_name"] = df["weekday"].apply(lambda x: weekday_labels[int(x)%7])
if "mnth"      in df.columns: df["month_name"]   = df["mnth"].apply(lambda x: month_labels[int(x)-1])
if "season"    in df.columns: df["season_name"]  = df["season"].map(season_labels)

# ------------------ Sidebar ------------------
img_candidates = [
    BASE / "penyewaan_sepeda.jpg",
    BASE / "assets" / "penyewaan_sepeda.jpg",
    Path(r"C:\Users\vivob\dashbord\penyewaan_sepeda.jpg"),
]
img_path = next((p for p in img_candidates if p.exists()), None)
if img_path:
    st.sidebar.image(str(img_path), use_container_width=True)
else:
    st.sidebar.image("https://em-content.zobj.net/source/microsoft-teams/363/bicycle_1f6b2.png", width=100)

st.sidebar.markdown("## Bike Sharing Dashboard")

min_d, max_d = df["dteday"].min(), df["dteday"].max()
date_rng = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=(min_d.date(), max_d.date()),
    min_value=min_d.date(), max_value=max_d.date()
)
start_d, end_d = pd.to_datetime(date_rng[0]), pd.to_datetime(date_rng[1])

analysis = st.sidebar.selectbox(
    "Pilih Analisis",
    [
        "Cuaca ➜ Rata-rata Penyewaan (Line)",
        "Pola Waktu 2011 ➜ Jam × Hari (Heatmap)",
        "Pola Bulanan 2011 ➜ Bar Chart",
        "Tren Musim 2011–2012 ➜ Area Line",
        "RFM ➜ (Recency Bar H, Scatter F–M, Histogram M)"
    ]
)

fdf = df[(df["dteday"] >= start_d) & (df["dteday"] <= end_d)].copy()
if fdf.empty:
    st.warning("Tidak ada data pada rentang tanggal yang dipilih.")
    st.stop()

# ------------------ Header ------------------
st.markdown("# 📊 Dashboard Analisis Penyewaan Sepeda")
st.caption(f"Data range: {start_d.date()} to {end_d.date()}")

def draw(fig):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# =====================================================================
# 1) CUACA — LINE CHART (BUKAN HORIZONTAL)
# =====================================================================
if analysis == "Cuaca ➜ Rata-rata Penyewaan (Line)":
    st.subheader("Rata-rata Penyewaan per Kondisi Cuaca")
    # group persis seperti di Colab-mu
    avg_weather = fdf.groupby("weathersit")["cnt"].mean().reset_index()
    avg_weather["weathersit"] = avg_weather["weathersit"].map(weather_label)

    st.write("Rata-rata penyewaan berdasarkan kondisi cuaca (tabel ringkas):")
    st.dataframe(avg_weather.rename(columns={"weathersit":"Weather Condition","cnt":"Average Rentals"}))

    fig, ax = plt.subplots(figsize=(8,5))
    order = ["Clear","Mist/Cloudy","Light Rain/Snow","Heavy Rain/Snow"]
    avg_weather = avg_weather.set_index("weathersit").loc[order].reset_index()
    ax.plot(avg_weather["weathersit"], avg_weather["cnt"], marker="o", linewidth=2, color="#1E90FF")
    ax.set_title("Rata-rata penyewaan sepeda berdasarkan kondisi cuaca")
    ax.set_xlabel("Weather Condition")
    ax.set_ylabel("Average Number of Rentals (cnt)")
    ax.grid(True, linestyle='--', alpha=0.5)
    draw(fig)

# =====================================================================
# 2) POLA WAKTU 2011 — HEATMAP JAM×HARI
# =====================================================================
elif analysis == "Pola Waktu 2011 ➜ Jam × Hari (Heatmap)":
    st.subheader("Pola Penyewaan Sepeda berdasarkan Jam dan Hari (2011)")
    hour_2011 = fdf[fdf["yr"] == 0].copy()  # 2011

    hourly_pattern = hour_2011.groupby(["weekday","hr"])["cnt"].mean().reset_index()
    hourly_pattern["weekday"] = hourly_pattern["weekday"].apply(lambda x: weekday_labels[int(x)%7])

    st.write("Contoh data rata-rata (top 10):")
    st.dataframe(hourly_pattern.head(10))

    pivot_hourly = hourly_pattern.pivot(index="weekday", columns="hr", values="cnt")
    pivot_hourly = pivot_hourly.reindex(index=weekday_labels)

    fig, ax = plt.subplots(figsize=(12,5))
    sns.heatmap(pivot_hourly, cmap="YlOrRd", linewidths=0.3, annot=False, ax=ax)
    ax.set_title("Pola Penyewaan Sepeda Berdasarkan Jam dan Hari (2011)", fontsize=13, weight='bold')
    ax.set_xlabel("Hours of the Day")
    ax.set_ylabel("Day of the Week")
    ax.tick_params(axis='x', labelrotation=0)
    ax.tick_params(axis='y', labelrotation=0)
    draw(fig)

# =====================================================================
# 2b) POLA BULANAN 2011 — BAR CHART
# =====================================================================
elif analysis == "Pola Bulanan 2011 ➜ Bar Chart":
    st.subheader("Rata-rata Penyewaan Sepeda per Bulan (2011)")
    hour_2011 = fdf[fdf["yr"] == 0].copy()

    monthly_pattern = hour_2011.groupby("mnth")["cnt"].mean().reset_index()
    monthly_pattern["mnth"] = monthly_pattern["mnth"].apply(lambda x: month_labels[int(x)-1])

    st.write("Rata-rata penyewaan per bulan (2011):")
    st.dataframe(monthly_pattern.rename(columns={"mnth":"Month","cnt":"Average Rentals"}))

    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(x="mnth", y="cnt", data=monthly_pattern, palette="YlGnBu", ax=ax)
    ax.set_title("Rata-rata Penyewaan Sepeda per Bulan (2011)", fontsize=13, weight='bold')
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Number of Rentals")
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    draw(fig)

# =====================================================================
# 3) TREN MUSIM 2011–2012 — AREA CHART SATU GARIS (AGREGAT)
# =====================================================================
elif analysis == "Tren Musim 2011–2012 ➜ Area Line":
    st.subheader("Rata-rata Penyewaan Sepeda Berdasarkan Musim (2011–2012)")
    season_pattern = fdf.groupby("season")["cnt"].mean().reset_index()
    season_pattern["season"] = season_pattern["season"].map(season_labels)

    st.write("Rata-rata penyewaan per musim (agregat 2011–2012):")
    st.dataframe(season_pattern.rename(columns={"season":"Season","cnt":"Average Rentals"}))

    order = ["Spring","Summer","Fall","Winter"]
    season_pattern = season_pattern.set_index("season").loc[order].reset_index()

    fig, ax = plt.subplots(figsize=(8,5))
    ax.fill_between(season_pattern["season"], season_pattern["cnt"], color="#FFA500", alpha=0.5)
    ax.plot(season_pattern["season"], season_pattern["cnt"], marker="o", color="#FF8C00", linewidth=2)
    ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Musim (2011–2012)", fontsize=13, weight='bold')
    ax.set_xlabel("Season")
    ax.set_ylabel("Average Number of Bike Rentals")
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    draw(fig)

# =====================================================================
# 4) RFM — 3 VISUAL (BAR H, SCATTER, HISTOGRAM)
# =====================================================================
elif analysis == "RFM ➜ (Recency Bar H, Scatter F–M, Histogram M)":
    st.subheader("Analisis Lanjutan: Pola Aktivitas Penyewaan (RFM)")

    # pastikan datetime
    fdf["dteday"] = pd.to_datetime(fdf["dteday"])
    latest_date = fdf["dteday"].max()
    fdf["recency"] = (latest_date - fdf["dteday"]).dt.days

    # Frequency & Monetary per bulan
    freq_per_month = fdf.groupby("mnth")["cnt"].count().reset_index()
    freq_per_month.columns = ["month", "frequency"]

    monetary_per_month = fdf.groupby("mnth")["cnt"].sum().reset_index()
    monetary_per_month.columns = ["month", "monetary"]

    rfm_df = freq_per_month.merge(monetary_per_month, on="month")
    rfm_df["recency"] = fdf.groupby("mnth")["recency"].min().values
    rfm_df["month"] = rfm_df["month"].apply(lambda x: month_labels[int(x)-1])

    st.write("Data gabungan hasil RFM (ringkas):")
    st.dataframe(rfm_df.head())

    # Recency by Season → horizontal bar
    season_map = {1:"Spring", 2:"Summer", 3:"Fall", 4:"Winter"}
    if "season_name" not in fdf.columns:
        fdf["season_name"] = fdf["season"].map(season_map)
    recency_by_season = fdf.groupby("season_name")["recency"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(y="season_name", x="recency", data=recency_by_season, palette="cool", ax=ax)
    ax.set_title("Rata-rata Hari Sejak Peminjaman Terakhir Berdasarkan Musim", fontsize=13, weight='bold')
    ax.set_xlabel("Rata-rata Hari Sejak Aktivitas Terakhir (Recency)")
    ax.set_ylabel("Musim")
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    draw(fig)

    # Scatter: Frequency vs Monetary (warna = bulan)
    fig, ax = plt.subplots(figsize=(9,6))
    scat = sns.scatterplot(
        data=rfm_df, x="frequency", y="monetary",
        hue="month", palette="viridis", s=120, edgecolor="white", linewidth=0.7, ax=ax
    )
    ax.set_title("Hubungan Frekuensi dan Total Penyewaan Sepeda per Bulan", fontsize=13, weight='bold')
    ax.set_xlabel("Frekuensi Penyewaan per Bulan")
    ax.set_ylabel("Total Jumlah Peminjaman Sepeda")
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(title="Bulan", bbox_to_anchor=(1.02, 1), loc="upper left")
    draw(fig)

    # Histogram Monetary
    fig, ax = plt.subplots(figsize=(9,5))
    sns.histplot(rfm_df["monetary"], bins=6, kde=True, color="#48C9B0", ax=ax)
    ax.set_title("Distribusi Total Penyewaan Sepeda per Bulan (Monetary)", fontsize=13, weight='bold')
    ax.set_xlabel("Total Penyewaan per Bulan")
    ax.set_ylabel("Frekuensi Bulan")
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    draw(fig)

# ------------------ Footer ------------------
st.divider()
st.caption("© 2025 — Dashboard Analisis Penyewaan Sepeda (Streamlit • pandas • seaborn • matplotlib)")
