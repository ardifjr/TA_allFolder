import pandas as pd
import numpy as np
import os
import glob
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

path_training = r'E:\Semester 7\TA\code_komparasi\training'
base_path_clustering = r'E:\Semester 7\TA\code_komparasi\clustering'
base_path_scoring = r'E:\Semester 7\TA\code_komparasi\clustering\scoring'

k_variants = [2,3,4,5,6,7,8,9,10]

def calculate_scoring(df_zona, current_price):
    """
    Menghitung skor berdasarkan rumus:
    Score = Strength / (Normalized_Distance + Smoothing_Factor)
    Jarak dihitung langsung ke titik pusat psikologis pasar (Centroid_Price).
    """
    smoothing_factor = 0.01
    scores = []
    norm_distances = []
    zone_boundaries = []
    
    for _, row in df_zona.iterrows():
        boundary = float(row['Centroid_Price'])
            
        abs_distance = abs(current_price - boundary)
        norm_distance = abs_distance / current_price
        
        score = float(row['Strength']) / (norm_distance + smoothing_factor)
        
        zone_boundaries.append(boundary)
        norm_distances.append(round(norm_distance, 4))
        scores.append(round(score, 2))
        
    df_zona['Zone_Boundary'] = zone_boundaries
    df_zona['Norm_Distance'] = norm_distances
    df_zona['Score'] = scores
    
    df_zona['Ranking'] = df_zona.groupby('Type')['Score'].rank(ascending=False, method='min').astype(int)
    df_zona = df_zona.sort_values(['Type', 'Ranking']).reset_index(drop=True)
    
    return df_zona

print("Memulai Proses Scoring Zona Berbasis Centroid Dynamic Width...")

for k in k_variants:
    path_input_zona = os.path.join(base_path_clustering, f'k{k}', 'summary_zona')
    path_output_scoring = os.path.join(base_path_scoring, f'k{k}')
    
    if not os.path.exists(path_output_scoring):
        os.makedirs(path_output_scoring)
    zona_files = glob.glob(os.path.join(path_input_zona, "*.csv"))
    
    print(f"\nMemproses Perhitungan Skor Prioritas K={k} ({len(zona_files)} Emiten)...")
    
    for file in zona_files:
        file_name = os.path.basename(file)
        
        training_file_path = os.path.join(path_training, file_name)
        if not os.path.exists(training_file_path):
            print(f"Data training untuk {file_name} tidak ditemukan. Dilewati.")
            continue
            
        df_train = pd.read_csv(training_file_path)
        current_price = float(df_train['Close'].iloc[-1])
        
        df_zona = pd.read_csv(file)
        
        df_scored = calculate_scoring(df_zona, current_price)
        df_scored['Current_Price'] = current_price
        
        columns_order = ['Type', 'Min', 'Max', 'Centroid_Price', 'Std_Internal', 'Strength', 
                         'Zone_Boundary', 'Norm_Distance', 'Current_Price', 'Score', 'Ranking']
        df_scored = df_scored[columns_order]
        
        output_file_path = os.path.join(path_output_scoring, file_name)
        df_scored.to_csv(output_file_path, index=False)
        
        if "ADRO" in file_name:
            print(f"   ↳ Sampel Output ADRO (K={k}) | Current Price: {current_price}")
            print(df_scored[['Type', 'Min', 'Max', 'Std_Internal', 'Score', 'Ranking']].to_string(index=False))

print("\nSemua proses scoring otomatis selesai! Hasil ter-update rapi di folder target masing-masing.")