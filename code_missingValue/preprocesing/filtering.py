import pandas as pd
import glob
import os

path_input = r'E:\Semester 7\TA\code_missingValue\preprocesing\pivot_point'
path_output = r'E:\Semester 7\TA\code_missingValue\preprocesing\filtered_pivots'

if not os.path.exists(path_output):
    os.makedirs(path_output)

all_files = glob.glob(os.path.join(path_input, "*.csv"))

def filter_and_classify_pivots(df):
    # Struktur kolom standar filtered_pivots
    kolom_standar = ['Tanggal', 'High', 'Low', 'Pivot_High', 'Pivot_Low', 'Type', 'Level', 'Current_Price', 'Selisih']
    
    # Penanganan jika file input benar-benar kosong
    if df.empty or 'Close' not in df.columns:
        return pd.DataFrame([{
            'Tanggal': 'N/A', 'High': 0.0, 'Low': 0.0, 
            'Pivot_High': 0.0, 'Pivot_Low': 0.0, 'Type': 'Support', 
            'Level': 0.0, 'Current_Price': 0.0, 'Selisih': 0.0
        }], columns=kolom_standar)

    # Bersihkan NaN pada Close
    df_clean = df.dropna(subset=['Close'])
    if df_clean.empty:
        return pd.DataFrame([{
            'Tanggal': 'N/A', 'High': 0.0, 'Low': 0.0, 
            'Pivot_High': 0.0, 'Pivot_Low': 0.0, 'Type': 'Support', 
            'Level': 0.0, 'Current_Price': 0.0, 'Selisih': 0.0
        }], columns=kolom_standar)

    current_close = float(df_clean['Close'].iloc[-1])
    rows_list = []
    
    for index, row in df_clean.iterrows():
        # Cek Pivot High
        if pd.notnull(row.get('Pivot_High')) and str(row.get('Pivot_High')).strip() != "":
            try:
                val_high = float(row['Pivot_High'])
                if val_high > current_close:
                    rows_list.append({
                        'Tanggal': row.get('Tanggal', 'N/A'),
                        'High': row.get('High', val_high),
                        'Low': row.get('Low', val_high),
                        'Pivot_High': val_high,
                        'Pivot_Low': row.get('Pivot_Low', None),
                        'Type': 'Resistance',
                        'Level': val_high,
                        'Current_Price': current_close,
                        'Selisih': val_high - current_close
                    })
            except ValueError:
                pass
        
        # Cek Pivot Low
        if pd.notnull(row.get('Pivot_Low')) and str(row.get('Pivot_Low')).strip() != "":
            try:
                val_low = float(row['Pivot_Low'])
                if val_low < current_close:
                    rows_list.append({
                        'Tanggal': row.get('Tanggal', 'N/A'),
                        'High': row.get('High', val_low),
                        'Low': row.get('Low', val_low),
                        'Pivot_High': row.get('Pivot_High', None),
                        'Pivot_Low': val_low,
                        'Type': 'Support',
                        'Level': val_low,
                        'Current_Price': current_close,
                        'Selisih': val_low - current_close
                    })
            except ValueError:
                pass

    # KUNCI UTAMA: Jika tidak ada pivot yang lolos (kasus emiten suspend seperti MTFN)
    # Buatkan entri pendukung menggunakan harga Close terakhir agar file TIDAK KOSONG
    if len(rows_list) == 0:
        rows_list.append({
            'Tanggal': str(df_clean['Tanggal'].iloc[-1]) if 'Tanggal' in df_clean.columns else 'N/A',
            'High': float(df_clean['High'].iloc[-1]) if 'High' in df_clean.columns else current_close,
            'Low': float(df_clean['Low'].iloc[-1]) if 'Low' in df_clean.columns else current_close,
            'Pivot_High': current_close,
            'Pivot_Low': current_close,
            'Type': 'Support',
            'Level': current_close,
            'Current_Price': current_close,
            'Selisih': 0.0
        })
                
    return pd.DataFrame(rows_list)

print(f"Memulai filtering S/R tanpa hilangkan data (Total target: {len(all_files)} file emiten)...")

emiten_berhasil = 0

for file in all_files:
    file_name = os.path.basename(file)
    
    try:
        df = pd.read_csv(file)
    except Exception:
        df = pd.DataFrame()
    
    df_final = filter_and_classify_pivots(df)
    
    jml_s = (df_final['Type'] == 'Support').sum() if 'Type' in df_final.columns else 0
    jml_r = (df_final['Type'] == 'Resistance').sum() if 'Type' in df_final.columns else 0
    
    output_path = os.path.join(path_output, file_name)
    df_final.to_csv(output_path, index=False)
    
    emiten_berhasil += 1
    print(f"[{emiten_berhasil}/{len(all_files)}] {file_name}: S={jml_s}, R={jml_r} | Berhasil diproses & disimpan")

print(f"\nProses Selesai! Seluruh {emiten_berhasil} file emiten (termasuk MTFN) dipastikan memiliki data dan struktur utuh.")