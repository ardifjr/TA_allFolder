import glob
import os
import shutil
import subprocess
import sys
import matplotlib.pyplot as plt
import pandas as pd

# Path direktori utama
BASE_DIR = r"E:\Semester 7\TA\code_komparasi"

CLUSTERING_SCRIPT = os.path.join(BASE_DIR, "clustering", "clustering.py")
SCORING_SCRIPT = os.path.join(BASE_DIR, "clustering", "scoring", "scoring.py")
TESTING_SCRIPT = os.path.join(BASE_DIR, "testingModel.py")

OUTPUT_EVAL_DIR = os.path.join(BASE_DIR, "evaluation")
OUTPUT_KOMPARASI_DIR = os.path.join(BASE_DIR, "komparasiW")


def run_pipeline_for_w(w_val):
    print(f"\n==========================================")
    print(f"   MENJALANKAN PIPELINE UNTUK w = {w_val}")
    print(f"==========================================")

    # 1. Jalankan clustering.py
    print(f"[1/3] Menjalankan {CLUSTERING_SCRIPT} (w={w_val})...")
    subprocess.run(
        [sys.executable, CLUSTERING_SCRIPT, "--w", str(w_val)], check=True
    )

    # 2. Jalankan scoring.py
    print(f"[2/3] Menjalankan {SCORING_SCRIPT}...")
    subprocess.run([sys.executable, SCORING_SCRIPT], check=True)

    # 3. Jalankan testingModel.py
    print(f"[3/3] Menjalankan {TESTING_SCRIPT}...")
    subprocess.run([sys.executable, TESTING_SCRIPT], check=True)


def move_results_to_w_folder(w_val):
    """Memindahkan/menyalin hasil evaluasi dari folder 'evaluation'
    ke folder komparasiW/w_{w_val}/
    """
    target_w_dir = os.path.join(OUTPUT_KOMPARASI_DIR, f"w_{w_val}")
    os.makedirs(target_w_dir, exist_ok=True)

    if os.path.exists(OUTPUT_EVAL_DIR):
        files_to_copy = glob.glob(
            os.path.join(OUTPUT_EVAL_DIR, "summary_metrics_k*.csv")
        ) + glob.glob(os.path.join(OUTPUT_EVAL_DIR, "confusion_matrix_k*.png"))

        for file in files_to_copy:
            shutil.copy(file, target_w_dir)

        print(
            f"[INFO] {len(files_to_copy)} file evaluasi berhasil disalin ke: komparasiW\\w_{w_val}\\"
        )
    else:
        print(f"[WARN] Folder {OUTPUT_EVAL_DIR} tidak ditemukan!")


def collect_metrics_and_plot():
    """Membaca summary_metrics dari SELURUH folder w_1 s/d w_20 lalu memplot grafik gabungan."""
    print(
        "\n[INFO] Mengumpulkan metrik evaluasi dari seluruh variasi w (1-20)..."
    )

    records = []

    # Membaca data dari w_1 hingga w_20
    for w in range(1, 31):
        w_dir = os.path.join(OUTPUT_KOMPARASI_DIR, f"w_{w}")

        for k in range(2, 11):
            csv_path = os.path.join(w_dir, f"summary_metrics_k{k}.csv")

            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    df.columns = df.columns.str.strip()

                    acc_col = [c for c in df.columns if "acc" in c.lower()]
                    prec_col = [c for c in df.columns if "prec" in c.lower()]
                    rec_col = [c for c in df.columns if "rec" in c.lower()]
                    f1_col = [
                        c
                        for c in df.columns
                        if "f1" in c.lower() or "f-score" in c.lower()
                    ]

                    acc = df[acc_col[0]].mean() if acc_col else 0
                    prec = df[prec_col[0]].mean() if prec_col else 0
                    rec = df[rec_col[0]].mean() if rec_col else 0
                    f1 = df[f1_col[0]].mean() if f1_col else 0

                    records.append(
                        {
                            "w": w,
                            "k": k,
                            "Accuracy": acc,
                            "Precision": prec,
                            "Recall": rec,
                            "F1-Score": f1,
                        }
                    )
                except Exception as e:
                    print(f"[WARN] Gagal membaca {csv_path}: {e}")

    if not records:
        print(
            "[ERROR] Tidak ditemukan data CSV evaluasi di dalam folder komparasiW."
        )
        return

    df_all = pd.DataFrame(records)

    # Rata-rata performa berdasarkan variasi nilai W
    df_w_summary = (
        df_all.groupby("w")[["Accuracy", "Precision", "Recall", "F1-Score"]]
        .mean()
        .reset_index()
    )

    # Buat Grafik Perbandingan Metrik dari W=1 s/d 20
    plt.figure(figsize=(12, 6))
    plt.plot(
        df_w_summary["w"],
        df_w_summary["Accuracy"],
        marker="o",
        linewidth=2,
        label="Accuracy",
    )
    plt.plot(
        df_w_summary["w"],
        df_w_summary["Precision"],
        marker="s",
        linewidth=2,
        label="Precision",
    )
    plt.plot(
        df_w_summary["w"],
        df_w_summary["Recall"],
        marker="^",
        linewidth=2,
        label="Recall",
    )
    plt.plot(
        df_w_summary["w"],
        df_w_summary["F1-Score"],
        marker="d",
        linewidth=2,
        label="F1-Score",
    )

    plt.title(
        "Perbandingan Performa Evaluasi Model Berdasarkan Variasi Nilai W (1 - 20)"
    )
    plt.xlabel("Nilai Konsentrasi Lebar Zona (W)")
    plt.ylabel("Skor Evaluasi")

    # Sumbu X ditampilkan lengkap dari 1 s/d 20
    plt.xticks(range(1, 21))
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.tight_layout()

    # Simpan grafik gabungan
    chart_path = os.path.join(
        OUTPUT_KOMPARASI_DIR, "grafik_komparasi_metrik_W_1_20.png"
    )
    plt.savefig(chart_path, dpi=300)
    print(
        f"\n[SUCCESS] Grafik komparasi W (1-20) berhasil disimpan di: {chart_path}"
    )
    plt.show()


if __name__ == "__main__":
    os.makedirs(OUTPUT_KOMPARASI_DIR, exist_ok=True)

    # Hanya menjalankan pipeline untuk W = 11 s/d 20
    # for w in range(21, 31):
    #     try:
    #         run_pipeline_for_w(w)
    #         move_results_to_w_folder(w)
    #     except Exception as e:
    #         print(f"[ERROR] Gagal pada w={w}: {e}")

    # Menggambar grafik gabungan W = 1 s/d 20
    collect_metrics_and_plot()