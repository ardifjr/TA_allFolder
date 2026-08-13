import pandas as pd
import numpy as np
import os
import glob
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

warnings.filterwarnings("ignore", category=UserWarning)

# Path disesuaikan dengan folder proyek missingValue kamu
path_testing = r'E:\Semester 7\TA\code_missingValue\testing'
base_path_scoring = r'E:\Semester 7\TA\code_missingValue\clustering\scoring'
path_output_eval = r'E:\Semester 7\TA\code_missingValue\evaluation'  

if not os.path.exists(path_output_eval): 
    os.makedirs(path_output_eval)

k_variants = [2, 3, 4, 5, 6, 7, 8, 9, 10]

def evaluate_testing_data(df_test, df_zona):
    """
    Membaca baris data testing satu per satu (kronologis) dan mencocokkannya 
    dengan batas dinamis K-Means untuk mendeteksi sinyal klasifikasi pasar.
    """
    y_true = []  
    y_pred = []  
    
    # Keamanan jika data testing atau df_zona kosong
    if df_test.empty or len(df_test) < 4 or df_zona.empty:
        return [0], [0]

    total_rows = len(df_test)
    
    # Filter zona: gunakan Ranking == 1 jika kolom tersedia, jika tidak gunakan seluruh zona
    if 'Ranking' in df_zona.columns:
        df_target_zona = df_zona[df_zona['Ranking'] == 1]
        if df_target_zona.empty:
            df_target_zona = df_zona
    else:
        df_target_zona = df_zona

    for i in range(total_rows - 3):
        row = df_test.iloc[i]
        next_days = df_test.iloc[i+1 : i+4]
        
        signal_triggered = False
        
        for _, zone in df_target_zona.iterrows():
            min_val = zone.get('Min', 0)
            max_val = zone.get('Max', 0)
            z_type = zone.get('Type', '')

            if z_type == 'Support':
                if min_val <= row.get('Low', 0) <= max_val:
                    y_pred.append(1)
                    signal_triggered = True
                    jebol = any(next_days['Low'] < min_val) if 'Low' in next_days.columns else False
                    y_true.append(0 if jebol else 1)
                    break
                        
            elif z_type == 'Resistance':
                if min_val <= row.get('High', 0) <= max_val:
                    y_pred.append(1)
                    signal_triggered = True
                    jebol = any(next_days['High'] > max_val) if 'High' in next_days.columns else False
                    y_true.append(0 if jebol else 1)
                    break
        
        if not signal_triggered:
            if i >= 2 and i < total_rows - 2:
                is_local_bottom = row.get('Low', 0) == df_test.iloc[i-2:i+3]['Low'].min() if 'Low' in df_test.columns else False
                is_local_top = row.get('High', 0) == df_test.iloc[i-2:i+3]['High'].max() if 'High' in df_test.columns else False
                
                if is_local_bottom or is_local_top:
                    y_pred.append(0)  
                    y_true.append(1)  
                else:
                    y_pred.append(0)  
                    y_true.append(0)

    # Fallback jika tidak ada sinyal sama sekali
    if len(y_pred) == 0:
        y_pred = [0]
        y_true = [0]

    return y_true, y_pred

print("=== Memulai Algorithmic Backtesting Otomatis Berkelanjutan (K2 - K10) ===")

for k in k_variants:
    path_scoring_zona = os.path.join(base_path_scoring, f'k{k}')
    zona_files = glob.glob(os.path.join(path_scoring_zona, "*.csv"))
    
    if len(zona_files) == 0:
        print(f"Folder data scoring K={k} kosong atau tidak ditemukan. Dilewati.")
        continue
        
    print(f"\n" + "="*80)
    print(f"MENGEKSEKUSI PENGUJIAN MODEL EMPIRIS UNTUK SKENARIO K = {k}")
    print("="*80)
    
    all_metrics = []
    
    for file in zona_files:
        file_name = os.path.basename(file)
        ticker = file_name.split('_')[0]
        
        # PERBAIKAN: Gunakan wildcard matching agar nama file testing otomatis ketemu
        test_file_matches = glob.glob(os.path.join(path_testing, f"{ticker}_*.csv"))
        
        if not test_file_matches: 
            print(f"File testing untuk emiten {ticker} tidak ditemukan di folder testing. Dilewati.")
            continue
            
        test_file_path = test_file_matches[0]
            
        try:
            df_zona = pd.read_csv(file)
            df_test = pd.read_csv(test_file_path)
        except Exception:
            df_zona = pd.DataFrame()
            df_test = pd.DataFrame()
        
        y_true, y_pred = evaluate_testing_data(df_test, df_zona)
        
        pantulan_tepat = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1) # TP
        zona_jebol = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)     # FP
        pantulan_terlewat = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0) # FN
        abaikan_valid = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)     # TN

        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        accuracy = accuracy_score(y_true, y_pred)
        
        all_metrics.append({
            'Emiten': ticker, 
            'Pantulan_Tepat': pantulan_tepat, 
            'Zona_Jebol': zona_jebol, 
            'Pantulan_Terlewat': pantulan_terlewat, 
            'Abaikan_Valid': abaikan_valid,
            'Accuracy': round(accuracy, 4), 
            'Precision': round(precision, 4),
            'Recall': round(recall, 4), 
            'F1_Score': round(f1, 4)
        })

    if len(all_metrics) > 0:
        df_results = pd.DataFrame(all_metrics)
        
        summary_save_path = os.path.join(path_output_eval, f"summary_metrics_k{k}.csv")
        df_results.to_csv(summary_save_path, index=False)
        
        final_tp = df_results['Pantulan_Tepat'].sum()
        final_fp = df_results['Zona_Jebol'].sum()
        final_fn = df_results['Pantulan_Terlewat'].sum()
        final_tn = df_results['Abaikan_Valid'].sum()
        
        cm_matrix = np.array([[final_tp, final_fp],
                              [final_fn, final_tn]])
        
        plt.figure(figsize=(7, 6))
        labels = ['Reversal (Zona Aktif)', 'Breakout / No Sinyal']
        
        sns.heatmap(cm_matrix, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=labels, yticklabels=labels, cbar=True,
                    annot_kws={"size": 13, "weight": "bold"})
        
        # PERBAIKAN: Judul Confusion Matrix disesuaikan
        plt.title(f'Confusion Matrix Evaluasi Sektoral (K={k})', fontsize=13, pad=15, weight='bold')
        plt.ylabel('Realita Pergerakan Pasar (True Label)', fontsize=11)
        plt.xlabel('Prediksi Model Zona K-Means (Predicted Label)', fontsize=11)
        plt.tight_layout()
        
        graph_save_path = os.path.join(path_output_eval, f"confusion_matrix_k{k}.png")
        plt.savefig(graph_save_path, dpi=300)
        plt.close()
        
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', 1000)
        
        print(f"TABEL EVALUASI PERFORMA MODEL PER EMITEN (K={k}):")
        print("-" * 115)
        print(df_results.to_string(index=False))
        print("-" * 115)
        
        print(f"\nRINGKASAN MATRIKS AKUMULASI SEKTORAL K={k}:")
        print(f" * Pantulan Tepat Target (TP) : {final_tp} kali")
        print(f" * Zona Jebol/Breakout (FP)   : {final_fp} kali")
        print(f" * Pantulan Terlewat (FN)     : {final_fn} kali")
        print(f" * Abaikan Valid (TN)         : {final_tn} kali")
        
        print(f"\nRATA-RATA SEKTORAL K={k}:")
        print(df_results[['Accuracy', 'Precision', 'Recall', 'F1_Score']].mean().to_string())
        print(f"\nBerkas disimpan: \n  {summary_save_path}\n  {graph_save_path}\n")
    else:
        print(f"Gagal memproses pengujian untuk skenario K={k}. Periksa kesiapan data Anda.")

print("\n" + "="*80)
print("SELESAI! Seluruh skenario K2 s/d K10 sukses dievaluasi secara flat di folder evaluation.")
print("="*80)