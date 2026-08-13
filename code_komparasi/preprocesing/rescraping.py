import yfinance as yf
import pandas as pd
import os
import time

path_output = r'E:\Semester 7\TA\code\training2'
start_date = "2023-12-26"
end_date = "2025-12-26"

if not os.path.exists(path_output):
    os.makedirs(path_output)

emiten_list = [
    ("DSSA", "DSSA.JK"), ("BUMI", "BUMI.JK"), ("PTRO", "PTRO.JK"), ("ADRO", "ADRO.JK"),
    ("TCPI", "TCPI.JK"), ("PGAS", "PGAS.JK"), ("ENRG", "ENRG.JK"), ("MEDC", "MEDC.JK"),
    ("PTBA", "PTBA.JK"), ("AKRA", "AKRA.JK"), ("ITMG", "ITMG.JK"), ("RAJA", "RAJA.JK"),
    ("DEWA", "DEWA.JK"), ("HRUM", "HRUM.JK"), ("INDY", "INDY.JK"), ("BULL", "BULL.JK"),
    ("TOBA", "TOBA.JK"), ("BIPI", "BIPI.JK"), ("MBSS", "MBSS.JK"), ("IATA", "IATA.JK"),
    ("SURE", "SURE.JK"), ("ELSA", "ELSA.JK"), ("SOCI", "SOCI.JK"), ("TEBE", "TEBE.JK"),
    ("DWGL", "DWGL.JK"), ("DOID", "DOID.JK"), ("WINS", "WINS.JK"), ("TPMA", "TPMA.JK"),
    ("ITMA", "ITMA.JK"), ("KKGI", "KKGI.JK"), ("BBRM", "BBRM.JK"), ("TAMU", "TAMU.JK"),
    ("ARII", "ARII.JK"), ("LEAD", "LEAD.JK"), ("APEX", "APEX.JK"), ("CNKO", "CNKO.JK"),
    ("MTFN", "MTFN.JK"), ("INPS", "INPS.JK"), ("FIRE", "FIRE.JK"), ("WOWS", "WOWS.JK"),
    ("RUIS", "RUIS.JK")
]

print(f"=== Memulai Re-Scraping Data ({start_date} s/d {end_date}) ===\n")

for kode, ticker in emiten_list:
    try:
        print(f"Downloading {kode}...")
        
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False, actions=False)
        
        if data.empty:
            print(f"[!] {kode}: Data kosong dari Yahoo Finance.")
            continue
            
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'Tanggal'}, inplace=True)
        
        data = data[['Tanggal', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        file_name = f"{kode}_{start_date}_to_{end_date}.csv"
        file_path = os.path.join(path_output, file_name)
        
        data.to_csv(file_path, index=False)
        
        print(f"[OK] Tersimpan: {file_name}")
        
        time.sleep(1)
        
    except Exception as e:
        print(f"[ERROR] Gagal download {kode}: {e}")

print("\n=== Proses Re-Scraping Selesai! SEMUA DATA SEKARANG BERSIH ===")