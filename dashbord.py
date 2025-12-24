from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Dashboard Analisis Penyewaan Sepeda",
    page_icon="📊",
    layout="wide"
)
sns.set(style="whitegrid")

st.markdown(
    """
<style>
  .block-container {padding-top: 1rem; padding-bottom: .5rem;}
  [data-testid="stSidebar"] {background:#1f2530;}
  [data-testid="stSidebar"] * {color:#f0f2f6 !important;}

  /* Card */
  .insight-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px;
    padding: 14px 16px;
    color: #f9fafb;
  }
  .insight-title {font-size: 14px; opacity: .85; margin-bottom: 6px;}
  .insight-value {font-size: 22px; font-weight: 800; margin: 2px 0;}
  .insight-sub {font-size: 13px; opacity: .82;}
  .insight-good {color: #22c55e;}
  .insight-bad {color: #ef4444;}
  .insight-mid {color: #60a5fa;}

  /* Kesimpulan box (besar & jelas) */
  .conclusion-box{
    background:#0b1220;
    border:1px solid rgba(255,255,255,.10);
    border-radius:14px;
    padding:14px 16px;
    margin-top:12px;
    color:#f9fafb;
    font-size:16px;
    line-height:1.50;
  }
  .conclusion-title{
    font-weight:900;
    font-size:16px;
    margin-bottom:6px;
  }
</style>
""",
    unsafe_allow_html=True
)

# =========================================================
# UTILITIES
# =========================================================
def draw(fig):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

def safe_date_range(val):
    if isinstance(val, (list, tuple)) and len(val) == 2:
        return pd.to_datetime(val[0]), pd.to_datetime(val[1])
    return pd.to_datetime(val), pd.to_datetime(val)

def pretty_int(x):
    try:
        return f"{float(x):.0f}"
    except:
        return str(x)

def pretty_float(x, nd=1):
    try:
        return f"{float(x):.{nd}f}"
    except:
        return str(x)

def show_insight_cards(
    peak_label, peak_value,
    low_label, low_value,
    gap_label, gap_value,
    conclusion_html=""
):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
<div class="insight-card">
  <div class="insight-title">⬆️ Tertinggi</div>
  <div class="insight-value insight-good">{peak_label}</div>
  <div class="insight-sub">{peak_value}</div>
</div>
""",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
<div class="insight-card">
  <div class="insight-title">⬇️ Terendah</div>
  <div class="insight-value insight-bad">{low_label}</div>
  <div class="insight-sub">{low_value}</div>
</div>
""",
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
<div class="insight-card">
  <div class="insight-title">↔️ Selisih</div>
  <div class="insight-value insight-mid">{gap_label}</div>
  <div class="insight-sub">{gap_value}</div>
</div>
""",
            unsafe_allow_html=True
        )

    if conclusion_html:
        st.markdown(
            f"""
<div class="conclusion-box">
  <div class="conclusion-title">Kesimpulan</div>
  {conclusion_html}
</div>
""",
            unsafe_allow_html=True
        )

def highlight_best_worst(df, value_col):
    def _style(s):
        is_max = s == s.max()
        is_min = s == s.min()
        out = []
        for v, w in zip(is_max, is_min):
            if v:
                out.append("background-color: rgba(34,197,94,.22); font-weight:800;")
            elif w:
                out.append("background-color: rgba(239,68,68,.22); font-weight:800;")
            else:
                out.append("")
        return out
    return df.style.apply(_style, subset=[value_col])

# =========================================================
# LOAD DATA
# =========================================================
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

if "dteday" not in df.columns:
    st.error("Kolom 'dteday' tidak ada di dataset.")
    st.stop()

df["dteday"] = pd.to_datetime(df["dteday"])

# Label
weather_label = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
weekday_labels = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
month_labels   = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
season_labels  = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}

if "weathersit" in df.columns:
    df["weather_name"] = df["weathersit"].map(weather_label)
if "weekday" in df.columns:
    df["weekday_name"] = df["weekday"].apply(lambda x: weekday_labels[int(x) % 7])
if "mnth" in df.columns:
    df["month_name"] = df["mnth"].apply(lambda x: month_labels[int(x) - 1])
if "season" in df.columns:
    df["season_name"] = df["season"].map(season_labels)

# =========================================================
# SIDEBAR
# =========================================================
img_candidates = [
    BASE / "penyewaan_sepeda.jpg",
    BASE / "assets" / "penyewaan_sepeda.jpg",
    Path(r"C:\Users\vivob\dashbord\penyewaan_sepeda.jpg"),
]
img_path = next((p for p in img_candidates if p.exists()), None)

if img_path:
    st.sidebar.image(str(img_path), use_container_width=True)
else:
    st.sidebar.image(
        "https://em-content.zobj.net/source/microsoft-teams/363/bicycle_1f6b2.png",
        width=100
    )

st.sidebar.markdown("## Bike Sharing Dashboard")

min_d, max_d = df["dteday"].min(), df["dteday"].max()

date_rng = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=(min_d.date(), max_d.date()),
    min_value=min_d.date(),
    max_value=max_d.date()
)
start_d, end_d = safe_date_range(date_rng)

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

# =========================================================
# HEADER
# =========================================================
st.markdown("# 📊 Dashboard Analisis Penyewaan Sepeda")
st.caption(f"Data range: {start_d.date()} to {end_d.date()}")

# =========================================================
# 1) CUACA — LINE
# =========================================================
if analysis == "Cuaca ➜ Rata-rata Penyewaan (Line)":
    st.subheader("Rata-rata Penyewaan per Kondisi Cuaca")

    avg_weather = fdf.groupby("weathersit")["cnt"].mean().reset_index()
    avg_weather["weather"] = avg_weather["weathersit"].map(weather_label)

    order = ["Clear", "Mist/Cloudy", "Light Rain/Snow", "Heavy Rain/Snow"]
    plot_df = avg_weather.set_index("weather").reindex(order).reset_index()

    st.write("Rata-rata penyewaan berdasarkan kondisi cuaca (tabel):")
    table_df = plot_df[["weather", "cnt"]].rename(columns={"weather": "Kondisi Cuaca", "cnt": "Rata-rata Penyewaan"})
    st.dataframe(highlight_best_worst(table_df, "Rata-rata Penyewaan"), use_container_width=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(plot_df["weather"], plot_df["cnt"], marker="o", linewidth=2, color="#1E90FF")
    ax.set_title("Rata-rata penyewaan sepeda berdasarkan kondisi cuaca")
    ax.set_xlabel("Kondisi Cuaca")
    ax.set_ylabel("Rata-rata Jumlah Penyewaan (cnt)")
    ax.grid(True, linestyle="--", alpha=0.5)
    draw(fig)

    max_row = plot_df.loc[plot_df["cnt"].idxmax()]
    min_row = plot_df.loc[plot_df["cnt"].idxmin()]
    gap = float(max_row["cnt"] - min_row["cnt"])

    show_insight_cards(
        peak_label=str(max_row["weather"]),
        peak_value=f"≈ {pretty_int(max_row['cnt'])} penyewaan",
        low_label=str(min_row["weather"]),
        low_value=f"≈ {pretty_int(min_row['cnt'])} penyewaan",
        gap_label=f"≈ {pretty_int(gap)}",
        gap_value="selisih rata-rata",
        conclusion_html=(
            f"Rata-rata penyewaan tertinggi terjadi saat cuaca <b>{max_row['weather']}</b>, "
            f"dan terendah saat cuaca <b>{min_row['weather']}</b>."
        )
    )

# =========================================================
# 2) POLA WAKTU 2011 — TABEL → HEATMAP → KESIMPULAN
# =========================================================
elif analysis == "Pola Waktu 2011 ➜ Jam × Hari (Heatmap)":
    st.subheader("Pola Penyewaan Sepeda berdasarkan Jam dan Hari (2011)")

    hour_2011 = fdf[fdf["yr"] == 0].copy()
    if hour_2011.empty:
        st.warning("Data 2011 tidak ada pada rentang tanggal yang dipilih.")
        st.stop()

    hourly_pattern = hour_2011.groupby(["weekday", "hr"])["cnt"].mean().reset_index()
    hourly_pattern["weekday_name"] = hourly_pattern["weekday"].apply(lambda x: weekday_labels[int(x) % 7])

    st.write("Tabel ringkas pola penyewaan (2011):")

    top_hours = hourly_pattern.groupby("hr")["cnt"].mean().reset_index().sort_values("cnt", ascending=False).head(3)
    top_hours["Jam"] = top_hours["hr"].astype(int)
    top_hours["Rata-rata Penyewaan"] = top_hours["cnt"].round(1)
    top_hours = top_hours[["Jam", "Rata-rata Penyewaan"]]

    top_days = hourly_pattern.groupby("weekday_name")["cnt"].mean().reset_index().sort_values("cnt", ascending=False).head(3)
    top_days["Rata-rata Penyewaan"] = top_days["cnt"].round(1)
    top_days = top_days.rename(columns={"weekday_name": "Hari"})[["Hari", "Rata-rata Penyewaan"]]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Top 3 Jam Paling Ramai**")
        st.dataframe(top_hours, use_container_width=True)
    with c2:
        st.markdown("**Top 3 Hari Paling Ramai**")
        st.dataframe(top_days, use_container_width=True)

    peak_per_day = hourly_pattern.loc[hourly_pattern.groupby("weekday_name")["cnt"].idxmax()].copy()
    peak_per_day = peak_per_day[["weekday_name", "hr", "cnt"]].rename(
        columns={"weekday_name": "Hari", "hr": "Jam Puncak", "cnt": "Rata-rata Penyewaan"}
    )
    peak_per_day["Jam Puncak"] = peak_per_day["Jam Puncak"].astype(int)
    peak_per_day["Rata-rata Penyewaan"] = peak_per_day["Rata-rata Penyewaan"].round(1)
    peak_per_day = peak_per_day.set_index("Hari").reindex(weekday_labels).reset_index()

    st.markdown("**Jam Puncak di Setiap Hari**")
    st.dataframe(peak_per_day, use_container_width=True)

    st.divider()

    pivot_hourly = hourly_pattern.pivot(index="weekday_name", columns="hr", values="cnt")
    pivot_hourly = pivot_hourly.reindex(index=weekday_labels)

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(pivot_hourly, cmap="YlOrRd", linewidths=0.3, annot=False, ax=ax)
    ax.set_title("Heatmap Penyewaan Sepeda (Jam × Hari) Tahun 2011", fontsize=13, weight="bold")
    ax.set_xlabel("Jam (0–23)")
    ax.set_ylabel("Hari")
    ax.tick_params(axis="x", labelrotation=0)
    ax.tick_params(axis="y", labelrotation=0)
    draw(fig)

    peak_combo = hourly_pattern.loc[hourly_pattern["cnt"].idxmax()]
    peak_hour = int(top_hours.iloc[0]["Jam"])
    peak_hour_val = float(top_hours.iloc[0]["Rata-rata Penyewaan"])
    peak_day = str(top_days.iloc[0]["Hari"])
    peak_day_val = float(top_days.iloc[0]["Rata-rata Penyewaan"])

    show_insight_cards(
        peak_label=f"{peak_combo['weekday_name']} (jam {int(peak_combo['hr'])})",
        peak_value=f"≈ {pretty_int(peak_combo['cnt'])} rata-rata",
        low_label=f"{peak_day}",
        low_value=f"≈ {pretty_int(peak_day_val)} rata-rata per hari",
        gap_label=f"Jam {peak_hour}",
        gap_value=f"≈ {pretty_int(peak_hour_val)} rata-rata",
        conclusion_html=(
            f"Penyewaan cenderung memuncak pada jam tertentu dan berbeda antar hari. "
            f"Kombinasi paling ramai terjadi pada <b>{peak_combo['weekday_name']}</b> di <b>jam {int(peak_combo['hr'])}</b>."
        )
    )

# =========================================================
# 2b) BULANAN 2011 — BAR
# =========================================================
elif analysis == "Pola Bulanan 2011 ➜ Bar Chart":
    st.subheader("Rata-rata Penyewaan Sepeda per Bulan (2011)")

    hour_2011 = fdf[fdf["yr"] == 0].copy()
    if hour_2011.empty:
        st.warning("Data 2011 tidak ada pada rentang tanggal yang dipilih.")
        st.stop()

    monthly_pattern = hour_2011.groupby("mnth")["cnt"].mean().reset_index()
    monthly_pattern["Bulan"] = monthly_pattern["mnth"].apply(lambda x: month_labels[int(x) - 1])

    st.write("Rata-rata penyewaan per bulan (tabel):")
    table_df = monthly_pattern[["Bulan", "cnt"]].rename(columns={"cnt": "Rata-rata Penyewaan"})
    st.dataframe(highlight_best_worst(table_df, "Rata-rata Penyewaan"), use_container_width=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x="Bulan", y="cnt", data=monthly_pattern, palette="YlGnBu", ax=ax)
    ax.set_title("Rata-rata Penyewaan Sepeda per Bulan (2011)", fontsize=13, weight="bold")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Rata-rata Jumlah Penyewaan")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    draw(fig)

    peak = monthly_pattern.loc[monthly_pattern["cnt"].idxmax()]
    low  = monthly_pattern.loc[monthly_pattern["cnt"].idxmin()]
    gap  = float(peak["cnt"] - low["cnt"])

    show_insight_cards(
        peak_label=str(peak["Bulan"]),
        peak_value=f"≈ {pretty_int(peak['cnt'])} rata-rata",
        low_label=str(low["Bulan"]),
        low_value=f"≈ {pretty_int(low['cnt'])} rata-rata",
        gap_label=f"≈ {pretty_int(gap)}",
        gap_value="selisih rata-rata",
        conclusion_html=(
            f"Bulan teramai adalah <b>{peak['Bulan']}</b>, sedangkan bulan tersepi adalah <b>{low['Bulan']}</b>."
        )
    )

# =========================================================
# 3) MUSIM 2011–2012 — AREA
# =========================================================
elif analysis == "Tren Musim 2011–2012 ➜ Area Line":
    st.subheader("Rata-rata Penyewaan Sepeda Berdasarkan Musim (2011–2012)")

    season_pattern = fdf.groupby("season")["cnt"].mean().reset_index()
    season_pattern["Musim"] = season_pattern["season"].map(season_labels)

    order = ["Spring", "Summer", "Fall", "Winter"]
    plot_df = season_pattern.set_index("Musim").reindex(order).reset_index()

    st.write("Rata-rata penyewaan per musim (tabel):")
    table_df = plot_df[["Musim", "cnt"]].rename(columns={"cnt": "Rata-rata Penyewaan"})
    st.dataframe(highlight_best_worst(table_df, "Rata-rata Penyewaan"), use_container_width=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(plot_df["Musim"], plot_df["cnt"], color="#FFA500", alpha=0.5)
    ax.plot(plot_df["Musim"], plot_df["cnt"], marker="o", color="#FF8C00", linewidth=2)
    ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Musim (2011–2012)", fontsize=13, weight="bold")
    ax.set_xlabel("Musim")
    ax.set_ylabel("Rata-rata Jumlah Penyewaan")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    draw(fig)

    peak = plot_df.loc[plot_df["cnt"].idxmax()]
    low  = plot_df.loc[plot_df["cnt"].idxmin()]
    gap  = float(peak["cnt"] - low["cnt"])

    show_insight_cards(
        peak_label=str(peak["Musim"]),
        peak_value=f"≈ {pretty_int(peak['cnt'])} rata-rata",
        low_label=str(low["Musim"]),
        low_value=f"≈ {pretty_int(low['cnt'])} rata-rata",
        gap_label=f"≈ {pretty_int(gap)}",
        gap_value="selisih rata-rata",
        conclusion_html=(
            f"Musim paling ramai adalah <b>{peak['Musim']}</b>, sedangkan paling rendah adalah <b>{low['Musim']}</b>."
        )
    )

# =========================================================
# 4) RFM — dengan kotak-kotak kesimpulan
# =========================================================
elif analysis == "RFM ➜ (Recency Bar H, Scatter F–M, Histogram M)":
    st.subheader("Analisis RFM")

    st.markdown(
        """
RFM digunakan untuk melihat pola aktivitas penyewaan:
- **Recency**: jarak hari sejak aktivitas terakhir (lebih kecil = lebih baru)
- **Frequency**: seberapa sering penyewaan terjadi
- **Monetary**: total jumlah penyewaan (akumulasi cnt)

Catatan: pada proyek ini RFM dihitung berdasarkan agregasi waktu (per bulan), karena dataset tidak memiliki ID pelanggan.
"""
    )

    latest_date = fdf["dteday"].max()
    fdf["recency"] = (latest_date - fdf["dteday"]).dt.days

    # Frequency & Monetary per bulan
    freq_per_month = fdf.groupby("mnth")["cnt"].count().reset_index()
    freq_per_month.columns = ["month", "frequency"]

    monetary_per_month = fdf.groupby("mnth")["cnt"].sum().reset_index()
    monetary_per_month.columns = ["month", "monetary"]

    rfm_df = freq_per_month.merge(monetary_per_month, on="month")
    rfm_df["recency"] = fdf.groupby("mnth")["recency"].min().values
    rfm_df["Bulan"] = rfm_df["month"].apply(lambda x: month_labels[int(x) - 1])

    st.write("Data ringkas RFM per bulan (tabel):")
    st.dataframe(rfm_df[["Bulan", "recency", "frequency", "monetary"]], use_container_width=True)

    st.divider()

    # A) Recency per season
    st.markdown("### A. Recency per Musim")
    recency_by_season = fdf.groupby("season_name")["recency"].mean().reset_index()
    order_season = ["Spring", "Summer", "Fall", "Winter"]
    recency_by_season = recency_by_season.set_index("season_name").reindex(order_season).reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(y="season_name", x="recency", data=recency_by_season, palette="cool", ax=ax)
    ax.set_title("Rata-rata Recency per Musim", fontsize=13, weight="bold")
    ax.set_xlabel("Rata-rata hari sejak aktivitas terakhir")
    ax.set_ylabel("Musim")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    draw(fig)

    best_s = recency_by_season.loc[recency_by_season["recency"].idxmin()]
    worst_s = recency_by_season.loc[recency_by_season["recency"].idxmax()]
    gap_r = float(worst_s["recency"] - best_s["recency"])

    show_insight_cards(
        peak_label=str(best_s["season_name"]),
        peak_value=f"Recency ≈ {pretty_int(best_s['recency'])} hari (paling baru)",
        low_label=str(worst_s["season_name"]),
        low_value=f"Recency ≈ {pretty_int(worst_s['recency'])} hari (paling lama)",
        gap_label=f"≈ {pretty_int(gap_r)} hari",
        gap_value="selisih recency",
        conclusion_html=(
            f"Musim <b>{best_s['season_name']}</b> menunjukkan aktivitas penyewaan yang lebih baru "
            f"(recency lebih kecil), dibandingkan musim <b>{worst_s['season_name']}</b>."
        )
    )

    st.divider()

    # B) Scatter Frequency vs Monetary
    st.markdown("### B. Frequency vs Monetary per Bulan")
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.scatterplot(
        data=rfm_df, x="frequency", y="monetary",
        hue="Bulan", palette="viridis",
        s=120, edgecolor="white", linewidth=0.7, ax=ax
    )
    ax.set_title("Hubungan Frequency dan Monetary per Bulan", fontsize=13, weight="bold")
    ax.set_xlabel("Frequency (jumlah catatan penyewaan)")
    ax.set_ylabel("Monetary (total penyewaan)")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(title="Bulan", bbox_to_anchor=(1.02, 1), loc="upper left")
    draw(fig)

    corr_fm = rfm_df["frequency"].corr(rfm_df["monetary"]) if len(rfm_df) > 2 else np.nan

    max_m = rfm_df.loc[rfm_df["monetary"].idxmax()]
    min_m = rfm_df.loc[rfm_df["monetary"].idxmin()]
    gap_m = float(max_m["monetary"] - min_m["monetary"])

    show_insight_cards(
        peak_label=str(max_m["Bulan"]),
        peak_value=f"Monetary ≈ {pretty_int(max_m['monetary'])}",
        low_label=str(min_m["Bulan"]),
        low_value=f"Monetary ≈ {pretty_int(min_m['monetary'])}",
        gap_label=f"≈ {pretty_int(gap_m)}",
        gap_value="selisih total",
        conclusion_html=(
            f"Secara umum, semakin tinggi frequency biasanya diikuti total penyewaan (monetary) yang lebih besar. "
            f"Nilai hubungan sederhana (korelasi) ≈ <b>{pretty_float(corr_fm, 3)}</b>."
        )
    )

    st.divider()

    # C) Histogram Monetary
    st.markdown("### C. Distribusi Monetary per Bulan")
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(rfm_df["monetary"], bins=6, kde=True, color="#48C9B0", ax=ax)
    ax.set_title("Distribusi Monetary (Total Penyewaan) per Bulan", fontsize=13, weight="bold")
    ax.set_xlabel("Total penyewaan per bulan")
    ax.set_ylabel("Jumlah bulan")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    draw(fig)

    med = float(rfm_df["monetary"].median())
    q1 = float(rfm_df["monetary"].quantile(0.25))
    q3 = float(rfm_df["monetary"].quantile(0.75))

    show_insight_cards(
        peak_label=f"Q3 ≈ {pretty_int(q3)}",
        peak_value="batas atas (25% bulan teratas)",
        low_label=f"Q1 ≈ {pretty_int(q1)}",
        low_value="batas bawah (25% bulan terbawah)",
        gap_label=f"Median ≈ {pretty_int(med)}",
        gap_value="nilai tengah",
        conclusion_html=(
            f"Sebagian besar bulan berada di sekitar median. Bulan yang jauh di atas Q3 dapat dianggap sebagai "
            f"periode yang lebih ramai dibandingkan bulan lainnya."
        )
    )

# =========================================================
# FOOTER
# =========================================================
st.divider()
st.caption("© 2025 — Dashboard Analisis Penyewaan Sepeda (Streamlit • pandas • seaborn • matplotlib)")
