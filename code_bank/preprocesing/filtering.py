import pandas as pd
import glob
import os

path_input = r'E:\Semester 7\TA\code_bank\preprocesing\pivot_point'
path_output = r'E:\Semester 7\TA\code_bank\preprocesing\filtered_pivots'

if not os.path.exists(path_output):
    os.makedirs(path_output)

all_files = glob.glob(os.path.join(path_input, "*.csv"))

def filter_and_classify_pivots(df):
    current_close = float(df['Close'].iloc[-1])
    rows_list = []
    
    for index, row in df.iterrows():
        
        if pd.notnull(row['Pivot_High']) and row['Pivot_High'] != "":
            val_high = float(row['Pivot_High'])
            if val_high > current_close:
                rows_list.append({
                    'Tanggal': row['Tanggal'],
                    'High': row['High'],
                    'Low': row['Low'],
                    'Pivot_High': val_high,
                    'Pivot_Low': row['Pivot_Low'],
                    'Type': 'Resistance',
                    'Level': val_high,
                    'Current_Price': current_close,
                    'Selisih': val_high - current_close
                })
        
        if pd.notnull(row['Pivot_Low']) and row['Pivot_Low'] != "":
            val_low = float(row['Pivot_Low'])
            if val_low < current_close:
                rows_list.append({
                    'Tanggal': row['Tanggal'],
                    'High': row['High'],
                    'Low': row['Low'],
                    'Pivot_High': row['Pivot_High'],
                    'Pivot_Low': val_low,
                    'Type': 'Support',
                    'Level': val_low,
                    'Current_Price': current_close,
                    'Selisih': val_low - current_close
                })
                
    return pd.DataFrame(rows_list)

print("Memulai filtering S/R (Fix Dual-Pivot per Tanggal)...")

for file in all_files:
    file_name = os.path.basename(file)
    df = pd.read_csv(file)
    
    df_final = filter_and_classify_pivots(df)
    
    jml_s = (df_final['Type'] == 'Support').sum()
    jml_r = (df_final['Type'] == 'Resistance').sum()
    
    if jml_s >= 3 and jml_r >= 3:
        output_path = os.path.join(path_output, file_name)
        df_final.to_csv(output_path, index=False)
        print(f"{file_name}: S={jml_s}, R={jml_r} | Baris ganda dijamin terpisah")
    else:
        print(f"{file_name}: S={jml_s}, R={jml_r} -> Skip (Kurang dari 3 titik)")

print(f"\nProses Selesai! Cek file ADRO atau emiten lainnya pada tanggal 2020-02-06.")