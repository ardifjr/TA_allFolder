import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns

path_evaluation = r'E:\Semester 7\TA\code_komparasi\evaluation'

csv_files = glob.glob(os.path.join(path_evaluation, "summary_metrics_k*.csv"))

if len(csv_files) == 0:
    print("ERROR: Tidak ditemukan file 'summary_metrics_k*.csv' di folder evaluation.")
    print("Pastikan kamu sudah menjalankan script 'backtesting_loop.py' terlebih dahulu.")
    exit()

rekap_sektoral = []

for file_path in csv_files:
    file_name = os.path.basename(file_path)
    
    try:
        k_val = int(file_name.split('_k')[-1].split('.csv')[0])
    except ValueError:
        continue
        
    df_metrics = pd.read_csv(file_path)
    
    if df_metrics.empty:
        continue
        
    avg_accuracy = df_metrics['Accuracy'].mean()
    avg_precision = df_metrics['Precision'].mean()
    avg_recall = df_metrics['Recall'].mean()
    avg_f1 = df_metrics['F1_Score'].mean()
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

df_summary = pd.DataFrame(rekap_sektoral).sort_values('Int_K').reset_index(drop=True)

print("\n" + "="*85)
print("REKAPITULASI RATA-RATA FINAL PERFORMA SEKTORAL ENERGI (K2 - K10)")
print("="*85)

print(f"{'Skenario':<10} | {'Emiten':<6} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
print("-"*85)
for _, row in df_summary.iterrows():
    print(f"{row['K_Value']:<10} | {row['Jumlah_Emiten']:<6} | {row['Avg_Accuracy']:10.4f} | {row['Avg_Precision']:10.4f} | {row['Avg_Recall']:10.4f} | {row['Avg_F1_Score']:10.4f}")
print("-"*85)

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

print("Memunculkan jendela grafis perbandingan metrik...")

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

plt.plot(df_summary['Int_K'], df_summary['Avg_Accuracy'], marker='o', linewidth=2, label='Accuracy', color='#1f77b4')
plt.plot(df_summary['Int_K'], df_summary['Avg_Precision'], marker='s', linewidth=2, label='Precision', color='#2ca02c')
plt.plot(df_summary['Int_K'], df_summary['Avg_Recall'], marker='^', linewidth=2, label='Recall', color='#ff7f0e')
plt.plot(df_summary['Int_K'], df_summary['Avg_F1_Score'], marker='D', linewidth=3, label='F1-Score (Utama)', color='#d62728')

plt.axvline(x=best_model['Int_K'], color='red', linestyle='--', alpha=0.7, 
            label=f"Optimal Target ({best_model['K_Value']})")

plt.title('Grafik Tren Komparasi Metrik Evaluasi Model Sektoral (K2 - K10)', fontsize=13, pad=15, weight='bold')
plt.xlabel('Nilai Klaster (Parameter K K-Means)', fontsize=11, labelpad=10)
plt.ylabel('Nilai Rata-Rata Metrik (Skala 0.0 - 1.0)', fontsize=11, labelpad=10)
plt.xticks(df_summary['Int_K'])
plt.ylim(0.0, 1.0) 

plt.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='gray')
plt.tight_layout()

graph_save_path = os.path.join(path_evaluation, "tren_komparasi_metrik_k.png")
plt.savefig(graph_save_path, dpi=300)
print(f"Grafik berhasil disimpan di: {graph_save_path}")

plt.show()