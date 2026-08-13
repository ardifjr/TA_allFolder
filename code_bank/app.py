import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os
import glob

# Konfigurasi Halaman Web
st.set_page_config(page_title="Pusat Visualisasi Bab 3", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size:28px; font-weight:bold; color:#1E3A8A; margin-bottom:20px; }
    .section-title { font-size:22px; font-weight:bold; color:#2563EB; margin-top:30px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">🎯 Pusat Visualisasi & Manajemen Aset Gambar - Bab III</div>', unsafe_allow_html=True)

# ==========================================
# DEFINISI DIREKTORI UTAMA (RIIL DATA)
# ==========================================
PATH_PREPROCESSED = r'E:\Semester 7\TA\code_bank\preprocesing\standardized_data'
PATH_CLUSTERING   = r'E:\Semester 7\TA\code_bank\clustering'
PATH_EVALUATION   = r'E:\Semester 7\TA\code_bank\evaluation'

# Daftar 26 Ticker yang Lolos Seleksi Irisan Sektoral
TICKERS_BASELINE = [
    "BACA", "BBCA", "BBHI", "BBMD", "BBNI", "BBRI",
    "BBTN", "BDMN", "BINA", "BJBR", "BJTM", "BMRI",
    "BNGA", "BNII", "BNLI", "BRIS", "BSIM", "BTPN", "BTPS", "BVIC",
    "INPC", "MCOR", "MEGA", "NISP", "NOBU", "PNBN"
]

# ==========================================
# FUNCTION DOWNLOAD HIGH RES (300 DPI)
# ==========================================
def hitung_dan_export_300dpi(fig_plt, nama_file="plot.png"):
    buf = io.BytesIO()
    fig_plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    st.download_button(
        label=f"📥 Download {nama_file} (300 DPI)",
        data=buf,
        file_name=nama_file,
        mime="image/png"
    )

# ==========================================
# KONTROL PANEL (SIDEBAR)
# ==========================================
st.sidebar.header("⚙️ Kontrol Panel Data")
menu_select = st.sidebar.radio(
    "Pilih Sub-bab Analisis:",
    ["A. Standardisasi & Pivot Points", 
     "B. Implementasi K-Means & Centroid", 
     "C. Pemetaan Zona Rentang Dinamis", 
     "D. Evaluasi Performa Model"]
)

ticker_aktif = st.sidebar.selectbox("Pilih Emiten:", TICKERS_BASELINE)

def gambarkan_diagram_seleksi_emiten():
    # Definisikan tahapan seleksi
    tahapan = [
        "Seluruh Emiten Sektor Energi\ndi BEI (IDX)", 
        "Penyaringan Kelayakan Data\n(Kelengkapan Historis)", 
        "Seleksi Kecukupan Pivot Points\nUntuk Variasi K=2 s/d K=10\n(Konsistensi Klasterisasi)"
    ]
    # Representasi jumlah emiten fiktif/perkiraan sebelum dikerucutkan ke 26 emiten lolos
    jumlah_emiten = [45, 34, 26] 
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Membuat diagram berbentuk corong/blok panah ke bawah
    y_pos = np.arange(len(tahapan))
    colors = ["#1E3A8A", "#2563EB", "#10B981"] # Biru Tua -> Biru Muda -> Hijau (Lolos)
    
    # Gambar kotak proses
    bars = ax.barh(y_pos, jumlah_emiten, align='center', color=colors, alpha=0.85, height=0.5, edgecolor='black')
    
    # Menambahkan teks label di dalam/samping balok
    for bar, teks, nilai in zip(bars, tahapan, jumlah_emiten):
        width = bar.get_width()
        ax.text(width / 2, bar.get_y() + bar.get_height()/2, f"{nilai} Emiten", 
                va='center', ha='center', color='white', fontweight='bold', fontsize=10)
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, teks, 
                va='center', ha='left', color='black', fontsize=9, fontweight='semibold')
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels([]) # Hilangkan tik standar
    ax.set_xlabel("Jumlah Emiten")
    ax.set_title("Alur Tahapan Penyaringan Irisan Sektoral Emiten Energi", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlim(0, 60)
    ax.invert_yaxis()  # Supaya urutan dari atas ke bawah
    ax.grid(axis='x', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    return fig

def gambarkan_komparasi_zscore_timeline(df_raw, ticker):
    # Buat subplot 1 baris, 2 kolom bersisian
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    
    # Filter data khusus untuk titik pivot (Support & Resistance) agar grafik tidak padat
    df_pivot = df_raw[df_raw['Type'].isin(['Support', 'Resistance'])].copy()
    if df_pivot.empty:
        df_pivot = df_raw.copy()
        
    # Pastikan kolom Tanggal bertipe datetime
    df_pivot['Tanggal'] = pd.to_datetime(df_pivot['Tanggal'])
    
    # Pisahkan data Support dan Resistance untuk membedakan warna seperti grafik harianmu
    df_high = df_pivot[df_pivot['Type'] == 'Resistance']
    df_low = df_pivot[df_pivot['Type'] == 'Support']
    
    # ----------------------------------------------------
    # KIRI: SEBELUM STANDARDISASI (X = HARGA RIIL, Y = TANGGAL)
    # ----------------------------------------------------
    ax1.scatter(df_high["Level"], df_high["Tanggal"], color="red", alpha=0.7, edgecolors='k', s=45, label="Pivot High (R)")
    ax1.scatter(df_low["Level"], df_low["Tanggal"], color="green", alpha=0.7, edgecolors='k', s=45, label="Pivot Low (S)")
    
    ax1.set_title(f"Original Data - {ticker} (Sebelum Standaridisasi)", fontsize=11, fontweight='bold')
    ax1.set_xlabel("Nominal Harga Saham Riil (Rupiah)", fontweight='semibold')
    ax1.set_ylabel("Rentang Tanggal Historis", fontweight='semibold')
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper right")
    
    # ----------------------------------------------------
    # KANAN: SESUDAH STANDARDISASI (X = Z-SCORE, Y = TANGGAL)
    # ----------------------------------------------------
    ax2.scatter(df_high["Z_Score"], df_high["Tanggal"], color="red", alpha=0.7, edgecolors='k', s=45, label="Pivot High (R)")
    ax2.scatter(df_low["Z_Score"], df_low["Tanggal"], color="green", alpha=0.7, edgecolors='k', s=45, label="Pivot Low (S)")
    
    # Garis bantu vertikal di Z-Score = 0 (Mean)
    ax2.axvline(0, color="purple", linestyle="--", alpha=0.7, label="Mean = 0")
    
    # Batasan Sumbu X dari -3 sampai 3 sesuai kebutuhan klasterisasi
    ax2.set_xlim(-3.5, 3.5)
    ax2.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    
    ax2.set_title("Standardized Data (Sesudah Z-Score)", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Skala Nilai Transformasi Z-Score", fontweight='semibold')
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper right")
    
    plt.suptitle(f"Gambar 3.2: Perbandingan Distribusi Titik Pivot {ticker} Berdasarkan Garis Waktu", fontsize=12, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    return fig

def gambarkan_variasi_k_inertia(df_cluster, ticker, k_val):
    """ Fungsi untuk Gambar 3.3: Menampilkan data titik pivot dalam runut waktu (Y=Tanggal/Bulan)
        terhadap skala Z-Score (X=Skala) dengan urutan warna kelompok yang KONSISTEN dan KONTRAS """
    import matplotlib.patches as patches
    fig, ax = plt.subplots(figsize=(8, 5.5))
    
    # Ambil data khusus untuk titik pivot (Support & Resistance)
    df_pivot = df_cluster[df_cluster['Type'].isin(['Support', 'Resistance'])].copy()
    if df_pivot.empty:
        df_pivot = df_cluster.copy()
        
    # Pastikan kolom Tanggal bertipe datetime
    df_pivot['Tanggal'] = pd.to_datetime(df_pivot['Tanggal'])
    df_pivot = df_pivot.sort_values('Tanggal')
    
    x_data = df_pivot["Z_Score"].values
    y_data = df_pivot["Tanggal"].values
    cluster_labels = df_pivot["Cluster"].values
    
    # PALET WARNA KONSISTEN & KONTRAS (Kunci dari Kelompok 1 s/d 10)
    # Memakai warna-warna tegas HEX agar kontrasnya terjaga dan tidak membingungkan
    WARNA_KONSISTEN = [
        "#1E3A8A", # 1. Biru Tua
        "#10B981", # 2. Hijau Emerald
        "#F59E0B", # 3. Oranye Kuning
        "#EF4444", # 4. Merah Terang
        "#8B5CF6", # 5. Ungu Murni
        "#EC4899", # 6. Pink Merona
        "#06B6D4", # 7. Cyan/Biru Langit
        "#6B7280", # 8. Abu-abu Gelap
        "#78350F", # 9. Cokelat Tanah
        "#111827"  # 10. Hitam Arang
    ]
    
    # 1. Plot titik data dan highlight area secara konsisten berurutan
    for c in range(k_val):
        mask = cluster_labels == c
        if np.any(mask):
            warna_aktif = WARNA_KONSISTEN[c]
            
            # Scatter plot titik data anggota klaster
            ax.scatter(x_data[mask], y_data[mask], 
                       color=warna_aktif, alpha=0.85, edgecolors='black', linewidths=0.7, s=55, 
                       label=f"Kelompok {c+1}", zorder=3)
            
            # 2. Tambahkan HIGHLIGHT AREA (Kotak Arsiran) dengan warna yang identik tapi sangat transparan (alpha=0.07)
            min_date, max_date = np.min(y_data), np.max(y_data)
            min_x, max_x = np.min(x_data[mask]), np.max(x_data[mask])
            
            # Kotak pembatas wilayah spasial klaster ke-c
            rect = patches.Rectangle(
                (min_x - 0.08, min_date), 
                (max_x - min_x + 0.16), 
                (max_date - min_date), 
                linewidth=1.2, 
                linestyle='--', 
                edgecolor=warna_aktif, 
                facecolor=warna_aktif, 
                alpha=0.07,  # Dibuat tipis agar jika ada overlay/irisan tipis tetap kontras dan bersih
                zorder=1
            )
            ax.add_patch(rect)
    
    # Atur tampilan layout grid dan batasan sumbu
    ax.set_title(f"Visualisasi Pembagian Kluster Titik Pivot (K={k_val})", fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Skala Nilai Fitur Hasil Standardisasi Z-Score", fontweight='semibold')
    ax.set_ylabel("Rentang Tanggal History", fontweight='semibold')
    
    ax.set_xlim(-3.5, 3.5)
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    
    ax.grid(True, linestyle=":", alpha=0.5)
    
    # Tempatkan legend di luar kanan grafik agar rapi dan tidak menutupi data harian
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), title="Daftar Kelompok", title_fontproperties={'weight':'bold'})
    
    plt.tight_layout()
    return fig

def gambarkan_sebaran_dan_centroid(df_cluster, ticker, k_val):
    """ Fungsi untuk Gambar 3.4: Menampilkan sebaran data Pivot Points pada garis waktu (Y=Tanggal)
        terhadap skala Z-Score (X) lengkap dengan garis vertikal penanda posisi Centroid kelompok """
    fig, ax = plt.subplots(figsize=(8, 5.5))
    
    # Ambil data khusus untuk titik pivot (Support & Resistance)
    df_pivot = df_cluster[df_cluster['Type'].isin(['Support', 'Resistance'])].copy()
    if df_pivot.empty:
        df_pivot = df_cluster.copy()
        
    # Pastikan kolom Tanggal bertipe datetime
    df_pivot['Tanggal'] = pd.to_datetime(df_pivot['Tanggal'])
    df_pivot = df_pivot.sort_values('Tanggal')
    
    x_data = df_pivot["Z_Score"].values
    y_data = df_pivot["Tanggal"].values
    cluster_labels = df_pivot["Cluster"].values
    
    # Gunakan palet warna yang sama persis dengan Gambar 3.3 agar konsisten
    WARNA_KONSISTEN = ["#1E3A8A", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4", "#6B7280", "#78350F", "#111827"]
    
    # 1. Plot sebaran titik data berdasarkan klaster pada garis waktu
    for c in range(k_val):
        mask = cluster_labels == c
        if np.any(mask):
            ax.scatter(x_data[mask], y_data[mask], 
                       color=WARNA_KONSISTEN[c], alpha=0.4, edgecolors='none', s=45, zorder=2)
            
    # 2. Hitung posisi koordinat Centroid (rata-rata nilai Z-Score per kelompok)
    centroids = df_pivot.groupby('Cluster')['Z_Score'].mean().reset_index()
    min_date, max_date = np.min(y_data), np.max(y_data)
    
    # 3. Gambar garis vertikal tegak lurus untuk posisi setiap Centroid
    for _, row in centroids.iterrows():
        c_idx = int(row['Cluster'])
        if c_idx < len(WARNA_KONSISTEN):
            warna_centroid = WARNA_KONSISTEN[c_idx]
            
            # Tarik garis vertikal putus-putus tebal memotong seluruh linimasa tanggal
            ax.axvline(x=row['Z_Score'], color=warna_centroid, linestyle='-.', linewidth=1.8, 
                       label=f"Garis Centroid Klaster {c_idx+1}", zorder=4)
            
            # Beri penanda 'X' besar di bagian tengah garis waktu untuk mempertegas posisi pusatnya
            tengah_index = len(y_data) // 2
            ax.scatter(row['Z_Score'], y_data[tengah_index], color=warna_centroid, marker="X", 
                       s=150, edgecolors='black', linewidths=1.2, zorder=5)

    # Atur tampilan layout grid dan batasan sumbu
    ax.set_title(f"Gambar 3.4: Ekstraksi Posisi Garis Centroid K-Means (K={k_val}) - {ticker}", fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Skala Nilai Fitur Hasil Standardisasi Z-Score", fontweight='semibold')
    ax.set_ylabel("Rentang Tanggal Historis", fontweight='semibold')
    
    ax.set_xlim(-3.5, 3.5)
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    
    ax.grid(True, linestyle=":", alpha=0.5)
    
    # Posisikan legend di luar kanan agar tidak menutupi chart historis saham
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), title="Referensi Pusat", title_fontproperties={'weight':'bold'})
    
    plt.tight_layout()
    return fig

def gambarkan_311_centroid_timeline(df_cluster, ticker, k_val, tipe_aktif="Support"):
    """ Gambar 3.11: Menampilkan sebaran data titik pivot berdasarkan Garis Waktu 
        dan posisi Titik Centroid-nya (X=Z-Score, Y=Tanggal) """
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    
    # Filter tipe data berdasarkan pilihan user (Support, Resistance, atau Keduanya)
    if tipe_aktif == "Keduanya":
        df_pivot = df_cluster[df_cluster['Type'].isin(['Support', 'Resistance'])].copy()
    else:
        df_pivot = df_cluster[df_cluster['Type'] == tipe_aktif].copy()
        
    if df_pivot.empty: 
        df_pivot = df_cluster.copy()
        
    df_pivot['Tanggal'] = pd.to_datetime(df_pivot['Tanggal'])
    df_pivot = df_pivot.sort_values('Tanggal')
    
    # Palet warna yang dikunci berdasarkan tipe data dan ID klaster agar konsisten
    WARNA_SUPPORT = ["#10B981", "#059669", "#047857", "#065F46", "#022C22", "#34D399", "#6EE7B7", "#A7F3D0", "#D1FAE5", "#ECFDF5"]
    WARNA_RESIST = ["#2563EB", "#1D4ED8", "#1E40AF", "#1E3A8A", "#172554", "#60A5FA", "#93C5FD", "#BFDBFE", "#DBEAFE", "#EFF6FF"]
    
    # 1. Plot Sebaran Titik Data
    for c in range(k_val):
        mask_c = df_pivot["Cluster"] == c
        
        if tipe_aktif == "Keduanya" or tipe_aktif == "Support":
            mask_s = mask_c & (df_pivot["Type"] == "Support")
            if np.any(mask_s):
                ax.scatter(df_pivot["Z_Score"][mask_s], df_pivot["Tanggal"][mask_s], 
                           color=WARNA_SUPPORT[c % 10], alpha=0.5, edgecolors='none', s=45, label=f"Support {c+1}")
                           
        if tipe_aktif == "Keduanya" or tipe_aktif == "Resistance":
            mask_r = mask_c & (df_pivot["Type"] == "Resistance")
            if np.any(mask_r):
                ax.scatter(df_pivot["Z_Score"][mask_r], df_pivot["Tanggal"][mask_r], 
                           color=WARNA_RESIST[c % 10], alpha=0.5, edgecolors='none', s=45, label=f"Resistance {c+1}")
            
    # 2. Plot Titik Centroid (Pusat Massa)
    # Grouping berdasarkan Type dan Cluster secara terpisah agar koordinat matematika centroid akurat
    centroids = df_pivot.groupby(['Type', 'Cluster'])['Z_Score'].mean().reset_index()
    tengah_idx = len(df_pivot) // 2
    
    for _, row in centroids.iterrows():
        c_idx = int(row['Cluster'])
        t_type = row['Type']
        warna_c = WARNA_SUPPORT[c_idx % 10] if t_type == "Support" else WARNA_RESIST[c_idx % 10]
        
        ax.scatter(row['Z_Score'], df_pivot["Tanggal"].values[tengah_idx], color=warna_c, marker="X", 
                   s=160, edgecolors='black', linewidths=1.2, label=f"Centroid {t_type[:3]}-{c_idx+1}", zorder=5)
                   
    ax.set_title(f"Gambar 3.11: Pemetaan Positional Titik Centroid Data {tipe_aktif} - {ticker}", fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Skala Nilai Fitur Hasil Standardisasi Z-Score", fontweight='semibold')
    ax.set_ylabel("Rentang Tanggal Historis", fontweight='semibold')
    ax.set_xlim(-3.5, 3.5)
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), title="Keterangan")
    plt.tight_layout()
    return fig

def gambarkan_312_min_max_development(df_cluster, ticker, k_val, tipe_aktif="Support"):
    """ Gambar 3.12: Mengembangkan Gambar 3.11 dengan menambahkan batas rentang internal Min & Max 
        hasil perhitungan standar deviasi klaster secara independen (X=Z-Score, Y=Tanggal) """
    import matplotlib.patches as patches
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    
    if tipe_aktif == "Keduanya":
        df_pivot = df_cluster[df_cluster['Type'].isin(['Support', 'Resistance'])].copy()
    else:
        df_pivot = df_cluster[df_cluster['Type'] == tipe_aktif].copy()
        
    if df_pivot.empty: 
        df_pivot = df_cluster.copy()
        
    df_pivot['Tanggal'] = pd.to_datetime(df_pivot['Tanggal'])
    df_pivot = df_pivot.sort_values('Tanggal')
    
    WARNA_SUPPORT = ["#10B981", "#059669", "#047857", "#065F46", "#022C22", "#34D399", "#6EE7B7", "#A7F3D0", "#D1FAE5", "#ECFDF5"]
    WARNA_RESIST = ["#2563EB", "#1D4ED8", "#1E40AF", "#1E3A8A", "#172554", "#60A5FA", "#93C5FD", "#BFDBFE", "#DBEAFE", "#EFF6FF"]
    min_date, max_date = np.min(df_pivot["Tanggal"]), np.max(df_pivot["Tanggal"])
    
    # 1. Plot Sebaran Titik Data & Highlight Rentang Batas
    for c in range(k_val):
        mask_c = df_pivot["Cluster"] == c
        
        # Sub-proses untuk data Support
        if tipe_aktif == "Keduanya" or tipe_aktif == "Support":
            mask_s = mask_c & (df_pivot["Type"] == "Support")
            if np.any(mask_s):
                warna_s = WARNA_SUPPORT[c % 10]
                ax.scatter(df_pivot["Z_Score"][mask_s], df_pivot["Tanggal"][mask_s], color=warna_s, alpha=0.35, edgecolors='none', s=45)
                min_xs, max_xs = np.min(df_pivot["Z_Score"][mask_s]), np.max(df_pivot["Z_Score"][mask_s])
                rect_s = patches.Rectangle((min_xs, min_date), (max_xs - min_xs), (max_date - min_date), 
                                          linewidth=1.0, linestyle='--', edgecolor=warna_s, facecolor=warna_s, alpha=0.06)
                ax.add_patch(rect_s)
                ax.axvline(x=min_xs, color=warna_s, linestyle=':', alpha=0.4, linewidth=1.0)
                ax.axvline(x=max_xs, color=warna_s, linestyle=':', alpha=0.4, linewidth=1.0)
                
        # Sub-proses untuk data Resistance
        if tipe_aktif == "Keduanya" or tipe_aktif == "Resistance":
            mask_r = mask_c & (df_pivot["Type"] == "Resistance")
            if np.any(mask_r):
                warna_r = WARNA_RESIST[c % 10]
                ax.scatter(df_pivot["Z_Score"][mask_r], df_pivot["Tanggal"][mask_r], color=warna_r, alpha=0.35, edgecolors='none', s=45)
                min_xr, max_xr = np.min(df_pivot["Z_Score"][mask_r]), np.max(df_pivot["Z_Score"][mask_r])
                rect_r = patches.Rectangle((min_xr, min_date), (max_xr - min_xr), (max_date - min_date), 
                                          linewidth=1.0, linestyle='--', edgecolor=warna_r, facecolor=warna_r, alpha=0.06)
                ax.add_patch(rect_r)
                ax.axvline(x=min_xr, color=warna_r, linestyle=':', alpha=0.4, linewidth=1.0)
                ax.axvline(x=max_xr, color=warna_r, linestyle=':', alpha=0.4, linewidth=1.0)

    # 2. Plot Titik Centroid Berlabel di Atas Overlay
    centroids = df_pivot.groupby(['Type', 'Cluster'])['Z_Score'].mean().reset_index()
    tengah_idx = len(df_pivot) // 2
    for _, row in centroids.iterrows():
        c_idx = int(row['Cluster'])
        t_type = row['Type']
        warna_c = WARNA_SUPPORT[c_idx % 10] if t_type == "Support" else WARNA_RESIST[c_idx % 10]
        ax.scatter(row['Z_Score'], df_pivot["Tanggal"].values[tengah_idx], color=warna_c, marker="X", 
                   s=140, edgecolors='black', linewidths=1.2, label=f"Batas {t_type[:3]}-{c_idx+1}", zorder=5)
                   
    ax.set_title(f"Gambar 3.12: Formasi Batas Perluasan Rentang (Min/Max) Data {tipe_aktif} - {ticker}", fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Skala Nilai Fitur Hasil Standardisasi Z-Score", fontweight='semibold')
    ax.set_ylabel("Rentang Tanggal Historis", fontweight='semibold')
    ax.set_xlim(-3.5, 3.5)
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), title="Batas Zona")
    plt.tight_layout()
    return fig

def gambarkan_313_zona_rupiah_aktual(df_raw, df_zona, ticker, k_val):
    """ Gambar 3.13 (Terupdate): Visualisasi Tren Harga Saham Riil dengan Arsiran Area 
        S&R Lengkap dengan Keterangan Nama Zona dan Rentang Nominal Rupiah Dinamis """
    fig, ax = plt.subplots(figsize=(12, 6.5)) # Ukuran dilebarkan sedikit agar teks muat rapi
    
    df_raw['Tanggal'] = pd.to_datetime(df_raw['Tanggal'])
    df_raw = df_raw.sort_values('Tanggal')
    
    # Plot Garis Harga Saham Aktual
    ax.plot(df_raw["Tanggal"], df_raw["Level"], color="black", linewidth=1.2, label="Harga Saham Aktual", alpha=0.85, zorder=2)
    
    # Ambil tanggal paling ujung kanan untuk posisi penempatan teks keterangan zona
    tanggal_maksimal = df_raw["Tanggal"].max()
    
    # Counter untuk penomoran urutan zona (diurutkan dari harga terendah ke tertinggi)
    # Urutkan df_zona berdasarkan nilai Centroid_Price agar penomoran zona 1, 2, 3 konsisten runtut
    df_zona_sorted = df_zona.sort_values('Centroid_Price').reset_index(drop=True)
    
    support_idx = 1
    resistance_idx = 1
    
    support_labeled = False
    resistance_labeled = False
    
    for _, row in df_zona_sorted.iterrows():
        min_p = int(row['Min'])
        max_p = int(row['Max'])
        center_p = int(row['Centroid_Price'])
        
        if row['Type'] == 'Resistance':
            label_r = "Zona Resistance (Batas Atas)" if not resistance_labeled else ""
            resistance_labeled = True
            
            # 1. Gambar arsiran area merah
            ax.axhspan(min_p, max_p, color='red', alpha=0.13, label=label_r, zorder=1)
            # 2. Gambar garis tengah Centroid
            ax.axhline(center_p, color='red', linestyle='--', alpha=0.4, linewidth=1.0, zorder=1)
            
            # 3. TAMBAHAN: Tulis Teks Keterangan Zona Resistance di ujung kanan grafik
            teks_label = f"Resistance {resistance_idx}\n({min_p} - {max_p})"
            ax.text(tanggal_maksimal, center_p, teks_label, color="#991B1B", 
                    fontsize=8.5, fontweight='bold', va='center', ha='left',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=2))
            
            resistance_idx += 1
            
        elif row['Type'] == 'Support':
            label_s = "Zona Support (Batas Bawah)" if not support_labeled else ""
            support_labeled = True
            
            # 1. Gambar arsiran area hijau
            ax.axhspan(min_p, max_p, color='green', alpha=0.13, label=label_s, zorder=1)
            # 2. Gambar garis tengah Centroid
            ax.axhline(center_p, color='green', linestyle='--', alpha=0.4, linewidth=1.0, zorder=1)
            
            # 3. TAMBAHAN: Tulis Teks Keterangan Zona Support di ujung kanan grafik
            teks_label = f"Support {support_idx}\n({min_p} - {max_p})"
            ax.text(tanggal_maksimal, center_p, teks_label, color="#065F46", 
                    fontsize=8.5, fontweight='bold', va='center', ha='left',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=2))
            
            support_idx += 1
            
    ax.set_title(f"Gambar 3.13: Pemetaan Rentang Zona Dinamis S&R Konversi Rupiah (K={k_val}) - {ticker}", fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel("Rentang Linimasa Tanggal Historis", fontweight='semibold')
    ax.set_ylabel("Nominal Harga Saham Riil (Rupiah)", fontweight='semibold')
    
    # Berikan ruang tambahan di sebelah kanan sumbu X agar teks keterangan tidak terpotong bingkai
    import matplotlib.dates as mdates
    rentang_waktu = (max_date := df_raw["Tanggal"].max()) - df_raw["Tanggal"].min()
    ax.set_xlim(df_raw["Tanggal"].min(), df_raw["Tanggal"].max() + rentang_waktu * 0.12)
    
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.3)
    
    plt.tight_layout()
    return fig
# ==========================================
# SUB-BAB A: STANDARDIZATION & PIVOT POINTS
# ==========================================
if menu_select == "A. Standardisasi & Pivot Points":
    st.markdown('<div class="section-title">A. Analisis Data, Pivot Points, dan Standardisasi Z-Score</div>', unsafe_allow_html=True)
    
    # Bagian Penyaringan Emiten & Gambar 3.1 Sektoral tetap berada di bagian atas...
    st.subheader("📌 Tahapan Penyaringan dan Konsistensi Data Penelitian")
    # ... (code penyaringan sebelumnya) ...
    
    st.markdown("---")
    
    # ----------------------------------------------------
    # DATA EMITEN AKTIF (DAPAT DI-FILTER DARI SIDEBAR)
    # ----------------------------------------------------
    st.subheader(f"🔍 Analisis Deteksi & Transformasi Spasial Dinamis: {ticker_aktif}")
    
    file_pattern = os.path.join(PATH_PREPROCESSED, f"{ticker_aktif}*.csv")
    matched_files = glob.glob(file_pattern)
    
    if matched_files:
        df_raw = pd.read_csv(matched_files[0])
        df_raw['Tanggal'] = pd.to_datetime(df_raw['Tanggal'])
        
        # --- BLOK INTEGRASI GAMBAR 3.2 TUNGGAL (X=Harga/Z-Score, Y=Tanggal) ---
        st.write(
            "Hasil identifikasi Pivot Points menunjukkan bahwa setiap emiten memiliki rentang harga yang berbeda, "
            f"mulai dari puluhan hingga ribuan rupiah per lembar saham. Oleh karena itu, khusus untuk emiten **{ticker_aktif}**, "
            "dilakukan standardisasi menggunakan metode Z-Score agar seluruh data berada pada skala yang sama "
            "sebelum proses klasterisasi. Hasil standardisasi ditampilkan pada **Gambar 3.2**."
        )
        
        # Memanggil fungsi grafik komparasi bersisian (Timeline)
        fig_32_timeline = gambarkan_komparasi_zscore_timeline(df_raw, ticker_aktif)
        st.pyplot(fig_32_timeline)
        hitung_dan_export_300dpi(fig_32_timeline, nama_file=f"Gambar_3.2_Transformasi_ZScore_{ticker_aktif}.png")
        
        st.write(
            "Based on the visualization above, seluruh data berhasil ditransformasikan ke dalam skala yang seragam "
            "dengan nilai rata-rata (*mean*) mendekati 0 dan standar deviasi sebesar 1. Kondisi ini membuat setiap "
            "emiten memiliki skala yang setara sehingga proses klasterisasi menggunakan algoritma K-Means "
            "dapat dilakukan secara lebih objektif."
        )
        
        st.markdown("---")
        
        # Tampilan tabel sampel data dan grafik runut waktu harian asli bawaanmu
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**📋 Sampel Data Terstandardisasi ({ticker_aktif})**")
            st.dataframe(df_raw[['Tanggal', 'Level', 'Type', 'Z_Score']].head(15), use_container_width=True, hide_index=True)
            
        with col2:
            st.markdown("**📈 Grafik Deteksi Pivot & Transformasi Z-Score**")
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
            
            # Subplot 1: Harga Riil
            ax1.plot(df_raw["Tanggal"], df_raw["Level"], label="Harga Penutupan Harian", color="blue", alpha=0.6)
            df_high = df_raw[df_raw['Type'] == 'Resistance']
            df_low  = df_raw[df_raw['Type'] == 'Support']
            ax1.scatter(df_high["Tanggal"], df_high["Level"], color="red", s=40, label="Pivot High (R)", zorder=5)
            ax1.scatter(df_low["Tanggal"], df_low["Level"], color="green", s=40, label="Pivot Low (S)", zorder=5)
            ax1.set_title(f"Ekstraksi Titik Balik (Pivot Points) Riil - {ticker_aktif}")
            ax1.legend()
            ax1.grid(True, linestyle="--", alpha=0.5)
            
            # Subplot 2: Distribusi Z-Score
            ax2.plot(df_raw["Tanggal"], df_raw["Z_Score"], label="Nilai Hasil Z-Score", color="purple", linestyle="-", alpha=0.7)
            ax2.axhline(0, color="black", linestyle="-", alpha=0.4)
            ax2.set_title("Hasil Transformasi Penyelarasan Skala (Z-Score)")
            ax2.legend()
            ax2.grid(True, linestyle="--", alpha=0.5)
            
            plt.tight_layout()
            st.pyplot(fig)
            hitung_dan_export_300dpi(fig, nama_file=f"SubbabA_Pivot_ZScore_{ticker_aktif}.png")
    else:
        st.error(f"❌ Berkas CSV untuk emiten {ticker_aktif} tidak ditemukan di direktori: {PATH_PREPROCESSED}")
# ==========================================
# SUB-BAB B: IMPLEMENTASI K-MEANS & CENTROID
# ==========================================
elif menu_select == "B. Implementasi K-Means & Centroid":
    st.markdown('<div class="section-title">B. Implementasi Klasterisasi K-Means & Ekstraksi Centroid</div>', unsafe_allow_html=True)
    
    # Slider kontrol dinamis dari sidebar asli kamu
    k_select = st.sidebar.slider("Pilih Nilai K untuk melihat Posisi Centroid:", 2, 10, 4)
    
    # Membaca data detail clustering hasil K-Means per nilai K yang dipilih
    file_pattern = os.path.join(PATH_CLUSTERING, f"k{k_select}", "detail", f"{ticker_aktif}*.csv")
    matched_files = glob.glob(file_pattern)
    
    if matched_files:
        df_cluster = pd.read_csv(matched_files[0])
        
        # ----------------------------------------------------
        # SEKSYEN GAMBAR 3.3: VARIASI NILAI K (DINAMIS S/D K=10)
        # ----------------------------------------------------
        st.subheader("⚙️ Pengujian Struktur Variasi Jumlah Klaster (K)")
        st.write(
            "Proses klasterisasi dilakukan dengan menguji variasi jumlah klaster (K) dari 2 hingga 10 "
            "menggunakan algoritma K-Means pada data Support dan Resistance secara terpisah. Setiap variasi "
            "nilai K dievaluasi untuk melihat hasil pengelompokan data yang terbentuk. Hasil pengujian "
            "tersebut ditampilkan pada **Gambar 3.3**."
        )
        
        # Sekarang melemparkan k_select (2 sampai 10) dari slider sidebar secara interaktif
        fig_33 = gambarkan_variasi_k_inertia(df_cluster, ticker_aktif, k_select)
        st.pyplot(fig_33)
        hitung_dan_export_300dpi(fig_33, nama_file=f"Gambar_3.3_Proses_Klasterisasi_K{k_select}_{ticker_aktif}.png")
        
        st.write(
            f"Berdasarkan **Gambar 3.3**, visualisasi di atas memperlihatkan bagaimana sebaran titik *Pivot Points* "
            f"pada emiten **{ticker_aktif}** yang dipetakan berdasarkan garis waktu kronologis (sumbu vertikal kiri) "
            f"dan nilai skala hasil standardisasi Z-Score (sumbu horizontal bawah). Pada pengujian interaktif dengan jumlah "
            f"klaster **K={k_select}**, sistem secara otomatis membagi sebaran titik balik ke dalam **{k_select} kelompok wilayah** "
            f"yang ditandai dengan kotak *highlight* arsiran warna terpisah."
        )
        st.write(
            f"Ketika Anda mengubah nilai K di sidebar dari K=2 hingga K=10, Anda dapat mengamati secara langsung bahwa "
            f"semakin besar nilai K yang dipilih, semakin banyak blok kelompok atau kotak *highlight* baru yang terbentuk "
            f"membelah rentang spasial tersebut, sehingga sebaran data pembalikan harga menjadi jauh lebih rinci dan spesifik. "
            f"Hasil eksperimen ini membuktikan bahwa perubahan nilai K secara langsung memengaruhi tingkat kerincian kerapatan "
            f"struktur klaster yang dihasilkan dan menjadi fondasi utama dalam menentukan jumlah klaster terbaik saat evaluasi model."
        )
        
        st.markdown("---")
        # ----------------------------------------------------
        # SEKSYEN GAMBAR 3.4: SEBARAN DATA & POSISI CENTROID
        # ----------------------------------------------------
        st.subheader("📍 Pemetaan Lokasi Centroid Ruang Spasial Z-Score")
        # ... (Sisa kode Gambar 3.4 yang menampilkan tanda 'X' besar sebagai centroid tetap di bawahnya) ...
        st.write(
            "Hasil proses K-Means menghasilkan titik pusat (*centroid*) yang mewakili setiap kelompok data "
            "berdasarkan kedekatan antar-Pivot Points. Setelah proses klasterisasi selesai, setiap data menjadi "
            "anggota dari kelompok yang memiliki *centroid* terdekat. Sebaran data dan posisi *centroid* ditampilkan "
            "pada **Gambar 3.4**."
        )
        
        fig_34 = gambarkan_sebaran_dan_centroid(df_cluster, ticker_aktif, k_select)
        st.pyplot(fig_34)
        hitung_dan_export_300dpi(fig_34, nama_file=f"Gambar_3.4_Centroid_Klaster_K{k_select}_{ticker_aktif}.png")
        
        st.write(
            "Berdasarkan gambar tersebut, data Pivot Points berhasil dikelompokkan ke dalam klaster masing-masing "
            "dengan posisi *centroid* yang merepresentasikan pusat dari setiap kelompok. Hasil ini menjadi dasar "
            "dalam pembentukan rentang zona Support dan Resistance pada tahap berikutnya."
        )
        
        # Teks Narasi Pendukung Tambahan Bab III
        st.write(
            "Hasil klasterisasi menunjukkan bahwa posisi *centroid* terbentuk mengikuti sebaran data Pivot Points "
            "pada setiap kelompok. Semakin banyak titik data yang berada pada suatu rentang nilai, semakin dekat "
            "posisi *centroid* dengan pusat sebaran data tersebut. Kondisi ini menunjukkan bahwa *centroid* dapat "
            "merepresentasikan area yang memiliki konsentrasi titik balik harga lebih tinggi dibandingkan area lainnya. "
            "Oleh karena itu, *centroid* digunakan sebagai acuan dalam pembentukan rentang zona Support dan Resistance "
            "pada tahap selanjutnya."
        )
        st.write(
            "Hasil klasterisasi juga menunjukkan bahwa proses pengelompokan dapat dilakukan secara konsisten "
            "meskipun setiap emiten memiliki rentang harga yang berbeda. Hal ini karena seluruh data telah melalui "
            "proses standardisasi Z-Score sehingga berada pada skala yang sama. Nilai *centroid* yang dihasilkan "
            "dari setiap klaster kemudian digunakan sebagai dasar dalam pembentukan batas bawah (Min) dan batas "
            "atas (Max) untuk membentuk zona Support dan Resistance pada tahap selanjutnya."
        )
        
    else:
        st.error(f"❌ Berkas detail klaster K={k_select} untuk {ticker_aktif} tidak ditemukan di: {PATH_CLUSTERING}")
# ==========================================
# SUB-BAB C: PEMETAAN ZONA RENTANG DINAMIS
# ==========================================
elif menu_select == "C. Pemetaan Zona Rentang Dinamis":
    st.markdown('<div class="section-title">C. Pemetaan Zona Rentang Dinamis (Batas Spasial Internal)</div>', unsafe_allow_html=True)
    
    # Slider Pilihan K terintegrasi dari sidebar asli kamu
    k_select = st.sidebar.slider("Pilih Nilai K untuk Visualisasi Zona:", 2, 10, 4)
    
    # Membaca berkas klaster detail dan summary_zona hasil perhitungan rumus Min/Max kamu
    file_pattern_detail = os.path.join(PATH_CLUSTERING, f"k{k_select}", "detail", f"{ticker_aktif}*.csv")
    file_pattern_zona   = os.path.join(PATH_CLUSTERING, f"k{k_select}", "summary_zona", f"{ticker_aktif}*.csv")
    file_raw_pattern     = os.path.join(PATH_PREPROCESSED, f"{ticker_aktif}*.csv")
    
    matched_detail = glob.glob(file_pattern_detail)
    matched_zona   = glob.glob(file_pattern_zona)
    matched_raw    = glob.glob(file_raw_pattern)
    
    if matched_detail and matched_zona and matched_raw:
        df_cluster = pd.read_csv(matched_detail[0])
        df_zona    = pd.read_csv(matched_zona[0])
        df_raw     = pd.read_csv(matched_raw[0])
        
        # Pilihan sub-tipe filter khusus untuk Gambar 3.11 & 3.12 agar tidak bertumpuk
        tipe_visual = st.radio("Tinjau Komponen Struktur Fitur:", ["Support", "Resistance", "Keduanya"], horizontal=True)
        
        # ----------------------------------------------------
        # SEKSYEN GAMBAR 3.11: POSISI CENTROID TIMELINE
        # ----------------------------------------------------
        st.subheader("📍 Titik Pusat (Centroid) Hasil Ekstraksi K-Means")
        st.write(
            "Nilai *centroid* yang diperoleh dari proses K-Means pada **Gambar 3.11** di bawah ini, "
            "selanjutnya digunakan untuk membentuk rentang zona *Support* dan *Resistance*. Proses ini merepresentasikan "
            "pusat akumulasi titik balik harga saham dalam ruang dimensi fitur Z-Score."
        )
        
        fig_311 = gambarkan_311_centroid_timeline(df_cluster, ticker_aktif, k_select, tipe_aktif=tipe_visual)
        st.pyplot(fig_311)
        hitung_dan_export_300dpi(fig_311, nama_file=f"Gambar_3.11_Centroid_Timeline_{ticker_aktif}.png")
        
        st.markdown("---")
        
        # ----------------------------------------------------
        # SEKSYEN GAMBAR 3.12: PENGEMBANGAN MIN MAX OVERLAY
        # ----------------------------------------------------
        st.subheader("🛡️ Pengembangan Batas Atas (Max) dan Batas Bawah (Min)")
        st.write(
            "Setiap *centroid* dikembangkan menjadi batas bawah (*Min*) dan batas atas (*Max*) menggunakan "
            "standar deviasi internal dari masing-masing klaster. Hasil perhitungan tersebut kemudian dikonversi kembali "
            "ke skala harga asli sehingga rentang zona dapat direpresentasikan dalam satuan rupiah. Proses pembentukan "
            "batas zona ditampilkan pada **Gambar 3.12**."
        )
        
        fig_312 = gambarkan_312_min_max_development(df_cluster, ticker_aktif, k_select, tipe_aktif=tipe_visual)
        st.pyplot(fig_312)
        hitung_dan_export_300dpi(fig_312, nama_file=f"Gambar_3.12_MinMax_Development_{ticker_aktif}.png")
        
        st.write(
            "Berdasarkan **Gambar 3.12**, batas bawah (*Min*) dan batas atas (*Max*) terbentuk di sekitar posisi *centroid*, "
            "sehingga setiap klaster tidak lagi direpresentasikan sebagai satu titik, tetapi sebagai sebuah rentang zona. "
            "Lebar rentang yang dihasilkan menyesuaikan dengan penyebaran data pada masing-masing klaster, sehingga "
            "setiap zona memiliki batas yang berbeda. Rentang zona inilah yang selanjutnya digunakan sebagai acuan pada proses pengujian model."
        )
        
        st.markdown("---")
        
        # ----------------------------------------------------
        # SEKSYEN GAMBAR 3.13: ZONA RUPIAH AKTUAL
        # ----------------------------------------------------
        st.subheader("📈 Hasil Akhir Pemetaan Zona Dinamis Satuan Rupiah")
        st.write(
            "Rentang zona yang telah diperoleh kemudian ditampilkan pada grafik pergerakan harga saham untuk memperlihatkan "
            "posisi zona *Support* dan *Resistance* terhadap data harga aktual. Hasil visualisasi tersebut disajikan pada **Gambar 3.13**."
        )
        
        fig_313 = gambarkan_313_zona_rupiah_aktual(df_raw, df_zona, ticker_aktif, k_select)
        st.pyplot(fig_313)
        hitung_dan_export_300dpi(fig_313, nama_file=f"Gambar_3.13_Zona_Rupiah_Aktual_{ticker_aktif}.png")
        
        st.write(
            "Berdasarkan **Gambar 3.13**, pergerakan harga saham ditampilkan dalam bentuk garis, sedangkan zona *Support* "
            "dan *Resistance* divisualisasikan sebagai area berwarna hasil perhitungan batas bawah (*Min*) dan batas atas (*Max*). "
            "Area berwarna **hijau** menunjukkan zona *Support*, sedangkan area berwarna **merah** menunjukkan zona *Resistance*. "
            "Visualisasi ini memperlihatkan bahwa rentang zona yang terbentuk mengikuti sebaran pergerakan harga historis "
            "sehingga dapat digunakan sebagai acuan pada proses pengujian model."
        )
        
        # Paragraf khusus Analisis K=2 (Kondisi Khusus Evaluasi Skripsi)
        if k_select == 2:
            st.info(
                "💡 **Analisis Khusus Konfigurasi K=2:** Pada konfigurasi K=2, data Pivot Points terbagi menjadi dua klaster "
                "yang merepresentasikan zona Support dan Resistance secara biner. Karena jumlah klaster yang digunakan "
                "relatif sedikit, rentang zona yang dihasilkan cenderung lebih lebar sehingga mencakup lebih banyak titik Pivot Points. "
                "Hasil ini menunjukkan bahwa pembentukan zona telah mengikuti sebaran data historis pada masing-masing klaster. "
                "Rentang zona yang diperoleh selanjutnya digunakan sebagai dasar pada proses pengujian model untuk mengevaluasi "
                "performanya dalam mengidentifikasi pergerakan harga saham sektor energi."
            )
            
    else:
        st.error("❌ Kegagalan memuat berkas detail klaster, summary_zona, atau file data dasar preprocessing.")

# ==========================================
# SUB-BAB D: EVALUASI PERFORMA MODEL
# ==========================================
elif menu_select == "D. Evaluasi Performa Model":
    st.markdown('<div class="section-title">D. Evaluasi Performa Model (Hasil Kinerja Riil Trading Rules)</div>', unsafe_allow_html=True)
    
    # Kumpulkan semua file summary_metrics_k2.csv sampai k10 otomatis dari folder evaluation
    all_metrics = []
    for k in range(2, 11):
        metric_file = os.path.join(PATH_EVALUATION, f"summary_metrics_k{k}.csv")
        if os.path.exists(metric_file):
            df_m = pd.read_csv(metric_file)
            # Rename Indonesian columns to English
            df_m = df_m.rename(columns={
                'Akurasi_Total': 'Accuracy',
                'Ketepatan_Prediksi': 'Precision',
                'Daya_Tangkap_Model': 'Recall',
                'Skor_Keseimbangan_F1': 'F1_Score'
            })
            df_m['K_Value'] = f"K={k}"
            all_metrics.append(df_m)
            
    if all_metrics:
        df_all_perf = pd.concat(all_metrics)
        
        # Fitur Pilihan Mode Tampilan di dalam halaman
        mode_tampilan = st.radio("Pilih Mode Analisis Evaluasi:", ["Rata-rata Sektoral (26 Emiten)", "Per Emiten Individu"], horizontal=True)
        
        mul = 100 if df_all_perf['Accuracy'].max() <= 1.0 else 1
        
        if mode_tampilan == "Rata-rata Sektoral (26 Emiten)":
            st.subheader("📊 Rekapitulasi Rata-Rata Final Performa Sektoral Energi (K2 - K10)")
            
            # Hitung rata-rata grouping berdasarkan K_Value (Persis seperti check_best_k.py)
            df_sektoral = df_all_perf.groupby('K_Value')[['Accuracy', 'Precision', 'Recall', 'F1_Score']].mean().reset_index()
            
            # Urutkan berdasarkan index K agar rapi dari K=2 sampai K=10
            df_sektoral['sort_key'] = df_sektoral['K_Value'].str.extract('(\d+)').astype(int)
            df_sektoral = df_sektoral.sort_values('sort_key').drop(columns=['sort_key'])
            
            st.dataframe(df_sektoral, use_container_width=True, hide_index=True)
            
            df_plot = df_sektoral
            judul_grafik = "Grafik Komparasi Rata-Rata Performa Sektoral Energi"
            nama_file_out = "SubbabD_RataRata_Sektoral_Energi.png"
            
        else:
            st.subheader(f"📊 Tabel Perbandingan Nilai K2 s/d K10 - {ticker_aktif}")
            
            # Filter berdasarkan emiten aktif pilihan user
            df_ticker_perf = df_all_perf[df_all_perf['Emiten'] == ticker_aktif].copy()
            df_ticker_perf['sort_key'] = df_ticker_perf['K_Value'].str.extract('(\d+)').astype(int)
            df_ticker_perf = df_ticker_perf.sort_values('sort_key').drop(columns=['sort_key'])
            
            st.dataframe(df_ticker_perf[['K_Value', 'Accuracy', 'Precision', 'Recall', 'F1_Score']], use_container_width=True, hide_index=True)
            
            df_plot = df_ticker_perf
            judul_grafik = f"Grafik Komparasi Metrik Confusion Matrix ({ticker_aktif})"
            nama_file_out = f"SubbabD_Komparasi_Akurasi_{ticker_aktif}.png"
            
        # Gambar Grafik Garis Komparasi Berdasarkan Mode yang Dipilih
        fig_b, ax_b = plt.subplots(figsize=(12, 6))
        x_indices = np.arange(len(df_plot))
        
        ax_b.plot(x_indices, df_plot["Accuracy"] * mul, marker='o', linewidth=2.5, markersize=8, label="Accuracy", color="#FF6B6B")
        ax_b.plot(x_indices, df_plot["Precision"] * mul, marker='s', linewidth=2.5, markersize=8, label="Precision", color="#4ECDC4")
        ax_b.plot(x_indices, df_plot["Recall"] * mul, marker='^', linewidth=2.5, markersize=8, label="Recall", color="#FFD93D")
        ax_b.plot(x_indices, df_plot["F1_Score"] * mul, marker='D', linewidth=2.5, markersize=8, label="F1-Score", color="#6C5CE7")
        
        ax_b.set_xticks(x_indices)
        ax_b.set_xticklabels(df_plot["K_Value"])
        ax_b.set_ylabel("Kinerja Prediksi Sinyal (%)")
        ax_b.set_title(judul_grafik)
        ax_b.legend()
        ax_b.grid(True, linestyle=":", alpha=0.5)
        
        st.pyplot(fig_b)
        hitung_dan_export_300dpi(fig_b, nama_file=nama_file_out)
        
    else:
        st.error(f"❌ Berkas metrik pengujian `summary_metrics_k*.csv` tidak ditemukan di folder: {PATH_EVALUATION}")