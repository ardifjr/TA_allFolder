import os
import yfinance as yf
import pandas as pd
from time import sleep

emiten_list = [
    ("Bank Jago Tbk.", "ARTO"),
    ("Bank Capital Indonesia Tbk.", "BACA"),
    ("Bank Central Asia Tbk.", "BBCA"),
    ("Allo Bank Indonesia Tbk.", "BBHI"),
    ("Bank Mestika Dharma Tbk.", "BBMD"),
    ("Bank Negara Indonesia (Persero) Tbk.", "BBNI"),
    ("Bank Rakyat Indonesia (Persero) Tbk.", "BBRI"),
    ("Bank Tabungan Negara (Persero) Tbk.", "BBTN"),
    ("Bank Neo Commerce Tbk.", "BBYB"),
    ("Bank Danamon Indonesia Tbk.", "BDMN"),
    ("Bank Ganesha Tbk.", "BGTG"),
    ("Bank Ina Perdana Tbk.", "BINA"),
    ("Bank Pembangunan Daerah Jawa Barat dan Banten Tbk.", "BJBR"),
    ("Bank Pembangunan Daerah Jawa Timur Tbk.", "BJTM"),
    ("Bank Mandiri (Persero) Tbk.", "BMRI"),
    ("Bank CIMB Niaga Tbk.", "BNGA"),
    ("Bank Maybank Indonesia Tbk.", "BNII"),
    ("Bank Permata Tbk.", "BNLI"),
    ("Bank Sinarmas Tbk.", "BSIM"),
    ("Bank SMBC Indonesia Tbk.", "BTPN"),
    ("Bank Victoria International Tbk.", "BVIC"),
    ("Bank Artha Graha Internasional Tbk.", "INPC"),
    ("Bank Mayapada Internasional Tbk.", "MAYA"),
    ("Bank China Construction Bank Indonesia Tbk.", "MCOR"),
    ("Bank Mega Tbk.", "MEGA"),
    ("Bank OCBC NISP Tbk.", "NISP"),
    ("Bank Nationalnobu Tbk.", "NOBU"),
    ("Bank Pan Indonesia Tbk.", "PNBN"),
    ("Bank Syariah Indonesia (Persero) Tbk.", "BRIS"),
    ("Bank BTPN Syariah Tbk.", "BTPS"),
    ("Bank Raya Indonesia Tbk.", "AGRO"),
]

# start_date = "2019-12-26" 
# end_date = "2023-12-26"
start_date = "2023-12-26"
end_date = "2025-12-26"

os.makedirs("testing", exist_ok=True)

print("=" * 100)
print(f"MULAI DOWNLOAD DATA SAHAM SEKTOR ENERGI")
print(f"Periode: {start_date} sampai {end_date}")
print(f"Total emiten: {len(emiten_list)}")
print("=" * 100)
print()

success_count = 0
failed_count = 0
failed_list = []

for idx, (nama_perusahaan, kode) in enumerate(emiten_list, 1):
    saham = f"{kode}.JK"
    
    print(f"[{idx}/{len(emiten_list)}] Mengunduh data {kode} - {nama_perusahaan}...", end=" ")
    
    try:
        data = yf.download(saham, start=start_date, end=end_date, progress=False, auto_adjust=True)
        
        if len(data) == 0:
            print("GAGAL")
            failed_count += 1
            failed_list.append((kode, "Tidak ada data"))
        else:
            df = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df.reset_index(inplace=True)
            df.rename(columns={'Date': 'Tanggal'}, inplace=True)
            df['Tanggal'] = df['Tanggal'].dt.strftime('%Y-%m-%d')
            
            filename = f"testing/{kode}_{start_date}_to_{end_date}.csv"
            df.to_csv(filename, index=False)
            
            print(f"BERHASIL ({len(df)} hari trading)")
            success_count += 1
        
        sleep(0.5)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        failed_count += 1
        failed_list.append((kode, str(e)))


print(f"Berhasil: {success_count} emiten")
print(f"Gagal: {failed_count} emiten")

if failed_list:
    print("\nDaftar emiten yang gagal:")
    for kode, reason in failed_list:
        print(f"  - {kode}: {reason}")
