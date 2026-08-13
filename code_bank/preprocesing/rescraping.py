import yfinance as yf
import pandas as pd
import os
import time

path_output = r'E:\Semester 7\TA\code_bank\training'
start_date = "2019-12-26" 
end_date = "2023-12-26"

if not os.path.exists(path_output):
    os.makedirs(path_output)

emiten_list = {
    "BACA": "BACA.JK",
    "BBCA": "BBCA.JK",
    "BBHI": "BBHI.JK",
    "BBMD": "BBMD.JK",
    "BBNI": "BBNI.JK",
    "BBRI": "BBRI.JK",
    "BBTN": "BBTN.JK",
    "BDMN": "BDMN.JK",
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
    "MCOR": "MCOR.JK",
    "MEGA": "MEGA.JK",
    "NISP": "NISP.JK",
    "PNBN": "PNBN.JK",
    "BRIS": "BRIS.JK",
    "BTPS": "BTPS.JK"
}

print(f"=== Memulai Re-Scraping Data ({start_date} s/d {end_date}) ===\n")

for kode, ticker in emiten_list.items():
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