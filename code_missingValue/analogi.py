import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
import random

# =========================
# GENERATE DATA (TIAP 3 HARI)
# =========================
start_date = datetime(2025, 12, 1)
end_date = datetime(2026, 3, 31)

dates = []
prices = []

current_date = start_date
while current_date <= end_date:
    dates.append(current_date.strftime("%d %b"))
    month = current_date.month
    day = current_date.day

    # -------------------------
    # LOGIKA HARGA JAKET
    # -------------------------
    if month == 12:
        if day <= 20:
            price = random.randint(180000, 220000)   # normal
        elif 21 <= day <= 29:
            price = random.randint(230000, 280000)   # naik
        else:
            price = random.randint(300000, 340000)   # puncak tahun baru

    elif month == 1:
        if day <= 2:
            price = random.randint(300000, 330000)   # puncak
        else:
            price = random.randint(190000, 230000)   # turun & stabil

    elif month == 2:
        if day < 20:
            price = random.randint(190000, 230000)   # stabil
        else:
            price = random.randint(230000, 270000)   # mulai naik

    elif month == 3:
        price = random.randint(260000, 310000)       # naik jelang Lebaran

    prices.append(price)
    current_date += timedelta(days=6)

# =========================
# FORMAT RUPIAH
# =========================
def rupiah(x, pos):
    return f"Rp {int(x):,}".replace(",", ".")

# =========================
# GUI TKINTER
# =========================
root = tk.Tk()
root.title("Grafik Pergerakan Harga Jaket")
root.geometry("1000x600")

title = ttk.Label(
    root,
    text="Pergerakan Harga Jaket",
    font=("Segoe UI", 16, "bold")
)
title.pack(pady=10)

subtitle = ttk.Label(
    root,
    text="Desember – Maret | Interval 3 Hari | Pola Musiman",
    font=("Segoe UI", 10)
)
subtitle.pack()

# =========================
# GRAFIK
# =========================
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(dates, prices, marker='o', linewidth=2)

ax.set_title("Harga Jaket (Rupiah)")
ax.set_xlabel("Periode Tanggal")
ax.set_ylabel("Harga")
ax.tick_params(axis='x', labelrotation=45)
ax.yaxis.set_major_formatter(FuncFormatter(rupiah))
ax.grid(True)

# =========================
# EMBED KE GUI
# =========================
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=20)

root.mainloop()
