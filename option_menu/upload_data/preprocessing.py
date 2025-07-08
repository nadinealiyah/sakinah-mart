import pandas as pd
import re
import streamlit as st

# Helper functions (tidak perlu di-cache secara individual lagi)
def check_columns(df, expected_columns):
    """Memeriksa apakah semua kolom yang diharapkan ada di DataFrame."""
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.error(f"❌ Kolom berikut tidak ditemukan dalam data: {', '.join(missing_columns)}.")
        return False
    return True

def handle_missing_values(df):
    """
    Memeriksa missing values. Jika ada, tampilkan detailnya, hapus barisnya, 
    dan kembalikan DataFrame yang sudah bersih.
    """
    missing_counts = df.isnull().sum()
    total_missing = missing_counts.sum()

    if total_missing > 0:
        # Tampilkan peringatan yang bisa diperluas (expander)
        with st.expander(f"⚠️ Ditemukan {total_missing} data kosong. Detail:"):
            missing_details = missing_counts[missing_counts > 0]
            for col, count in missing_details.items():
                # Tampilkan baris (indeks) mana saja yang kosong untuk setiap kolom
                rows_with_missing = df[df[col].isnull()].index.tolist()
                st.write(f"- Kolom **'{col}'** memiliki **{count}** data kosong pada baris: `{rows_with_missing[:5]}`")
        
            # Hapus baris yang mengandung missing value
            df_cleaned = df.dropna()
            st.info(f"ℹ️ {total_missing} baris yang mengandung data kosong telah dihapus secara otomatis.")
        return df_cleaned
    
    return df

def fix_data_types(df, expected_dtypes):
    """Mengonversi kolom ke tipe data yang diharapkan."""
    for col, expected_dtype in expected_dtypes.items():
        if col in df.columns:
            try:
                if 'datetime' in expected_dtype:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                elif 'int' in expected_dtype:
                    # Menggunakan float dulu untuk menangani nilai non-numerik yang menjadi NaN, lalu ke Int64
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    df[col] = df[col].astype('Int64') # Int64 bisa menangani NaN
                elif 'object' in expected_dtype:
                    df[col] = df[col].astype(str)
            except Exception as e:
                st.error(f"⚠️ Error saat mengonversi kolom '{col}': {e}")
    return df

def preprocess_text_column(df, column_name='NAMA BARANG'):
    """Membersihkan kolom teks (NAMA BARANG)."""
    def preprocess_text(text):
        if pd.isnull(text) or not isinstance(text, str):
            return '' # Kembalikan string kosong jika data bukan string atau null
        
        text = str(text)
        text = re.sub(r'\s{3,}.*', '', text)  # Hapus spasi double dan teks setelahnya
        text = re.sub(r'[^\w\s/]', ' ', text)  # Hapus tanda baca kecuali /
        text = ' '.join(word for word in text.split() if not re.search(r'\d{5,}', word))  # Hapus kata dengan >= 5 angka
        text = re.sub(r'\s+', ' ', text).strip().upper() # Hapus spasi ganda, trim, dan UPPERCASE
        return text
    
    df[column_name] = df[column_name].apply(preprocess_text)
    return df

# --- FUNGSI UTAMA YANG DI-CACHE ---
# Inilah fungsi yang akan kita panggil dari app.py
@st.cache_data(show_spinner=False) # Spinner akan kita kontrol manual di app.py
def process_uploaded_data(df_raw):
    """
    Pipeline lengkap untuk memproses DataFrame yang baru di-upload.
    Menerapkan semua langkah preprocessing dan mengembalikan DataFrame yang bersih.
    Fungsi ini di-cache untuk efisiensi.
    """
    # 1. Buat salinan untuk menghindari mengubah data asli di luar fungsi
    df = df_raw.copy()
    
    # 2. Definisikan ekspektasi
    expected_columns = ['TANGGAL', 'NO TRANSAKSI', 'NAMA BARANG', 'QTY']
    expected_dtypes = {
        'TANGGAL': 'datetime64[ns]',
        'NO TRANSAKSI': 'int64',
        'NAMA BARANG': 'object',
        'QTY': 'int64'
    }

    # 3. Jalankan pipeline preprocessing
    if not check_columns(df, expected_columns):
        return None  # Hentikan jika kolom utama tidak ada

    df = fix_data_types(df, expected_dtypes)
    df = handle_missing_values(df)
    df = preprocess_text_column(df, 'NAMA BARANG')
    
    # Hapus transaksi tanpa item setelah preprocessing
    df.dropna(subset=['NAMA BARANG', 'NO TRANSAKSI'], inplace=True)
    df = df[df['NAMA BARANG'] != '']
    return df