# 📊 Dashboard Analisis Penyewaan Sepeda
Dashboard ini dikembangkan menggunakan **Streamlit** untuk menganalisis dataset **Bike Sharing** (penyewaan sepeda) yang disediakan pada modul *Analisis Data dengan Python*. Dataset yang digunakan adalah **hour_df**, berisi aktivitas penyewaan sepeda berdasarkan waktu, cuaca, dan musim.

## 🧩 Deskripsi Proyek
Tujuan utama dashboard ini adalah untuk:
- Mengetahui pengaruh **cuaca** terhadap tingkat penyewaan sepeda.  
- Menganalisis **pola waktu** penyewaan berdasarkan jam, hari, dan bulan.  
- Melihat **tren penyewaan** pada setiap musim (Spring–Winter).  
- Melakukan **analisis lanjutan (RFM)** untuk memahami perilaku peminjaman pengguna.

## ⚙️ Proses Analisis Data
Tahapan analisis dilakukan mulai dari pengumpulan hingga eksplorasi data, seluruhnya digabung menjadi satu alur agar efisien dan mudah dipahami.

```python
# Import dan Baca Dataset
import pandas as pd
hour_df = pd.read_csv("hour_cleaned.csv")

# Pemeriksaan Awal (Assessing)
print(hour_df.info())
print(hour_df.isnull().sum())
print(hour_df.duplicated().sum())

# Pembersihan Data (Cleaning)
hour_df.dropna(inplace=True)
hour_df.drop_duplicates(inplace=True)
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

# Eksplorasi Awal (EDA)
print(hour_df.describe())
print(hour_df.head())
```
Hasil tahapan ini memastikan data telah bersih dari nilai kosong dan duplikasi, serta siap digunakan dalam analisis visual. Setelah data siap, dilakukan analisis menggunakan berbagai jenis visualisasi untuk menjawab pertanyaan penelitian yang telah ditentukan.

## 📈 Jenis Analisis dan Visualisasi
| No | Pertanyaan Analisis | Jenis Visualisasi | Tujuan Visualisasi |
|----|----------------------|-------------------|--------------------|
| 1 | Bagaimana cuaca memengaruhi penyewaan sepeda? | Line Chart | Melihat pengaruh kondisi cuaca terhadap rata-rata penyewaan. |
| 2 | Bagaimana pola penyewaan berdasarkan jam dan hari selama 2011? | Heatmap | Menunjukkan intensitas aktivitas penyewaan berdasarkan waktu. |
| 3 | Bagaimana pola penyewaan bulanan pada tahun 2011? | Bar Chart | Menampilkan tren penyewaan sepeda tiap bulan. |
| 4 | Bagaimana tren penyewaan sepeda pada setiap musim (2011–2012)? | Area Chart | Menunjukkan perubahan rata-rata penyewaan di tiap musim. |
| 5 | Bagaimana perilaku pengguna berdasarkan RFM? | Bar Chart, Scatter Plot, Histogram | Menjelaskan hubungan antara Recency, Frequency, dan Monetary. |

## 💻 Instalasi dan Persiapan Lingkungan
Langkah-langkah berikut dilakukan agar dashboard dapat dijalankan dengan baik di perangkat lokal:

1️⃣ **Buat Virtual Environment**
```bash
py -m venv venv
Set-ExecutionPolicy Unrestricted -Scope Process
venv\Scripts\activate
```

2️⃣ **Instalasi Library yang Dibutuhkan**
```bash
pip install streamlit pandas numpy matplotlib seaborn
```

3️⃣ **Struktur Folder Proyek**
```
📂 dashbord/
 ├── dashbord.py
 ├── hour_cleaned.csv
 └── penyewaan_sepeda.jpg
```

4️⃣ **Menjalankan Dashboard**
```bash
streamlit run dashbord.py
```

Akses hasilnya melalui browser:  
**Local URL:** http://localhost:8501  
**Network URL:** http://192.168.x.x:8501 *(tergantung IP lokal)*

## 🔍 Fitur Analisis dalam Dashboard
1️⃣ **Cuaca ➜ Rata-rata Penyewaan (Line Chart)** – Menampilkan rata-rata penyewaan berdasarkan kondisi cuaca — cerah, mendung, hujan ringan, hingga hujan lebat/salju.  
2️⃣ **Pola Waktu 2011 ➜ Jam × Hari (Heatmap)** – Memperlihatkan aktivitas peminjaman berdasarkan kombinasi jam dan hari dalam seminggu.  
3️⃣ **Pola Bulanan 2011 ➜ Bar Chart** – Menunjukkan rata-rata peminjaman tiap bulan selama tahun 2011.  
4️⃣ **Tren Musim 2011–2012 ➜ Area Chart** – Menggambarkan tren penyewaan sepeda pada setiap musim (Spring, Summer, Fall, Winter).  
5️⃣ **Analisis RFM ➜ Bar Chart, Scatter Plot, Histogram**
- *Recency:* Rata-rata hari sejak peminjaman terakhir per musim.  
- *Frequency:* Frekuensi peminjaman sepeda per bulan.  
- *Monetary:* Total jumlah peminjaman per bulan.  

## 📊 Hasil Analisis (Insight Utama)
- Kondisi **cuaca cerah** menunjukkan tingkat penyewaan tertinggi dibanding cuaca lainnya.  
- Aktivitas penyewaan meningkat pada **jam sore (16.00–18.00)** dan hari kerja.  
- **Bulan Agustus** memiliki jumlah peminjaman tertinggi, sedangkan **Januari** terendah.  
- Pada skala musim, **Summer (musim panas)** menjadi puncak aktivitas penyewaan.  
- Berdasarkan hasil **RFM Analysis**, pengguna aktif cenderung memiliki frekuensi tinggi dan total penyewaan besar setiap bulan.  
- Secara keseluruhan, pola penggunaan sepeda menunjukkan ketergantungan kuat terhadap faktor **cuaca, waktu, dan musim**.

## 👩‍💻 Pengembang
**Nama:** Ratna Sari  
**Program Studi:** Sistem & Teknologi Informasi  
**Universitas:** Universitas Ivet Semarang  
**Tahun:** 2025  

📎 *Dibuat menggunakan Python, Pandas, Seaborn, Matplotlib, dan Streamlit.*
