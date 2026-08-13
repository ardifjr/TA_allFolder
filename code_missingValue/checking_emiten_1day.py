import yfinance as yf
import pandas as pd

def get_idx_fraksi(price):
    """
    Fungsi untuk membulatkan harga sesuai aturan Fraksi Harga IDX terbaru.
    """
    if price < 200:
        return round(price)
    elif 200 <= price < 500:
        return round(price / 2) * 2
    elif 500 <= price < 2000:
        return round(price / 5) * 5
    elif 2000 <= price < 5000:
        return round(price / 10) * 10
    elif price >= 5000:
        return round(price / 25) * 25
    else:
        return price

def check_stock_data(ticker, tanggal):
    """
    Mengambil data OHLCV dan melakukan normalisasi fraksi harga.
    """
    if not ticker.endswith(".JK"):
        ticker = f"{ticker}.JK"
    
    print(f"--- Memeriksa Data: {ticker} | Tanggal: {tanggal} ---")
    
    start_dt = pd.to_datetime(tanggal)
    end_dt = start_dt + pd.Timedelta(days=1)
    
    try:
        data = yf.download(ticker, start=start_dt, end=end_dt, progress=False, auto_adjust=False)
        
        if data.empty:
            print(f"❌ Data tidak ditemukan untuk {ticker} pada {tanggal}.")
            return

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data.reset_index(inplace=True)
        
        row = data.iloc[0]
        
        print("\n[DATA ORIGINAL YAHOO]")
        print(f"Open   : {row['Open']}")
        print(f"High   : {row['High']}")
        print(f"Low    : {row['Low']}")
        print(f"Close  : {row['Close']}")
        print(f"Volume : {int(row['Volume'])}")

        print("\n[DATA NORMALISASI (FRAKSI IDX)]")
        print(f"Open   : {get_idx_fraksi(row['Open'])}")
        print(f"High   : {get_idx_fraksi(row['High'])}")
        print(f"Low    : {get_idx_fraksi(row['Low'])}")
        print(f"Close  : {get_idx_fraksi(row['Close'])}")
        print(f"Volume : {int(row['Volume'])}")
        
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error: {e}")

TICKER = "bbrm"       
TANGGAL = "2021-12-17" 

check_stock_data(TICKER, TANGGAL)