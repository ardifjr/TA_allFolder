import os
import matplotlib.pyplot as plt

# 1. Definisikan daftar emiten dari folder testing kamu (26 emiten valid)
lolos = [
    "ADRO", "AKRA", "APEX", "ARII", "BULL", "BUMI", "DEWA", "DOID", 
    "ELSA", "ENRG", "FIRE", "HRUM", "INDY", "ITMA", "ITMG", "KKGI", 
    "MBSS", "MEDC", "PGAS", "PTBA", "RUIS", "SOCI", "TCPI", "TEBE", 
    "TPMA", "WINS"
]

# 14 Emiten pelengkap yang tereliminasi
tereliminasi = [
    "BIPI", "BOSS", "BBRM", "COAL", "DEAL", "GTBO", "HITS", 
    "IATA", "MITI", "PKPK", "RMKO", "SGER", "TOBA", "W領S"
]
tereliminasi = [x for x in tereliminasi if x not in lolos][:14]

# Format teks daftar emiten agar rapi ditaruh di Legend (pecah per baris)
def format_emiten_teks(daftar, per_baris=7):
    return "\n".join([", ".join(daftar[i:i+per_baris]) for i in range(0, len(daftar), per_baris)])

teks_lolos_legend = f"Lolos Kriteria ({len(lolos)} Emiten):\n" + format_emiten_teks(lolos, 6)
teks_gugur_legend = f"Tereliminasi ({len(tereliminasi)} Emiten):\n" + format_emiten_teks(tereliminasi, 5)

# 2. Set Up Data Visualisasi Diagram
labels = [f'Lolos Kriteria ({len(lolos)} Emiten)', f'Tereliminasi ({len(tereliminasi)} Emiten)']
sizes = [len(lolos), len(tereliminasi)]
colors = ['#2ecc71', '#e74c3c'] 
explode = (0.05, 0)  

# 3. Proses Penggambaran Diagram (Layout Responsif)
fig, ax = plt.subplots(figsize=(11, 6)) # Diperlebar ke samping supaya space aman

wedges, texts, autotexts = ax.pie(
    sizes, 
    explode=explode, 
    labels=labels, 
    colors=colors,
    autopct='%1.1f%%', 
    shadow=True, 
    startangle=140,
    textprops={'fontsize': 11, 'weight': 'bold'}
)

# Memperjelas teks persentase di dalam lingkaran
plt.setp(autotexts, size=11, weight="bold", color="white")

# 4. Membuat Legend di Samping Kanan (Aman dari Tabrakan Teks)
ax.legend(
    wedges, 
    [teks_lolos_legend, teks_gugur_legend],
    title="Penyaringan Emiten Sektor Energi",
    title_fontproperties={'weight': 'bold', 'size': 11},
    loc="center left",
    bbox_to_anchor=(1, 0, 0.5, 1), # Mengunci posisi di kanan luar diagram
    fontsize=9.5,
    frameon=True,
    facecolor='#f9f9f9',
    edgecolor='#cccccc'
)

plt.title("DIAGRAM PARTISI SELEKSI EMITEN SEKTOR ENERGI IDX\n(Total Populasi: 40 Emiten)", fontsize=13, weight='bold', pad=10)

# 5. Penyimpanan Aset Gambar
path_folder = r"E:\Semester 7\TA\code"
output_gambar = os.path.join(path_folder, "diagram_partisi_emiten2.png")

# plt.tight_layout() otomatis mengatur ruang agar responsif dan tidak terpotong
plt.tight_layout()
plt.savefig(output_gambar, dpi=300, bbox_inches='tight')
plt.show()

print(f"\n[SUKSES] Gambar diagram responsif berhasil disimpan di: {output_gambar}")