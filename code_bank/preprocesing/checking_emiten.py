import pandas as pd
import yfinance as yf
import os
import glob

path_training = r'E:\Semester 7\TA\code_bank\training'
start_date = "2019-12-26"
end_date = "2023-12-26"

emiten_dict = {
    "ARTO": "ARTO.JK",
    "BACA": "BACA.JK",
    "BBCA": "BBCA.JK",
    "BBHI": "BBHI.JK",
    "BBMD": "BBMD.JK",
    "BBNI": "BBNI.JK",
    "BBRI": "BBRI.JK",
    "BBTN": "BBTN.JK",
    "BBYB": "BBYB.JK",
    "BDMN": "BDMN.JK",
    "BGTG": "BGTG.JK",
    "BINA": "BINA.JK",
    "BJBR": "BJBR.JK",
    "BJTM": "BJTM.JK",
    "BMRI": "BMRI.JK",
    "BNGA": "BNGA.JK",
    "BNII": "BNII.JK",
    "BNLI": "BNLI.JK",
    "BSIM": "BSIM.JK",
    "BTPN": "BTPN.JK",
    "BVIC": "BVIC.JK",
    "INPC": "INPC.JK",
    "MAYA": "MAYA.JK",
    "MCOR": "MCOR.JK",
    "MEGA": "MEGA.JK",
    "NISP": "NISP.JK",
    "NOBU": "NOBU.JK",
    "PNBN": "PNBN.JK",
    "BRIS": "BRIS.JK",
    "BTPS": "BTPS.JK",
    "AGRO": "AGRO.JK"
}

discrepancy_report = []
summary_stats = {}

print("=== Memulai Validasi & Integrity Check 41 Emiten ===\n")

for kode, ticker in emiten_dict.items():
    file_pattern = os.path.join(path_training, f"{kode}*.csv")
    local_files = glob.glob(file_pattern)
    
    if not local_files:
        continue
    
    try:
        df_local = pd.read_csv(local_files[0], skiprows=[1])
        df_local['Tanggal'] = pd.to_datetime(df_local['Tanggal']).dt.date
        
        data_online = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)
        
        if isinstance(data_online.columns, pd.MultiIndex):
            data_online.columns = data_online.columns.get_level_values(0)
        data_online.reset_index(inplace=True)
        data_online['Date'] = data_online['Date'].dt.date

        merged = pd.merge(df_local, data_online, left_on='Tanggal', right_on='Date', suffixes=('_Lokal', '_Online'))
        
        error_in_emiten = 0
        for _, row in merged.iterrows():
            v_lokal = float(row['Close_Lokal'])
            v_online = float(row['Close_Online'])
            vol_lokal = float(row['Volume_Lokal'])
            
            diff_pct = abs(v_lokal - v_online) / v_online if v_online != 0 else 0
            is_bad_decimal = len(str(v_lokal).split('.')[-1]) > 4 if '.' in str(v_lokal) else False
            
            if diff_pct > 0.02 or is_bad_decimal or (vol_lokal == 0 and row['Volume_Online'] > 0):
                error_in_emiten += 1
                discrepancy_report.append({
                    'Emiten': kode, 'Tanggal': row['Tanggal'], 
                    'Sebab': 'Harga Selisih' if diff_pct > 0.02 else ('Data Adjusted' if is_bad_decimal else 'Volume 0')
                })
        
        summary_stats[kode] = {
            'total_rows': len(merged),
            'errors': error_in_emiten,
            'error_rate': (error_in_emiten / len(merged)) * 100 if len(merged) > 0 else 0
        }
        
        status = "OK" if error_in_emiten == 0 else f"DIRTY ({error_in_emiten} errors)"
        print(f"[{status}] {kode} selesai dicek.")

    except Exception as e:
        print(f"[ERROR] {kode} gagal diproses: {e}")

print("\n" + "="*50)
print("📊 INSIGHT KUALITAS DATA (DATA INTEGRITY REPORT)")
print("="*50)

dirty_emiten = {k: v for k, v in summary_stats.items() if v['errors'] > 0}

if not dirty_emiten:
    print("✅ LUAR BIASA! Semua data emiten bersih dan konsisten.")
else:
    print(f"⚠️ Ditemukan {len(dirty_emiten)} emiten dengan data bermasalah.\n")
    print(f"{'Emiten':<10} | {'Total Data':<12} | {'Jml Error':<10} | {'Error Rate':<10}")
    print("-" * 50)
    
    sorted_dirty = sorted(dirty_emiten.items(), key=lambda x: x[1]['error_rate'], reverse=True)
    
    for kode, stat in sorted_dirty:
        print(f"{kode:<10} | {stat['total_rows']:<12} | {stat['errors']:<10} | {stat['error_rate']:.2f}%")

print("\n💡 REKOMENDASI:")
if len(dirty_emiten) > 5:
    print("- Karena banyak emiten bermasalah, disarankan RE-SCRAPE data menggunakan auto_adjust=False.")
else:
    print("- Data relatif bersih, cukup perbaiki/hapus baris yang bermasalah di emiten tersebut.")
print("="*50)

if discrepancy_report:
    pd.DataFrame(discrepancy_report).to_csv("detail_error_emiten.csv", index=False)