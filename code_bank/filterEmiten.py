import os
import glob

base_path_clustering = r'E:\Semester 7\TA\code\clustering'
k_variants = [2, 3, 4, 5, 6, 7, 8, 9, 10]

# 1. Kumpulkan emiten yang lolos di setiap K
emiten_per_k = {}
for k in k_variants:
    path_zona = os.path.join(base_path_clustering, f'k{k}', 'summary_zona')
    files = glob.glob(os.path.join(path_zona, "*.csv"))
    tickers = {os.path.basename(f).split('_')[0] for f in files}
    emiten_per_k[k] = tickers

# 2. Cari irisan (Intersection) emiten yang selalu ada di K=2 sampai K=10
emiten_konsisten = set.intersection(*emiten_per_k.values())
emiten_konsisten = sorted(list(emiten_konsisten))

print(f"====================================================")
print(f"🎯 HASIL FILTERISASI EMITEN UNTUK STANDARD BASELINE")
print(f"====================================================")
print(f"Total Emiten yang Selalu Lolos Validasi K2-K10: {len(emiten_konsisten)} Emiten")
print(f"Daftar Ticker: {emiten_konsisten}")
print(f"====================================================")

# Simpan daftar ini ke file teks sebagai acuan program lain
with open(os.path.join(base_path_clustering, 'emiten_lolos_sensor.txt'), 'w') as f:
    for ticker in emiten_konsisten:
        f.write(f"{ticker}\n")
print("✨ Berkas 'emiten_lolos_sensor.txt' berhasil dibuat sebagai acuan filter!")