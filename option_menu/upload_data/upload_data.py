import streamlit as st
import pandas as pd

def upload_data():
    st.header("Upload Data")
    uploaded_file = st.file_uploader(
        "Pilih file Excel", 
        type=["xlsx", "xls"],
        help="Pastikan data memiliki kolom ['TANGGAL', 'NO TRANSAKSI', 'NAMA BARANG', 'QTY']"
    )

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            return df  
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")
            return None  

    return None 

