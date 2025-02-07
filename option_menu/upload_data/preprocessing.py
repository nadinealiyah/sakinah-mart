import pandas as pd
import re
import streamlit as st

@st.cache_data
def check_columns(df, expected_columns):
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.success(f"⚠️ Kolom berikut tidak ditemukan dalam data: {missing_columns}")
        return False
    #st.success("✅ Format kolom sesuai.")
    return True

@st.cache_data
def check_missing_values(df):
    missing_counts = df.isnull().sum()
    total_missing = missing_counts.sum()

    if total_missing > 0:
        st.success(f"⚠️ Terdapat {total_missing} missing values dalam data!")
        return False

    #st.success("✅ Tidak ada missing values.")
    return True

@st.cache_data
def fix_data_types(df, expected_dtypes):
    for col, expected_dtype in expected_dtypes.items():
        if col in df.columns:
            try:
                if expected_dtype == 'datetime64[ns]':
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                elif expected_dtype == 'int64':
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                elif expected_dtype == 'object':
                    df[col] = df[col].astype(str)
            except Exception as e:
                st.error(f"⚠️ Error saat mengonversi kolom '{col}': {e}")
    #st.success("✅ Semua tipe data telah sesuai.")
    return df

@st.cache_data
def checking_data(df):
    expected_columns = ['TANGGAL', 'NO TRANSAKSI', 'NAMA BARANG', 'QTY']
    expected_dtypes = {
        'TANGGAL': 'datetime64[ns]',
        'NO TRANSAKSI': 'int64',
        'NAMA BARANG': 'object',
        'QTY': 'int64'
    }

    # 1. Cek format kolom
    if not check_columns(df, expected_columns):
        return None  # Jika format kolom salah, hentikan proses

    # 2. Cek missing values
    if not check_missing_values(df):
        return None  # Jika ada missing values, hentikan proses

    # 3. Perbaiki tipe data
    df = fix_data_types(df, expected_dtypes)

    return df

@st.cache_data
def preprocess_description_column(df, column_name='NAMA BARANG'):
    def preprocess_text(text):
        if pd.isnull(text):  
            return text
        
        text = re.sub(r'\s{3,}.*', '', text)  # Hapus spasi double dan teks setelahnya
        text = re.sub(r'[^\w\s/]', ' ', text)  # Hapus tanda baca kecuali /
        text = ' '.join(word for word in text.split() if not re.search(r'\d{5,}', word))  # Hapus kata dengan >= 5 angka
        text = re.sub(r'\s+', ' ', text).strip()  # Hapus spasi ganda & trim
        
        return text
    
    df[column_name] = df[column_name].apply(preprocess_text)
    #st.success("✅ Kolom 'NAMA BARANG' telah dibersihkan.")
    
    return df
