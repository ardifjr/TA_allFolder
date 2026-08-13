import pandas as pd
import glob
import os
import numpy as np

path_input = r'E:\Semester 7\TA\code_missingValue\preprocesing\filtered_pivots'
path_output = r'E:\Semester 7\TA\code_missingValue\preprocesing\standardized_data'

if not os.path.exists(path_output):
    os.makedirs(path_output)

all_files = glob.glob(os.path.join(path_input, "*.csv"))

def apply_zscore(df):
    """
    Menghitung Z-score untuk kolom Level sesuai formula:
    z = (x - mean) / std_dev
    """
    if df.empty or 'Level' not in df.columns:
        df['Z_Score'] = []
        df['Mean_Reference'] = []
        df['Std_Reference'] = []
        return df

    x = df['Level'].values
    mean_val = np.mean(x)
    std_val = np.std(x)
    
    if std_val == 0:
        df['Z_Score'] = 0.0
    else:
        df['Z_Score'] = (df['Level'] - mean_val) / std_val
        
    df['Mean_Reference'] = mean_val
    df['Std_Reference'] = std_val
    
    return df

print(f"Memulai Standarisasi Z-Score (Total target: {len(all_files)} file emiten)...")

emiten_berhasil = 0

for file in all_files:
    file_name = os.path.basename(file)
    
    # PENANGANAN UTAMA: Cek jika ukuran file 0 bytes atau kosong
    try:
        if os.path.exists(file) and os.path.getsize(file) > 0:
            df = pd.read_csv(file)
        else:
            # Jika file kosong, buat DataFrame default berstruktur
            df = pd.DataFrame(columns=['Tanggal', 'High', 'Low', 'Pivot_High', 'Pivot_Low', 'Type', 'Level', 'Current_Price', 'Selisih'])
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=['Tanggal', 'High', 'Low', 'Pivot_High', 'Pivot_Low', 'Type', 'Level', 'Current_Price', 'Selisih'])

    df_standardized = apply_zscore(df)
    
    # Simpan hasil Z-Score
    output_path = os.path.join(path_output, file_name)
    df_standardized.to_csv(output_path, index=False)
    
    emiten_berhasil += 1
    
    # Print status log
    if not df_standardized.empty and 'Level' in df_standardized.columns and len(df_standardized['Level']) > 0:
        sample_original = df_standardized['Level'].iloc[0]
        sample_z = df_standardized['Z_Score'].iloc[0]
        print(f"[{emiten_berhasil}/{len(all_files)}] {file_name}: Original={sample_original} -> Z-Score={sample_z:.4f}")
    else:
        print(f"[{emiten_berhasil}/{len(all_files)}] {file_name}: File Kosong/Suspend -> Berhasil dilewati & disimpan dengan aman")

print(f"\nProses Selesai! Seluruh {emiten_berhasil} data emiten tersimpan di: {path_output}")