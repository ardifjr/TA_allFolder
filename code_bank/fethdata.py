import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.signal import argrelextrema
import warnings
warnings.filterwarnings('ignore')

# ========== KONFIGURASI ==========
ticker = "BREN.JK"
start_date = "2023-10-20"
end_date = "2024-10-04"

# ========== DOWNLOAD DATA ==========
print(f"📥 Downloading data untuk {ticker}...")
data = yf.download(ticker, start=start_date, end=end_date)
data.to_csv(f"harga_saham_{ticker.replace('.JK', '')}.csv")
print(f"✅ Data berhasil disimpan!\n")

# ========== HARGA SAAT INI (END DATE) ==========
current_price = float(data['Close'].iloc[-1])
print(f"💰 HARGA SAAT INI ({end_date}): Rp {current_price:,.0f}")
print("=" * 70)

# ========== FUNGSI DETEKSI PIVOT POINTS ==========
def detect_pivot_points(df, order=5):
    """
    Deteksi pivot high (resistance) dan pivot low (support)
    order: jumlah candle di kiri & kanan untuk konfirmasi pivot
    
    Reference:
    - De Prado, M. L. (2018). Advances in Financial Machine Learning. Wiley.
    """
    # Pivot Highs (potential resistance)
    df['pivot_high'] = df['High'].iloc[
        argrelextrema(df['High'].values, np.greater_equal, order=order)[0]
    ]
    
    # Pivot Lows (potential support)
    df['pivot_low'] = df['Low'].iloc[
        argrelextrema(df['Low'].values, np.less_equal, order=order)[0]
    ]
    
    return df

# ========== DETEKSI PIVOT POINTS ==========
print("\n🔍 Mendeteksi pivot points...")
data = detect_pivot_points(data, order=5)

# Ambil semua pivot highs dan lows yang terdeteksi
all_resistance_levels = data['pivot_high'].dropna().values
all_support_levels = data['pivot_low'].dropna().values

print(f"   Pivot Highs terdeteksi: {len(all_resistance_levels)}")
print(f"   Pivot Lows terdeteksi: {len(all_support_levels)}")

# ========== FILTER BERDASARKAN HARGA SAAT INI ==========
# Support: hanya pivot yang di BAWAH harga saat ini
support_levels = all_support_levels[all_support_levels < current_price]

# Resistance: hanya pivot yang di ATAS harga saat ini
resistance_levels = all_resistance_levels[all_resistance_levels > current_price]

print(f"\n📊 Setelah filter berdasarkan harga saat ini:")
print(f"   Support levels (di bawah {current_price:,.0f}): {len(support_levels)}")
print(f"   Resistance levels (di atas {current_price:,.0f}): {len(resistance_levels)}")

# ========== MACHINE LEARNING: K-MEANS CLUSTERING ==========
def cluster_levels(levels, n_clusters=3):
    """
    Clustering price levels untuk mendapatkan zona S/R
    
    References:
    - MacQueen, J. (1967). Some methods for classification and analysis 
      of multivariate observations. Proceedings of the Fifth Berkeley 
      Symposium on Mathematical Statistics and Probability.
    - Hastie, T., Tibshirani, R., & Friedman, J. (2009). 
      The Elements of Statistical Learning. Springer.
    """
    if len(levels) == 0:
        return []
    
    if len(levels) < n_clusters:
        n_clusters = max(1, len(levels))
    
    # Reshape untuk sklearn
    X = levels.reshape(-1, 1)
    
    # Standardize (Z-score normalization)
    # Formula: z = (x - μ) / σ
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # K-Means Clustering
    # Minimize WCSS: Σ ||x - μᵢ||²
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    
    # Transform kembali ke harga asli
    centers = scaler.inverse_transform(kmeans.cluster_centers_)
    
    # Hitung range untuk setiap cluster
    zones = []
    for i in range(n_clusters):
        cluster_points = X[kmeans.labels_ == i]
        if len(cluster_points) > 0:
            zone_min = float(cluster_points.min())
            zone_max = float(cluster_points.max())
            
            # Expand zone sedikit untuk coverage lebih baik
            # Murphy (1999): S/R adalah zona, bukan garis exact
            margin = (zone_max - zone_min) * 0.1
            zones.append({
                'min': zone_min - margin,
                'max': zone_max + margin,
                'strength': len(cluster_points)  # Jumlah touch points
            })
    
    # Sort by price
    zones = sorted(zones, key=lambda x: x['min'])
    return zones

# ========== CLUSTERING SUPPORT LEVELS ==========
print("\n🤖 Machine Learning: Clustering Support Levels...")
if len(support_levels) > 0:
    n_support_clusters = min(3, len(support_levels))
    support_zones = cluster_levels(support_levels, n_clusters=n_support_clusters)
    
    print(f"\n📉 ZONA SUPPORT (dari {len(support_levels)} pivot lows DI BAWAH harga saat ini):")
    print("=" * 70)
    if support_zones:
        for i, zone in enumerate(support_zones, 1):
            print(f"Support Zone {i}: Rp {zone['min']:,.0f} - Rp {zone['max']:,.0f}")
            print(f"   Strength: {zone['strength']} touch points")
            print()
    else:
        print("⚠️  Tidak ada zona support terbentuk\n")
else:
    print("\n⚠️  Tidak ada support level terdeteksi di bawah harga saat ini\n")
    support_zones = []

# ========== CLUSTERING RESISTANCE LEVELS ==========
print("🤖 Machine Learning: Clustering Resistance Levels...")
if len(resistance_levels) > 0:
    n_resistance_clusters = min(3, len(resistance_levels))
    resistance_zones = cluster_levels(resistance_levels, n_clusters=n_resistance_clusters)
    
    print(f"\n📈 ZONA RESISTANCE (dari {len(resistance_levels)} pivot highs DI ATAS harga saat ini):")
    print("=" * 70)
    if resistance_zones:
        for i, zone in enumerate(resistance_zones, 1):
            print(f"Resistance Zone {i}: Rp {zone['min']:,.0f} - Rp {zone['max']:,.0f}")
            print(f"   Strength: {zone['strength']} touch points")
            print()
    else:
        print("⚠️  Tidak ada zona resistance terbentuk\n")
else:
    print("\n⚠️  Tidak ada resistance level terdeteksi di atas harga saat ini\n")
    resistance_zones = []

# ========== TRADING SIGNAL ==========
print(f"\n🎯 TRADING SIGNAL:")
print("=" * 70)

if support_zones and resistance_zones:
    # Ambil support terdekat (paling atas)
    nearest_support = max(support_zones, key=lambda x: x['min'])
    # Ambil resistance terdekat (paling bawah)
    nearest_resistance = min(resistance_zones, key=lambda x: x['min'])
    
    distance_to_support = ((current_price - nearest_support['max']) / current_price) * 100
    distance_to_resistance = ((nearest_resistance['min'] - current_price) / current_price) * 100
    
    print(f"📉 Nearest Support: Rp {nearest_support['min']:,.0f} - Rp {nearest_support['max']:,.0f}")
    print(f"   Distance: {abs(distance_to_support):.2f}% below current price")
    print()
    print(f"📈 Nearest Resistance: Rp {nearest_resistance['min']:,.0f} - Rp {nearest_resistance['max']:,.0f}")
    print(f"   Distance: {distance_to_resistance:.2f}% above current price")
    print()
    
    # Trading recommendation
    if distance_to_support < 5:  # Dalam 5% dari support
        print("🟢 NEAR SUPPORT ZONE - Potensi BOUNCE (BUY OPPORTUNITY)")
        print("   Watch for bullish confirmation (green candle, volume spike)")
    elif distance_to_resistance < 5:  # Dalam 5% dari resistance
        print("🔴 NEAR RESISTANCE ZONE - Potensi REJECTION (SELL OPPORTUNITY)")
        print("   Watch for bearish confirmation (red candle, volume spike)")
    else:
        print("🟡 NEUTRAL ZONE - Tunggu konfirmasi mendekati S/R")
        
elif support_zones:
    nearest_support = max(support_zones, key=lambda x: x['min'])
    print(f"📉 Nearest Support: Rp {nearest_support['min']:,.0f} - Rp {nearest_support['max']:,.0f}")
    print("⚠️  Tidak ada resistance terdeteksi di atas harga saat ini")
    
elif resistance_zones:
    nearest_resistance = min(resistance_zones, key=lambda x: x['min'])
    print(f"📈 Nearest Resistance: Rp {nearest_resistance['min']:,.0f} - Rp {nearest_resistance['max']:,.0f}")
    print("⚠️  Tidak ada support terdeteksi di bawah harga saat ini")
    
else:
    print("⚠️  Insufficient data untuk trading signal")

print("\n" + "=" * 70)
print("📝 Note: Ini bukan rekomendasi trading. Selalu gunakan analisis tambahan!")
print("=" * 70)

# ========== SCORING FUNCTION ==========
def calculate_zone_score(zone, current_price, is_support=True):
    """
    Hitung score berdasarkan:
    1. Distance: Semakin dekat = semakin baik
    2. Strength: Semakin banyak touch points = semakin kuat
    
    Score = (Strength Weight) / (Distance Weight)
    Semakin tinggi score = semakin valid zona S/R
    
    Reference:
    - Multi-criteria decision making approach
    - Saaty, T. L. (2008). Decision making with the analytic hierarchy process.
    """
    if is_support:
        # Untuk support, hitung jarak dari max zone ke current price
        distance = abs(current_price - zone['max'])
    else:
        # Untuk resistance, hitung jarak dari min zone ke current price
        distance = abs(zone['min'] - current_price)
    
    # Normalized distance (percentage)
    normalized_distance = distance / current_price
    
    # Score formula: Strength dibagi dengan distance
    # Semakin banyak touch points dan semakin dekat = score tinggi
    score = zone['strength'] / (normalized_distance + 0.01)  # +0.01 untuk avoid division by zero
    
    return score

# ========== FINAL OUTPUT ==========
print(f"\n📊 HASIL PREDIKSI SUPPORT & RESISTANCE:")
print("=" * 70)
print(f"Ticker: {ticker}")
print(f"Period: {start_date} to {end_date}")
print(f"Current Price: Rp {current_price:,.0f}")
print("=" * 70)

# Pilih support terbaik berdasarkan score
if support_zones:
    # Hitung score untuk semua support zones
    support_scores = [(zone, calculate_zone_score(zone, current_price, is_support=True)) 
                     for zone in support_zones]
    # Pilih yang score tertinggi
    best_support, support_score = max(support_scores, key=lambda x: x[1])
    print(f"\n✅ SUPPORT: Rp {best_support['min']:,.0f} - Rp {best_support['max']:,.0f}")
    print(f"   (Touch points: {best_support['strength']}, Score: {support_score:.2f})")
else:
    print("\n❌ SUPPORT: Tidak terdeteksi")

# Pilih resistance terbaik berdasarkan score
if resistance_zones:
    # Hitung score untuk semua resistance zones
    resistance_scores = [(zone, calculate_zone_score(zone, current_price, is_support=False)) 
                        for zone in resistance_zones]
    # Pilih yang score tertinggi
    best_resistance, resistance_score = max(resistance_scores, key=lambda x: x[1])
    print(f"✅ RESISTANCE: Rp {best_resistance['min']:,.0f} - Rp {best_resistance['max']:,.0f}")
    print(f"   (Touch points: {best_resistance['strength']}, Score: {resistance_score:.2f})")
else:
    print("❌ RESISTANCE: Tidak terdeteksi")

print("=" * 70)