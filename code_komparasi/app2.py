import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from sklearn.cluster import KMeans

# 1. Konfigurasi Antarmuka Web
st.set_page_config(page_title="Deteksi S/R Saham IDX Real-Time (K=2)", layout="wide")
st.title("Aplikasi Deteksi Zona Support & Resistance Saham Real-Time")
st.write("Analisis otomatis berbasis pada seluruh saham IDX.")

# 2. Input Parameter di Sidebar
st.sidebar.header("Parameter Analisis")

# User bisa mengetik kode saham apa saja secara bebas
ticker_input = st.sidebar.text_input("Masukkan Kode Saham IDX (Contoh: BBCA, BMRI, ADRO):", value="ADRO").upper().strip()
ticker_yahoo = f"{ticker_input}.JK"

opsi_waktu = {
    "1 Minggu": "7d",
    "1 Bulan": "1mo",
    "3 Bulan": "3mo",
    "6 Bulan": "6mo",
    "1 Tahun": "1y",
    "2 Tahun": "2y"
}
pilihan_waktu = st.sidebar.selectbox("Rentang Waktu Analisis:", list(opsi_waktu.keys()), index=4) # Default 1 Tahun

# Konfigurasi K terkunci ke K=2 sesuai model paling optimal hasil TA kamu
K_FIXED = 2

# 3. Menarik Data Real-Time dari yfinance
@st.cache_data(ttl=3600)
def fetch_data_yahoo(ticker, period):
    try:
        df = yf.download(ticker, period=period, interval='1d')
        if df.empty:
            return None
        
        # Meratakan MultiIndex jika ada di versi yfinance terbaru
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        df = df.reset_index()
        return df
    except Exception as e:
        return None

# Validasi input sebelum fetch data
if ticker_input:
    with st.spinner(f"Sedang mengunduh data saham {ticker_yahoo} dari Yahoo Finance..."):
        df_filtered = fetch_data_yahoo(ticker_yahoo, opsi_waktu[pilihan_waktu])
    
    if df_filtered is not None and len(df_filtered) > 5:
        # Ekstraksi Series 1D
        dates = df_filtered['Date'].dt.strftime('%Y-%m-%d').tolist()
        opens = [int(round(x)) for x in df_filtered['Open'].squeeze().astype(float)]
        highs = [int(round(x)) for x in df_filtered['High'].squeeze().astype(float)]
        lows = [int(round(x)) for x in df_filtered['Low'].squeeze().astype(float)]
        closes = [int(round(x)) for x in df_filtered['Close'].squeeze().astype(float)]
        
        harga_terakhir = closes[-1]
        tgl_terakhir = dates[-1]

        # Header Informasi
        st.write("---")
        col_header1, col_header2 = st.columns(2)
        with col_header1:
            st.metric(label=f"Saham: {ticker_yahoo}", value=f"Rp {harga_terakhir:,}", delta=f"Data per {tgl_terakhir}")

        # 4. Deteksi Pivot Points (High/Low) & Eksekusi K-Means K=2 Sesuai Metodologi TA
        def hitung_zona_sr_kmeans_k2(high_prices, low_prices):
            # Deteksi Pivot Point sederhana dari historis High & Low
            pivots = list(high_prices) + list(low_prices)
            data_pivots = np.array(pivots).reshape(-1, 1)
            
            # K-Means K=2
            kmeans = KMeans(n_clusters=K_FIXED, random_state=42, n_init=10)
            kmeans.fit(data_pivots)
            labels = kmeans.labels_
            centroids = kmeans.cluster_centers_.flatten()
            
            # Pengurutan: Centroid lebih rendah = Support, Centroid lebih tinggi = Resistance
            idx_sorted = np.argsort(centroids)
            
            zona_list = []
            nama_zona = ['Zona Support (Area Bawah)', 'Zona Resistance (Area Atas)']
            
            for rank, idx_cluster in enumerate(idx_sorted):
                centroid_val = centroids[idx_cluster]
                cluster_data = data_pivots[labels == idx_cluster]
                
                # Dynamic Width menggunakan internal std_dev
                std_dev = np.std(cluster_data) if len(cluster_data) > 0 else 0
                
                bawah = int(round(centroid_val - std_dev))
                atas = int(round(centroid_val + std_dev))
                tengah = int(round(centroid_val))
                
                zona_list.append({
                    'tipe': nama_zona[rank],
                    'tengah': tengah,
                    'bawah': bawah,
                    'atas': atas
                })
                
            return zona_list  # Mengembalikan [Zona Support, Zona Resistance]

        zona_sr = hitung_zona_sr_kmeans_k2(highs, lows)
        zona_support = zona_sr[0]
        zona_resistance = zona_sr[1]

        # 5. Tampilkan Nilai Zona (Support Area & Resistance Area) Tanpa Desimal
        st.subheader(f"Area Zona Support & Resistance - Saham {ticker_yahoo}")
        col_sup, col_res = st.columns(2)
        
        with col_sup:
            st.success(f"**{zona_support['tipe']}**")
            st.metric(label="Garis Tengah Centroid", value=f"Rp {zona_support['tengah']:,}")
            st.markdown(f"**Rentang Area Highlight:** `Rp {zona_support['bawah']:,}` s/d `Rp {zona_support['atas']:,}`")

        with col_res:
            st.error(f"**{zona_resistance['tipe']}**")
            st.metric(label="Garis Tengah Centroid", value=f"Rp {zona_resistance['tengah']:,}")
            st.markdown(f"**Rentang Area Highlight:** `Rp {zona_resistance['bawah']:,}` s/d `Rp {zona_resistance['atas']:,}`")

        # 6. Logika Komparasi Harga Terakhir & Kategori Rekomendasi
        st.write("---")
        st.subheader("Rekomendasi Sistem Berdasarkan Posisi Harga Terakhir")

        jarak_ke_support = abs(harga_terakhir - zona_support['tengah'])
        jarak_ke_resistance = abs(harga_resistance := zona_resistance['tengah'])

        # Kategori Posisi Harga
        if zona_support['bawah'] <= harga_terakhir <= zona_support['atas']:
            st.success("Kategori: **Rekomendasi Beli Sekarang (Buy Inside Support Zone)**")
            st.write(f"Alasan: Harga (Rp {harga_terakhir:,}) saat ini berada tepat di **Area Support (Rp {zona_support['bawah']:,} - Rp {zona_support['atas']:,})**. Potensi *reversal* memantul naik tinggi.")
            
        elif harga_terakhir < zona_support['bawah']:
            st.error("Kategori: **Jangan Beli / Cut Loss (Breakdown Support)**")
            st.write(f"Alasan: Harga (Rp {harga_terakhir:,}) menembus di bawah rentang support terendah (Rp {zona_support['bawah']:,}). Tren berisiko melanjutkan penurunan.")
            
        elif zona_resistance['bawah'] <= harga_terakhir <= zona_resistance['atas']:
            st.error("Kategori: **Rekomendasi Jual / Take Profit (Inside Resistance Zone)**")
            st.write(f"Alasan: Harga (Rp {harga_terakhir:,}) berada tepat di **Area Resistance (Rp {zona_resistance['bawah']:,} - Rp {zona_resistance['atas']:,})**. Tekanan jual diperkirakan meningkat.")
            
        elif jarak_ke_support < jarak_ke_resistance:
            st.warning("Kategori: **Tunggu di Area Support (Wait and See - Dekat Support)**")
            st.write(f"Alasan: Harga mendekati zona support. Disarankan menanti konfirmasi hingga masuk ke rentang area **Rp {zona_support['bawah']:,} - Rp {zona_support['atas']:,}** sebelum beli.")
            
        else:
            st.info("Kategori: **Hold / Konsolidasi Tengah Tren**")
            st.write("Alasan: Posisi harga berada di area tengah antara Support dan Resistance. Disarankan menahan posisi (*hold*) sampai menyentuh salah satu zona konfirmasi.")

        # 7. Chart Visualisasi Candlestick + HIGHLIGHT LAYER AREA SHADING (Bukan Sekadar Garis Tunggal)
        st.write("---")
        st.subheader("Visualisasi Candlestick & Layer Highlight Area S/R")
        
        fig = go.Figure()

        # A. Layer Shading Highlight Area Support (Warna Hijau Transparan)
        fig.add_shape(
            type="rect",
            xref="paper", yref="y",
            x0=0, x1=1,
            y0=zona_support['bawah'], y1=zona_support['atas'],
            fillcolor="rgba(0, 200, 0, 0.2)",
            line=dict(width=0),
            layer="below"
        )

        # B. Layer Shading Highlight Area Resistance (Warna Merah Transparan)
        fig.add_shape(
            type="rect",
            xref="paper", yref="y",
            x0=0, x1=1,
            y0=zona_resistance['bawah'], y1=zona_resistance['atas'],
            fillcolor="rgba(200, 0, 0, 0.2)",
            line=dict(width=0),
            layer="below"
        )

        # C. Grafik Candlestick
        fig.add_trace(go.Candlestick(
            x=dates,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name='Harga Saham'
        ))

        # D. Garis Putus-Putus Tengah Centroid
        fig.add_trace(go.Scatter(
            x=dates, y=[zona_support['tengah']]*len(dates),
            mode='lines', name=f"Support (Rp {zona_support['tengah']:,})",
            line=dict(dash='dash', color='green', width=1.5)
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=[zona_resistance['tengah']]*len(dates),
            mode='lines', name=f"Resistance (Rp {zona_resistance['tengah']:,})",
            line=dict(dash='dash', color='red', width=1.5)
        ))

        fig.update_layout(
            template="plotly_white",
            xaxis_title="Tanggal",
            yaxis_title="Harga (Rp)",
            xaxis_rangeslider_visible=False,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(f"Gagal memuat data untuk ticker '{ticker_yahoo}'. Pastikan kode saham terdaftar di IDX dan koneksi internet aktif.")