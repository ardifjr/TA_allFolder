import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import os
import glob
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# ================= CONFIGURATION =================
path_input = r'E:\Semester 7\TA\code_bank\preprocesing\standardized_data'
BASE_OUTPUT = r'E:\Semester 7\TA\code_bank\clustering'

all_files = glob.glob(os.path.join(path_input, "*.csv"))

def cluster_engine(df, k, p_type):
    """Proses clustering K-Means dengan batas dinamis Centroid +/- 1 Std Dev Internal"""
    sub_df = df[df['Type'] == p_type].copy()
    
    # Proteksi matematika K-Means agar tidak error jika variasi data unik kurang dari K
    if len(sub_df) < k or sub_df['Z_Score'].nunique() < k:
        return pd.DataFrame(), pd.DataFrame()

    X = sub_df['Z_Score'].values.reshape(-1, 1)
    kmeans = KMeans(n_clusters=k, n_init='auto', random_state=42)
    sub_df['Cluster'] = kmeans.fit_predict(X)
    
    mean_ref = sub_df['Mean_Reference'].iloc[0]
    std_ref  = sub_df['Std_Reference'].iloc[0]
    centroids_z = kmeans.cluster_centers_.flatten()
    
    zona_list = []
    for c in range(k):
        cluster_data = sub_df[sub_df['Cluster'] == c]
        if not cluster_data.empty:
            c_price = (centroids_z[c] * std_ref) + mean_ref
            sigma_internal = cluster_data['Level'].std() if len(cluster_data) > 1 else 0.0
            
            zona_list.append({
                'Type':           p_type,
                'Min':            int(round(c_price - sigma_internal, 0)),
                'Max':            int(round(c_price + sigma_internal, 0)),
                'Centroid_Price': int(round(c_price, 0)),
                'Std_Internal':   round(sigma_internal, 2),
                'Strength':       len(cluster_data),
                'Temp_Sort':      c_price
            })
            
    return sub_df, pd.DataFrame(zona_list)


# ================= FASE 1: SCANNING EMITEN YANG KONSISTEN (INTERSECTION) =================
print("🔍 Fase 1: Memindai irisan emiten yang selalu lolos kriteria dari K=2 s/d K=10...")

emiten_lolos_per_k = {k: set() for k in range(2, 11)}

for K_VALUE in range(2, 11):
    for file in all_files:
        file_name = os.path.basename(file)
        ticker = file_name.split('_')[0]
        df_raw = pd.read_csv(file)
        
        # Cek ketersediaan data secara virtual tanpa menyimpan file
        sub_s = df_raw[df_raw['Type'] == 'Support']
        sub_r = df_raw[df_raw['Type'] == 'Resistance']
        
        cond_s = len(sub_s) >= K_VALUE and sub_s['Z_Score'].nunique() >= K_VALUE
        cond_r = len(sub_r) >= K_VALUE and sub_r['Z_Score'].nunique() >= K_VALUE
        
        if cond_s and cond_r:
            emiten_lolos_per_k[K_VALUE].add(ticker)

# Cari irisan (Intersection) emiten yang selalu True di semua nilai K (pasti menghasilkan 26 emiten)
emiten_konsisten_final = set.intersection(*emiten_lolos_per_k.values())
emiten_konsisten_final = sorted(list(emiten_konsisten_final))

print(f"🎯 Selesai! Ditemukan {len(emiten_konsisten_final)} emiten yang 100% konsisten memenuhi syarat K2-K10.")
print(f"📋 Daftar emiten yang dikunci sebagai baseline: {emiten_konsisten_final}\n")

# Simpan catatan log txt untuk bukti lampiran sidang skripsi kamu
os.makedirs(BASE_OUTPUT, exist_ok=True)
with open(os.path.join(BASE_OUTPUT, 'emiten_lolos_sensor.txt'), 'w') as f:
    for ticker in emiten_konsisten_final:
        f.write(f"{ticker}\n")


# ================= FASE 2: LOOP UTAMA CLUSTERING (K = 2 SAMPAI 10) =================
print("🚀 Fase 2: Menjalankan K-Means Clustering Terstandardisasi Sektoral...")

for K_VALUE in range(2, 11):
    path_output_detail = os.path.join(BASE_OUTPUT, f'k{K_VALUE}', 'detail')
    path_output_zona   = os.path.join(BASE_OUTPUT, f'k{K_VALUE}', 'summary_zona')
    
    for p in [path_output_detail, path_output_zona]:
        os.makedirs(p, exist_ok=True)

    print(f"\n{'='*65}")
    print(f" 🔁 MEMPROSES CLUSTERING K = {K_VALUE} (Baseline Terkunci)")
    print(f"{'='*65}")

    saved   = 0
    skipped = 0

    for file in all_files:
        file_name = os.path.basename(file)
        ticker = file_name.split('_')[0]
        
        # KEY REVISI: Jika emiten ini tereliminasi di skenario K mana pun, 
        # maka langsung di-skip sejak awal di SEMUA nilai K demi keadilan data.
        if ticker not in emiten_konsisten_final:
            skipped += 1
            continue
            
        df_raw = pd.read_csv(file)
        
        df_s_detail, df_s_zona = cluster_engine(df_raw, K_VALUE, 'Support')
        df_r_detail, df_r_zona = cluster_engine(df_raw, K_VALUE, 'Resistance')
        
        df_final_detail = pd.concat([df_s_detail, df_r_detail]).sort_values('Tanggal')
        df_final_zona = (pd.concat([df_s_zona, df_r_zona])
                           .sort_values(['Type', 'Temp_Sort'])
                           .drop(columns=['Temp_Sort']))
        
        df_final_detail.to_csv(os.path.join(path_output_detail, file_name), index=False)
        df_final_zona.to_csv( os.path.join(path_output_zona,   file_name), index=False)
        saved += 1

    print(f" ✨ Hasil K={K_VALUE} → {saved} Emiten disimpan, {skipped} Emiten disaring.")

print(f"\n{'='*65}")
print("🏁 PIPELINE CLUSTERING SELESAI DENGAN DATA BASELINE YANG ADIL!")
print(f" Output bersih tersimpan rapi di: {BASE_OUTPUT}\\k2 … k10")
print(f" Bukti baseline dicatat di: {BASE_OUTPUT}\\emiten_lolos_sensor.txt")
print(f"{'='*65}")