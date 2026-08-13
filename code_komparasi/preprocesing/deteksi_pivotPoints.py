import pandas as pd
import glob
import os

path_training = r'E:\Semester 7\TA\code\training'
path_output = r'E:\Semester 7\TA\code\preprocesing\pivot_point'

if not os.path.exists(path_output):
    os.makedirs(path_output)

all_files = glob.glob(os.path.join(path_training, "*.csv"))

def detect_fractal_pivots(df, order=1):
    """
    Logika sesuai contoh manual:
    - Pivot High: High hari ini > High 1 hari sebelum DAN 1 hari sesudah.
    - Pivot Low: Low hari ini < Low 1 hari sebelum DAN 1 hari sesudah.
    """
    df['Pivot_High'] = None
    df['Pivot_Low'] = None
    
    for i in range(order, len(df) - order):
        current_high = df.loc[i, 'High']
        current_low = df.loc[i, 'Low']
        
        if all(current_high > df.loc[i-j, 'High'] for j in range(1, order + 1)) and \
           all(current_high > df.loc[i+j, 'High'] for j in range(1, order + 1)):
            df.at[i, 'Pivot_High'] = current_high
            
        if all(current_low < df.loc[i-j, 'Low'] for j in range(1, order + 1)) and \
           all(current_low < df.loc[i+j, 'Low'] for j in range(1, order + 1)):
            df.at[i, 'Pivot_Low'] = current_low
            
    return df

print(f"Memulai deteksi Fractal Pivot Points (Order=1)...")

for file in all_files:
    file_name = os.path.basename(file)
    df = pd.read_csv(file)
    
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    df = df.sort_values('Tanggal').reset_index(drop=True)
    
    df_result = detect_fractal_pivots(df, order=1)
    
    output_path = os.path.join(path_output, file_name)
    df_result.to_csv(output_path, index=False)
    
    total_high = df_result['Pivot_High'].notna().sum()
    total_low = df_result['Pivot_Low'].notna().sum()
    print(f"{file_name}: Pivot High={total_high}, Pivot Low={total_low}")

print(f"\nProses Selesai! Data tersimpan di: {path_output}")