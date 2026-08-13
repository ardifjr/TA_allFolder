import pandas as pd
import numpy as np
import os
import glob
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

warnings.filterwarnings("ignore", category=UserWarning)

# ================= CONFIGURATION =================
path_testing = r'E:\Semester 7\TA\code_bank\testing'
base_path_scoring = r'E:\Semester 7\TA\code_bank\clustering\scoring'
path_output_eval = r'E:\Semester 7\TA\code_bank\evaluation'  # Penyimpanan langsung flat di folder ini

if not os.path.exists(path_output_eval): 
    os.makedirs(path_output_eval)

# Array skenario K dinamis dari K=2 sampai K=10 sesuai alur pipeline terpadu
k_variants = [2, 3, 4, 5, 6, 7, 8, 9, 10]

def evaluate_testing_data(df_test, df_zona):
    """
    Membaca baris data testing satu per satu (kronologis) dan mencocokkannya 
    dengan batas dinamis K-Means untuk mendeteksi sinyal klasifikasi pasar.
    """
    y_true = []  # 1: Berbalik Arah (Sesuai Prediksi), 0: Jebol / Tidak Ada Perubahan
    y_pred = []  # 1: Model Memprediksi Harga Berbalik, 0: Model Memprediksi Harga Stabil (Luar Jangkauan)
    
    total_rows = len(df_test)
    
    for i in range(total_rows - 3):
        row = df_test.iloc[i]
        next_days = df_test.iloc[i+1 : i+4]
        
        signal_triggered = False
        
        # Evaluasi hanya berbasis Zona Berperingkat Terkuat (Ranking == 1) hasil pembobotan
        df_rank1 = df_zona[df_zona['Ranking'] == 1]
        
        for _, zone in df_rank1.iterrows():
            # --- A. EVALUASI BATAS BAWAH (SUPPORT) ---
            if zone['Type'] == 'Support':
                if zone['Min'] <= row['Low'] <= zone['Max']:
                    y_pred.append(1)
                    signal_triggered = True
                    jebol = any(next_days['Low'] < zone['Min'])
                    y_true.append(0 if jebol else 1)
                    break
                        
            # --- B. EVALUASI BATAS ATAS (RESISTANCE) ---
            elif zone['Type'] == 'Resistance':
                if zone['Min'] <= row['High'] <= zone['Max']:
                    y_pred.append(1)
                    signal_triggered = True
                    jebol = any(next_days['High'] > zone['Max'])
                    y_true.append(0 if jebol else 1)
                    break
        
        # --- C. DETEKSI DI LUAR JANGKAUAN ZONA (NEGATIVE CLASS) ---
        if not signal_triggered:
            if i >= 2 and i < total_rows - 2:
                is_local_bottom = row['Low'] == df_test.iloc[i-2:i+3]['Low'].min()
                is_local_top = row['High'] == df_test.iloc[i-2:i+3]['High'].max()
                
                if is_local_bottom or is_local_top:
                    y_pred.append(0)  
                    y_true.append(1)  # Menjadi FN (Perubahan Arah Terlewat)
                else:
                    y_pred.append(0)  
                    y_true.append(0)  # Menjadi TN (Harga Stabil / Wajar)

    return y_true, y_pred

# ================= AUTOMATED LOOP EXECUTION =================
print("=== Memulai Analisis Pengujian Otomatis Berkelanjutan (K2 - K10) ===")

for k in k_variants:
    path_scoring_zona = os.path.join(base_path_scoring, f'k{k}')
    zona_files = glob.glob(os.path.join(path_scoring_zona, "*.csv"))
    
    if len(zona_files) == 0:
        print(f"⚠️ Folder data scoring K={k} kosong atau tidak ditemukan. Dilewati.")
        continue
        
    print(f"\n" + "="*80)
    print(f"🔄 MENGEKSEKUSI PENGUJIAN MODEL EMPIRIS UNTUK SKENARIO K = {k}")
    print("="*80)
    
    all_metrics = []
    
    for file in zona_files:
        file_name = os.path.basename(file)
        ticker = file_name.split('_')[0]
        
        test_file_name = f"{ticker}_2023-12-26_to_2025-12-26.csv"
        test_file_path = os.path.join(path_testing, test_file_name)
        
        if not os.path.exists(test_file_path): 
            continue
            
        df_zona = pd.read_csv(file)
        df_test = pd.read_csv(test_file_path)
        
        y_true, y_pred = evaluate_testing_data(df_test, df_zona)
        
        if len(y_pred) == 0: 
            continue
            
        # --- KALKULASI MANUAL KOMPONEN MATRIKS EVALUASI ---
        tebakan_tepat = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)      # TP
        prediksi_meleset = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)   # FP
        perubahan_terlewat = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0) # FN
        kondisi_stabil = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)     # TN

        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        accuracy = accuracy_score(y_true, y_pred)
        
        all_metrics.append({
            'Emiten': ticker, 
            'Tebakan_Tepat': tebakan_tepat, 
            'Prediksi_Meleset': prediksi_meleset, 
            'Perubahan_Terlewat': perubahan_terlewat, 
            'Kondisi_Stabil': kondisi_stabil,
            'Akurasi_Total': round(accuracy, 4), 
            'Ketepatan_Prediksi': round(precision, 4),
            'Daya_Tangkap_Model': round(recall, 4), 
            'Skor_Keseimbangan_F1': round(f1, 4)
        })

    # --- SAVE & OUTPUT PER VARIASI KASI NILAI K ---
    if len(all_metrics) > 0:
        df_results = pd.DataFrame(all_metrics)
        
        # Penamaan file flat langsung di bawah folder evaluation memakai suffix _k
        summary_save_path = os.path.join(path_output_eval, f"summary_metrics_k{k}.csv")
        df_results.to_csv(summary_save_path, index=False)
        
        # Accumulate matriks total sektoral untuk gambar grafik
        final_tp = df_results['Tebakan_Tepat'].sum()
        final_fp = df_results['Prediksi_Meleset'].sum()
        final_fn = df_results['Perubahan_Terlewat'].sum()
        final_tn = df_results['Kondisi_Stabil'].sum()
        
        cm_matrix = np.array([[final_tp, final_fp],
                              [final_fn, final_tn]])
        
        # Pembuatan Grafik Heatmap Real Matriks dengan Keterangan Jelas
        plt.figure(figsize=(7, 6))
        labels = ['Berbalik Arah (Aktif)', 'Jebol / Harga Stabil']
        
        sns.heatmap(cm_matrix, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=labels, yticklabels=labels, cbar=True,
                    annot_kws={"size": 13, "weight": "bold"})
        
        plt.title(f'Matriks Evaluasi Sektoral Energi (K={k})', fontsize=13, pad=15, weight='bold')
        plt.ylabel('Kondisi Nyata Pasar (Kebenaran)', fontsize=11)
        plt.xlabel('Hasil Prediksi Model (Tebakan)', fontsize=11)
        plt.tight_layout()
        
        # Menyimpan grafik flat langsung dengan name akhiran _k
        graph_save_path = os.path.join(path_output_eval, f"confusion_matrix_k{k}.png")
        plt.savefig(graph_save_path, dpi=300)
        plt.close()
        
        # Cetak Tabel Hasil ke Layar Command Line
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', 1000)
        
        print(f"📋 TABEL EVALUASI PERFORMA MODEL PER EMITEN (K={k}):")
        print("-" * 125)
        print(df_results.to_string(index=False))
        print("-" * 125)
        
        print(f"\n📊 RINGKASAN MATRIKS AKUMULASI SEKTORAL K={k}:")
        print(f" * Tebakan Tepat Target (TP)      : {final_tp} kali")
        print(f" * Prediksi Meleset/Jebol (FP)    : {final_fp} kali")
        print(f" * Perubahan Arah Terlewat (FN)   : {final_fn} kali")
        print(f" * Kondisi Pasar Stabil (TN)      : {final_tn} kali")
        
        print(f"\n🎯 RATA-RATA KESELURUHAN K={k}:")
        print(df_results[['Akurasi_Total', 'Ketepatan_Prediksi', 'Daya_Tangkap_Model', 'Skor_Keseimbangan_F1']].mean().to_string())
        print(f"\n💾 Berkas disimpan: \n ➡️ {summary_save_path}\n ➡️ {graph_save_path}\n")
    else:
        print(f"❌ Gagal memproses pengujian untuk skenario K={k}. Periksa kesiapan data Anda.")

print("\n" + "="*80)
print("✨ SELESAI! Seluruh skenario K2 s/d K10 sukses dievaluasi secara flat di folder evaluation.")
print("="*80)