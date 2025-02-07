import pandas as pd
import streamlit as st
from PIL import Image
import streamlit_antd_components as sac
from helper.logo_img import get_logo_pens, get_logo_sakinah
from option_menu.home.home import project_description
from option_menu.upload_data.upload_data import upload_data
from option_menu.upload_data.preprocessing import checking_data, preprocess_description_column
from option_menu.eda.items import items
from option_menu.eda.customers import customers
from option_menu.pola_pembelian.apriori import data_apriori, apriori_algorithm, apriori_visual, analyze_rules

st.set_page_config(layout="wide")

# session_state untuk menyimpan df hasil upload
if "df" not in st.session_state:
    st.session_state.df = None  # Awalnya None, baru diisi setelah upload

# Fungsi untuk memperbarui info data
def update_info_data():
    df = st.session_state.df
    if df is not None:
        df['TANGGAL'] = pd.to_datetime(df['TANGGAL'])
        start_date = df['TANGGAL'].min().date()
        end_date = df['TANGGAL'].max().date()
        record_count = len(df)
        st.session_state.info_data = f"Transaction data 2023 (Record data: {record_count})"
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
    else:
        st.session_state.info_data = "No data uploaded"
        st.session_state.start_date = None
        st.session_state.end_date = None

update_info_data()  # **Perbarui info data saat pertama kali aplikasi dijalankan**

with st.sidebar:
    st.markdown("# Sakinah Mart Analytics")
    selected_menu = sac.menu([
        sac.MenuItem('HOME', icon='house-fill'),
        sac.MenuItem('Upload Data', icon='upload'),
        sac.MenuItem('EDA', icon='pie-chart-fill', description='Exploratory Data Analysis', children=[
            sac.MenuItem('Customers', icon='people-fill'),
            sac.MenuItem('Items', icon='box-seam-fill')]),
        sac.MenuItem('Pola Pembelian', icon='basket2-fill', description='Apriori Implementation'),
        sac.MenuItem('Prediksi Stok Barang', icon='bar-chart-line-fill', description='Vector Autoregressive Implementation'),
        sac.MenuItem(type='divider'),
    ], size='md', open_all=True, color='white', variant='left-bar', indent=30)
    
    st.markdown("<div style='text-align: center; font-size: smaller; color: #004e26'>Created By: Nadine Aliyah Mustafa</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: smaller; color: #004e26'>Supported By: </div>", unsafe_allow_html=True)
    st.caption(" ")
    cols = st.columns(4)
    with cols[1]:
        logo_path = get_logo_pens()
        logo_image = Image.open(logo_path)
        st.image(logo_image, width=50)
    with cols[2]:
        logo_path = get_logo_sakinah()
        logo_image = Image.open(logo_path)
        st.image(logo_image, width=300)

if selected_menu == "HOME":
    project_description()

elif selected_menu == "Upload Data":
    df_uploaded = upload_data()

    if df_uploaded is not None:
        df_before = df_uploaded.copy()  # **Simpan data sebelum preprocessing**
        df_check = checking_data(df_uploaded)  

        if df_check is not None:
            df_final = preprocess_description_column(df_check.copy())  # **Pastikan df_check tidak berubah**

            # **Simpan df_final ke session_state agar digunakan di menu lain**
            st.session_state.df = df_final.copy()
            update_info_data()  # **Perbarui info data setelah upload**
            
            cols = st.columns(2)
            with cols[0]:
                st.write("Data sebelum preprocessing:")
                st.dataframe(df_before)  # **Menampilkan data asli**
            with cols[1]:
                st.write("Data setelah preprocessing:")
                st.dataframe(df_final)  # **Menampilkan data yang telah diproses**

elif selected_menu == "Customers":
    if st.session_state.df is not None:
        customers(st.session_state.df, st.session_state.start_date, st.session_state.end_date, st.session_state.info_data)
    else:
        st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")

elif selected_menu == "Items":
    if st.session_state.df is not None:
        items(st.session_state.df, st.session_state.start_date, st.session_state.end_date, st.session_state.info_data)
    else:
        st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")
        
elif selected_menu == "Pola Pembelian":
    if st.session_state.df is not None:
        basket_sets = data_apriori(st.session_state.df, st.session_state.start_date, st.session_state.end_date)
        table_result = apriori_algorithm(basket_sets)
        table_result = table_result[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
        st.dataframe(table_result, height=200)    
        apriori_visual(table_result)
        analyze_rules(table_result)
    else:
        st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")
