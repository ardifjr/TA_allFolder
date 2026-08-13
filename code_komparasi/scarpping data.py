import os
import yfinance as yf
import pandas as pd
from time import sleep

emiten_list = [
    ("Dian Swastatika Sentosa Tbk", "DSSA"),
    ("Bumi Resources Tbk", "BUMI"),
    ("Petrosea Tbk", "PTRO"),
    ("Alamtri Resources Indonesia Tbk", "ADRO"),
    ("Transcoal Pacific Tbk", "TCPI"),
    ("Perusahaan Gas Negara Tbk", "PGAS"),
    ("Energi Mega Persada Tbk", "ENRG"),
    ("Medco Energi Internasional Tbk", "MEDC"),
    ("Bukit Asam Tbk", "PTBA"),
    ("AKR Corporindo Tbk", "AKRA"),
    ("Indo Tambangraya Megah Tbk", "ITMG"),
    ("Rukun Raharja Tbk", "RAJA"),
    ("Darma Henwa Tbk", "DEWA"),
    ("Harum Energy Tbk", "HRUM"),
    ("Indika Energy Tbk", "INDY"),
    ("Buana Lintas Lautan Tbk", "BULL"),
    ("TBS Energi Utama Tbk", "TOBA"),
    ("Astrindo Nusantara Infrastruktur Tbk", "BIPI"),
    ("Mitrabahtera Segara Sejati Tbk", "MBSS"),
    ("MNC Energy Investments Tbk", "IATA"),
    ("Super Energy Tbk", "SURE"),
    ("Elnusa Tbk", "ELSA"),
    ("Soechi Lines Tbk", "SOCI"),
    ("Dana Brata Luhur Tbk", "TEBE"),
    ("Dwi Guna Laksana Tbk", "DWGL"),
    ("BUMA Internasional Grup Tbk", "DOID"),
    ("Wintermar Offshore Marine Tbk", "WINS"),
    ("Trans Power Marine Tbk", "TPMA"),
    ("Sumber Energi Andalan Tbk", "ITMA"),
    ("Resource Alam Indonesia Tbk", "KKGI"),
    ("Pelayaran National Bina Buana Raya Tbk", "BBRM"),
    ("Pelayaran Tamarin Samudra Tbk", "TAMU"),
    ("Atlas Resources Tbk", "ARII"),
    ("Logindo Samudramakmur Tbk", "LEAD"),
    ("Apexindo Pratama Duta Tbk", "APEX"),
    ("Exploitasi Energi Indonesia Tbk", "CNKO"),
    ("Capitalinc Investment Tbk", "MTFN"),
    ("Indah Prakasa Sentosa Tbk", "INPS"),
    ("Alfa Energi Investama Tbk", "FIRE"),
    ("Ginting Jaya Energi Tbk", "WOWS"),
    ("Radiant Utama Interinsco Tbk", "RUIS"),
]

start_date = "2019-12-26" 
end_date = "2023-12-26"
# start_date = "2023-12-26"
# end_date = "2025-12-26"

os.makedirs("training", exist_ok=True)

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
            
            filename = f"training/{kode}_{start_date}_to_{end_date}.csv"
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
