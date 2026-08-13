import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns

# ================= CONFIGURATION =================
path_evaluation = r'E:\Semester 7\TA\code_bank\evaluation'

# Cari semua file summary_metrics_k*.csv di folder evaluation
csv_files = glob.glob(os.path.join(path_evaluation, "summary_metrics_k*.csv"))

if len(csv_files) == 0:
    print("ERROR: Tidak ditemukan file 'summary_metrics_k*.csv' di folder evaluation.")
    print("Pastikan kamu sudah menjalankan script 'backtesting_loop.py' terlebih dahulu.")
    exit()

rekap_sektoral = []

# ================= LOOP READING DATA =================
for file_path in csv_files:
    file_name = os.path.basename(file_path)
    
    # Ekstrak nilai K dari nama file (misal: summary_metrics_k3.csv -> K = 3)
    try:
        k_val = int(file_name.split('_k')[-1].split('.csv')[0])
    except ValueError:
        continue
        
    df_metrics = pd.read_csv(file_path)
    
    if df_metrics.empty:
        continue
        
    # Tangani MultiIndex jika kolom terbungkus multi-level
    if isinstance(df_metrics.columns, pd.MultiIndex):
        df_metrics.columns = df_metrics.columns.get_level_values(0)
        
    # Bersihkan spasi tak terlihat pada nama kolom
    df_metrics.columns = df_metrics.columns.str.strip()
    
    # FIX: Validasi menggunakan kolom bahasa Indonesia yang ada di file kamu
    required_cols = ['Akurasi_Total', 'Ketepatan_Prediksi', 'Daya_Tangkap_Model', 'Skor_Keseimbangan_F1']
    missing_cols = [col for col in required_cols if col not in df_metrics.columns]
    if missing_cols:
        print(f"\n[!] File {file_name} dilewati karena kolom ini hilang: {missing_cols}")
        print(f"    Kolom yang terdeteksi di dalam file: {list(df_metrics.columns)}")
        continue
        
    # Hitung rata-rata sektoral menggunakan nama kolom bahasa Indonesia
    avg_accuracy = df_metrics['Akurasi_Total'].mean()
    avg_precision = df_metrics['Ketepatan_Prediksi'].mean()
    avg_recall = df_metrics['Daya_Tangkap_Model'].mean()
    avg_f1 = df_metrics['Skor_Keseimbangan_F1'].mean()
    total_emiten = len(df_metrics)
    
    rekap_sektoral.append({
        'K_Value': f"K = {k_val}",
        'Int_K': k_val,
        'Avg_Accuracy': avg_accuracy,
        'Avg_Precision': avg_precision,
        'Avg_Recall': avg_recall,
        'Avg_F1_Score': avg_f1,
        'Jumlah_Emiten': total_emiten
    })

if not rekap_sektoral:
    print("\n[ERROR] Tidak ada data valid yang berhasil direkap. Periksa kembali struktur file CSV kamu.")
    exit()

# Ubah ke DataFrame dan urutkan berdasarkan nilai K terkecil ke terbesar untuk tampilan tabel
df_summary = pd.DataFrame(rekap_sektoral).sort_values('Int_K').reset_index(drop=True)

# ================= OUTPUT RESULTS (TERMINAL) =================
print("\n" + "="*85)
print("REKAPITULASI RATA-RATA FINAL PERFORMA SEKTORAL ENERGI (K2 - K10)")
print("="*85)

# Cetak tabel ringkasan
print(f"{'Skenario':<10} | {'Emiten':<6} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
print("-"*85)
for _, row in df_summary.iterrows():
    print(f"{row['K_Value']:<10} | {row['Jumlah_Emiten']:<6} | {row['Avg_Accuracy']:10.4f} | {row['Avg_Precision']:10.4f} | {row['Avg_Recall']:10.4f} | {row['Avg_F1_Score']:10.4f}")
print("-"*85)

# --- PENENTUAN MODEL TERBAIK BERDASARKAN F1-SCORE ---
best_model = df_summary.loc[df_summary['Avg_F1_Score'].idxmax()]

print("\nKESIMPULAN OPTIMALISASI NILAI K UNTUK BAB 5:")
print("-" * 55)
print(f"Model Klaster Paling Optimal : {best_model['K_Value']}")
print(f"Rata-Rata F1-Score Sektoral : {best_model['Avg_F1_Score']:.4f} ({round(best_model['Avg_F1_Score']*100, 2)}%)")
print(f"Rata-Rata Akurasi Sektoral  : {best_model['Avg_Accuracy']:.4f} ({round(best_model['Avg_Accuracy']*100, 2)}%)")
print("-" * 55)
print(f"REKOMENDASI: Gunakan konfigurasi {best_model['K_Value']} sebagai parameter final")
print("   pada sistem Support & Resistance Algoritma K-Means kamu!")
print("="*85 + "\n")

# ================= AUTOMATED GUI GRAPH VISUALIZATION =================
print("Memunculkan jendela grafis perbandingan metrik...")

# Set style seaborn agar visualisasi terlihat modern, clean, dan elegant
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

# Plot masing-masing metrik evaluasi ke dalam satu chart garis
plt.plot(df_summary['Int_K'], df_summary['Avg_Accuracy'], marker='o', linewidth=2, label='Accuracy', color='#1f77b4')
plt.plot(df_summary['Int_K'], df_summary['Avg_Precision'], marker='s', linewidth=2, label='Precision', color='#2ca02c')
plt.plot(df_summary['Int_K'], df_summary['Avg_Recall'], marker='^', linewidth=2, label='Recall', color='#ff7f0e')
plt.plot(df_summary['Int_K'], df_summary['Avg_F1_Score'], marker='D', linewidth=3, label='F1-Score (Utama)', color='#d62728')

# Highlight titik K paling optimal dengan lingkaran putus-putus vertikal
plt.axvline(x=best_model['Int_K'], color='red', linestyle='--', alpha=0.7, 
            label=f"Optimal Target ({best_model['K_Value']})")

# Konfigurasi kelayakan estetika grafik untuk kebutuhan dokumen skripsi
plt.title('Grafik Tren Komparasi Metrik Evaluasi Model Sektoral (K2 - K10)', fontsize=13, pad=15, weight='bold')
plt.xlabel('Nilai Klaster (Parameter K K-Means)', fontsize=11, labelpad=10)
plt.ylabel('Nilai Rata-Rata Metrik (Skala 0.0 - 1.0)', fontsize=11, labelpad=10)
plt.xticks(df_summary['Int_K']) # Memastikan sumbu X hanya memunculkan angka bulat K
plt.ylim(0.0, 1.0) # Skala persentase konvensional

# Tampilkan legenda penanda warna di pojok kanan atas
plt.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='gray')
plt.tight_layout()

# 1. Simpan grafik secara otomatis ke dalam folder evaluation untuk Bab 4
graph_save_path = os.path.join(path_evaluation, "tren_komparasi_metrik_k.png")
plt.savefig(graph_save_path, dpi=300)
print(f"Grafik berhasil disimpan di: {graph_save_path}")

# 2. Munculkan window pop-up GUI interaktif ke layar monitor
plt.show()