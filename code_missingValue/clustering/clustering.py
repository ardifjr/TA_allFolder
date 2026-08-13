import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import os
import glob
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Path disesuaikan dengan folder proyek missingValue kamu
path_input = r'E:\Semester 7\TA\code_missingValue\preprocesing\standardized_data'
BASE_OUTPUT = r'E:\Semester 7\TA\code_missingValue\clustering'

all_files = glob.glob(os.path.join(path_input, "*.csv"))

def cluster_engine(df, k_target, p_type):
    # Struktur default untuk output zona jika data kosong
    kolom_zona = ['Type', 'Min', 'Max', 'Centroid_Price', 'Std_Internal', 'Strength']
    
    if df.empty or 'Type' not in df.columns or 'Z_Score' not in df.columns:
        return df, pd.DataFrame(columns=kolom_zona)

    sub_df = df[df['Type'] == p_type].copy()
    
    # PENANGANAN UTAMA: Jika data kosong atau kurang dari 1
    if sub_df.empty or len(sub_df) == 0:
        return sub_df, pd.DataFrame([{
            'Type': p_type, 'Min': 0, 'Max': 0, 
            'Centroid_Price': 0, 'Std_Internal': 0.0, 'Strength': 0
        }], columns=kolom_zona)

    # Penyesuaian K dinamis agar K-Means tidak error saat data < K
    n_unique = sub_df['Z_Score'].nunique()
    k_actual = min(k_target, len(sub_df), n_unique)
    
    if k_actual < 1:
        k_actual = 1

    X = sub_df['Z_Score'].values.reshape(-1, 1)
    
    # Eksekusi K-Means
    try:
        kmeans = KMeans(n_clusters=k_actual, n_init='auto', random_state=42)
        sub_df['Cluster'] = kmeans.fit_predict(X)
        centroids_z = kmeans.cluster_centers_.flatten()
    except Exception:
        sub_df['Cluster'] = 0
        centroids_z = np.array([sub_df['Z_Score'].mean()])
        k_actual = 1

    mean_ref = sub_df['Mean_Reference'].iloc[0] if 'Mean_Reference' in sub_df.columns else 0.0
    std_ref  = sub_df['Std_Reference'].iloc[0] if 'Std_Reference' in sub_df.columns else 0.0
    
    if np.isnan(mean_ref): mean_ref = 0.0
    if np.isnan(std_ref): std_ref = 0.0

    zona_list = []
    for c in range(k_actual):
        cluster_data = sub_df[sub_df['Cluster'] == c]
        if not cluster_data.empty:
            c_price = (centroids_z[c] * std_ref) + mean_ref
            sigma_internal = cluster_data['Level'].std() if len(cluster_data) > 1 else 0.0
            if np.isnan(sigma_internal): sigma_internal = 0.0
            
            c_price_int = int(round(c_price, 0)) if not np.isnan(c_price) else 0
            sig_int = round(sigma_internal, 2)
            
            zona_list.append({
                'Type':           p_type,
                'Min':            int(round(c_price - sigma_internal, 0)) if not np.isnan(c_price) else 0,
                'Max':            int(round(c_price + sigma_internal, 0)) if not np.isnan(c_price) else 0,
                'Centroid_Price': c_price_int,
                'Std_Internal':   sig_int,
                'Strength':       len(cluster_data),
                'Temp_Sort':      c_price if not np.isnan(c_price) else 0
            })
            
    df_zona = pd.DataFrame(zona_list)
    return sub_df, df_zona


print("Fase 1: Memasukkan SELURUH 41 emiten ke dalam daftar baseline (Tanpa Eliminasi)...")

emiten_semua = []
for file in all_files:
    file_name = os.path.basename(file)
    ticker = file_name.split('_')[0]
    emiten_semua.append(ticker)

emiten_konsisten_final = sorted(list(set(emiten_semua)))

print(f"Selesai! Berhasil mengunci TOTAL {len(emiten_konsisten_final)} emiten sebagai baseline.")
print(f"Daftar 41 emiten: {emiten_konsisten_final}\n")

os.makedirs(BASE_OUTPUT, exist_ok=True)
with open(os.path.join(BASE_OUTPUT, 'emiten_lolos_sensor.txt'), 'w') as f:
    for ticker in emiten_konsisten_final:
        f.write(f"{ticker}\n")


print("Fase 2: Menjalankan K-Means Clustering untuk K=2 s/d K=10 (100% 41 Emiten Diproses)")

for K_VALUE in range(2, 11):
    path_output_detail = os.path.join(BASE_OUTPUT, f'k{K_VALUE}', 'detail')
    path_output_zona   = os.path.join(BASE_OUTPUT, f'k{K_VALUE}', 'summary_zona')
    
    for p in [path_output_detail, path_output_zona]:
        os.makedirs(p, exist_ok=True)

    print(f"\n{'='*65}")
    print(f" MEMPROSES CLUSTERING K = {K_VALUE} (Total: {len(all_files)} File)")
    print(f"{'='*65}")

    saved   = 0

    for file in all_files:
        file_name = os.path.basename(file)
        
        try:
            df_raw = pd.read_csv(file)
        except Exception:
            df_raw = pd.DataFrame()
        
        df_s_detail, df_s_zona = cluster_engine(df_raw, K_VALUE, 'Support')
        df_r_detail, df_r_zona = cluster_engine(df_raw, K_VALUE, 'Resistance')
        
        # Gabungkan Detail
        df_final_detail = pd.concat([df_s_detail, df_r_detail], ignore_index=True)
        if 'Tanggal' in df_final_detail.columns and not df_final_detail.empty:
            df_final_detail = df_final_detail.sort_values('Tanggal')
            
        # Gabungkan Summary Zona
        df_final_zona = pd.concat([df_s_zona, df_r_zona], ignore_index=True)
        if not df_final_zona.empty and 'Temp_Sort' in df_final_zona.columns:
            df_final_zona = (df_final_zona.sort_values(['Type', 'Temp_Sort'])
                                         .drop(columns=['Temp_Sort'], errors='ignore'))
        
        # Simpan File Ke Folder K
        df_final_detail.to_csv(os.path.join(path_output_detail, file_name), index=False)
        df_final_zona.to_csv(os.path.join(path_output_zona, file_name), index=False)
        saved += 1

    print(f" Hasil K={K_VALUE} → {saved}/{len(all_files)} Emiten Berhasil Disimpan 100%.")

print(f"\n{'='*65}")
print(" PIPELINE CLUSTERING SELESAI TANPA ADA EMITEN YANG TERBUANG!")
print(f" Output tersimpan rapi di: {BASE_OUTPUT}\\k2 … k10")
print(f" Bukti 41 emiten dicatat di: {BASE_OUTPUT}\\emiten_lolos_sensor.txt")
print(f"{'='*65}")