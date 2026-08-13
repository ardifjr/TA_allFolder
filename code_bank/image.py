import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Membuat Data Pergerakan Harga Saham Historis (Realistis)
np.random.seed(150)
n_days = 150
prices = 1000 + np.cumsum(np.random.normal(loc=0.2, scale=25, size=n_days)) + 120 * np.sin(np.linspace(0, 3 * np.pi, n_days))

df = pd.DataFrame({
    'Hari': np.arange(n_days),
    'Close_Price': prices
})

# 2. Pengaturan Tampilan Grafik
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(11, 6), dpi=150)

# Plot Utama: Harga Saham Historis
ax.plot(df['Hari'], df['Close_Price'], color='#708090', linewidth=2, label='Harga Saham Historis')

# --- SIMULASI SUBJEKTIVITAS ANALIS KONVENSIONAL (Garis Kaku & Berbeda-beda) ---
# Ceritanya para analis konvensional menarik garis di puncak/lembah yang berbeda secara subjektif
ax.axhline(y=1180, color='#FF5733', linestyle=':', linewidth=1.5, label='Garis Resistance (Analis A - Subjektif)')
ax.axhline(y=1220, color='#C70039', linestyle=':', linewidth=1.5, label='Garis Resistance (Analis B - Subjektif)')

ax.axhline(y=910, color='#900C3F', linestyle=':', linewidth=1.5, label='Garis Support (Analis C - Subjektif)')
ax.axhline(y=860, color='#581845', linestyle=':', linewidth=1.5, label='Garis Support (Analis D - Subjektif)')


# --- SIMULASI MODEL SEBENARNYA (Zona Rentang Dinamis K-Means Ardi) ---
# Area Resistance K-Means (Berbasis titik kumpul riil)
ax.axhspan(1130, 1165, color='#1B365D', alpha=0.25, label='Zona Pemetaan Objektif (Model K-Means Ardi)')
# Area Support K-Means (Berbasis titik kumpul riil)
ax.axhspan(930, 965, color='#1B365D', alpha=0.25)


# 3. Plot Marker Titik Pantul Riil (Pivot Points yang ditangkap sistem)
# Menambahkan sedikit titik merah/biru untuk memperjelas kenapa zona K-Means terbentuk di sana
puncak_riil = [35, 110]
lembah_riil = [70, 140]
ax.scatter(df['Hari'].iloc[puncak_riil], df['Close_Price'].iloc[puncak_riil], color='#1B365D', marker='^', s=50, zorder=5)
ax.scatter(df['Hari'].iloc[lembah_riil], df['Close_Price'].iloc[lembah_riil], color='#1B365D', marker='v', s=50, zorder=5)

# Formatting Teks dan Estetika Grafik
ax.set_title('Perbandingan Visual: Garis Kaku Analis Konvensional vs Zona Dinamis Objektif', fontsize=12, pad=15, fontweight='bold', color='#333333')
ax.set_xlabel('Garis Waktu Perdagangan (Hari)', fontsize=10, labelpad=8)
ax.set_ylabel('Harga Saham (Rupiah)', fontsize=10, labelpad=8)

# Merapikan posisi legenda agar tidak menutupi chart
ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#E0E0E0', fontsize=9)
plt.tight_layout()

# Simpan sebagai aset gambar
plt.savefig('subjektivitas_vs_objektif_kmeans.png', dpi=300, bbox_inches='tight')
plt.show()