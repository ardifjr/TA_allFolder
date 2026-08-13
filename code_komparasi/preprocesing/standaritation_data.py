import pandas as pd
import glob
import os
import numpy as np

path_input = r'E:\Semester 7\TA\code\preprocesing\filtered_pivots'
path_output = r'E:\Semester 7\TA\code\preprocesing\standardized_data'

if not os.path.exists(path_output):
    os.makedirs(path_output)

all_files = glob.glob(os.path.join(path_input, "*.csv"))

def apply_zscore(df):
    """
    Menghitung Z-score untuk kolom Level sesuai formula:
    z = (x - mean) / std_dev
    """
    if df.empty:
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

print("Memulai Standarisasi Z-Score untuk 34 Emiten...")

for file in all_files:
    file_name = os.path.basename(file)
    df = pd.read_csv(file)
    
    df_standardized = apply_zscore(df)
    
    output_path = os.path.join(path_output, file_name)
    df_standardized.to_csv(output_path, index=False)
    
    sample_original = df_standardized['Level'].iloc[0]
    sample_z = df_standardized['Z_Score'].iloc[0]
    print(f"{file_name}: Original={sample_original} -> Z-Score={sample_z:.4f}")

print(f"\nProses Selesai! Data tersimpan di: {path_output}")