# import pandas as pd
# import streamlit as st
# from PIL import Image
# import streamlit_antd_components as sac
# from helper.logo_img import get_logo_pens, get_logo_sakinah
# from option_menu.home.home import project_description
# from option_menu.upload_data.upload_data import upload_data
# from option_menu.upload_data.preprocessing import checking_data, preprocess_description_column
# from option_menu.eda.items import items
# from option_menu.eda.transactions import transactions
# from option_menu.pola_pembelian.apriori import data_apriori, apriori_algorithm, apriori_visual,analyze_rules

# st.set_page_config(layout="wide")

# # session_state untuk menyimpan df hasil upload
# if "df" not in st.session_state:
#     st.session_state.df = None  # Awalnya None, baru diisi setelah upload

# # Fungsi untuk memperbarui info data
# def update_info_data():
#     df = st.session_state.df
#     if df is not None:
#         df['TANGGAL'] = pd.to_datetime(df['TANGGAL'])
#         start_date = df['TANGGAL'].min().date()
#         end_date = df['TANGGAL'].max().date()
#         record_count = len(df)
#         st.session_state.info_data = f"Transaction data 2023 (Record data: {record_count})"
#         st.session_state.start_date = start_date
#         st.session_state.end_date = end_date
#     else:
#         st.session_state.info_data = "No data uploaded"
#         st.session_state.start_date = None
#         st.session_state.end_date = None

# update_info_data()  # **Perbarui info data saat pertama kali aplikasi dijalankan**

# with st.sidebar:
#     st.markdown("# Supermarket XYZ Analytics")
#     selected_menu = sac.menu([
#         sac.MenuItem('HOME', icon='house-fill'),
#         sac.MenuItem('Upload Data', icon='upload'),
#         sac.MenuItem('EDA', icon='pie-chart-fill', description='Exploratory Data Analysis', children=[
#             sac.MenuItem('Transactions', icon='people-fill'),
#             sac.MenuItem('Items', icon='box-seam-fill')]),
#         sac.MenuItem('Pola Pembelian', icon='basket2-fill', description='Apriori Implementation'),
#         #sac.MenuItem('Prediksi Penjualan', icon='bar-chart-line-fill', description='Vector Autoregressive Implementation'),
#         sac.MenuItem(type='divider'),
#     ], size='md', open_all=True, color='white', variant='left-bar', indent=30)
    
#     st.markdown("<div style='text-align: center; font-size: smaller; color: #004e26'>Created By: Nadine Aliyah Mustafa</div>", unsafe_allow_html=True)
#     #st.markdown("<div style='text-align: center; font-size: smaller; color: #004e26'>Supported By: </div>", unsafe_allow_html=True)
#     # st.caption(" ")
#     # cols = st.columns(4)
#     # with cols[1]:
#     #     logo_path = get_logo_pens()
#     #     logo_image = Image.open(logo_path)
#     #     st.image(logo_image, width=50)
#     # with cols[2]:
#     #     logo_path = get_logo_sakinah()
#     #     logo_image = Image.open(logo_path)
#     #     st.image(logo_image, width=300)

# if selected_menu == "HOME":
#     project_description()

# elif selected_menu == "Upload Data":
#     df_uploaded = upload_data()

#     if df_uploaded is not None:
#         df_before = df_uploaded.copy()  # **Simpan data sebelum preprocessing**
#         df_check = checking_data(df_uploaded)  

#         if df_check is not None:
#             df_final = preprocess_description_column(df_check.copy())  # **Pastikan df_check tidak berubah**

#             # **Simpan df_final ke session_state agar digunakan di menu lain**
#             st.session_state.df = df_final.copy()
#             update_info_data()  # **Perbarui info data setelah upload**

# elif selected_menu == "Transactions":
#     if st.session_state.df is not None:
#         transactions(st.session_state.df, st.session_state.start_date, st.session_state.end_date, st.session_state.info_data)
#     else:
#         st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")

# elif selected_menu == "Items":
#     if st.session_state.df is not None:
#         items(st.session_state.df, st.session_state.start_date, st.session_state.end_date, st.session_state.info_data)
#     else:
#         st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")
        
# elif selected_menu == "Pola Pembelian":
#     if st.session_state.df is not None:
#         basket_sets = data_apriori(st.session_state.df, st.session_state.start_date, st.session_state.end_date)
#         table_result = apriori_algorithm(basket_sets)
#         table_result = table_result[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
#         with st.expander("Table Result"):
#             st.dataframe(table_result, height=200)
#             st.caption("Keterangan Kolom")
#             st.caption("""
#             - **antecedents**: Item yang muncul terlebih dahulu.
#             - **consequents**: Item yang cenderung muncul setelah antecedents.
#             - **support**: Seberapa sering kombinasi tersebut muncul di seluruh transaksi.
#             - **confidence**: Seberapa besar kemungkinan item consequents muncul jika item antecedents sudah ada.
#             - **lift**: Mengukur seberapa kuat hubungan antara antecedents dan consequents. Nilai >1 berarti ada hubungan yang kuat.
#             """)

#         with st.expander("Filter Rules"):
#             rules_to_show = st.slider(
#                 'Jumlah rules untuk divisualisasikan dan dianalisis',
#                 min_value=1,
#                 max_value=len(table_result),
#                 value=3,
#                 step=1,
#             )

#         apriori_visual(table_result, rules_to_show)
#         analyze_rules(table_result, rules_to_show)

#     else:
#         st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")

# elif selected_menu == "Prediksi Penjualan":
#     if st.session_state.df is not None:
#         items(st.session_state.df, st.session_state.start_date, st.session_state.end_date, st.session_state.info_data)
#     else:
#         st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")

# app.py (REVISI)

import pandas as pd
import streamlit as st
from PIL import Image
import streamlit_antd_components as sac
from helper.logo_img import get_logo_pens, get_logo_sakinah
from option_menu.home.home import project_description
from option_menu.upload_data.upload_data import upload_data
from option_menu.upload_data.preprocessing import process_uploaded_data
from option_menu.eda.items import items
from option_menu.eda.transactions import transactions
from option_menu.pola_pembelian.apriori import generate_rules, apriori_visual, analyze_rules
from option_menu.prediksi_penjualan.rnn import show_rnn_prediction_page 

st.set_page_config(layout="wide")

# session_state CUKUP untuk menyimpan DataFrame yang sudah diproses
if "df" not in st.session_state:
    st.session_state.df = None
# <<< PERBAIKAN: st.session_state.apriori_table_result tidak diperlukan lagi, akan digantikan oleh fungsi cache.

# Fungsi ini tetap sama, bagus untuk UI
def update_info_data():
    df = st.session_state.df
    if df is not None:
        if 'TANGGAL' in df.columns:
            # Pastikan konversi hanya dilakukan sekali jika belum
            if not pd.api.types.is_datetime64_any_dtype(df['TANGGAL']):
                df['TANGGAL'] = pd.to_datetime(df['TANGGAL'])
            start_date = df['TANGGAL'].min().date()
            end_date = df['TANGGAL'].max().date()
        else:
            start_date = None
            end_date = None
        
        record_count = len(df)
        st.session_state.info_data = f"Transaction data (Record data: {record_count})"
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
    else:
        st.session_state.info_data = "No data uploaded"
        st.session_state.start_date = None
        st.session_state.end_date = None

# Sidebar (Tidak ada perubahan, sudah bagus)
with st.sidebar:
    st.markdown("# Sakinah Mart Analytics")
    selected_menu = sac.menu([
        sac.MenuItem('HOME', icon='house-fill'),
        sac.MenuItem('Upload Data', icon='upload'),
        sac.MenuItem('EDA', icon='pie-chart-fill', description='Exploratory Data Analysis', children=[
            sac.MenuItem('Transactions', icon='people-fill'),
            sac.MenuItem('Items', icon='box-seam-fill')]),
        sac.MenuItem('Pola Pembelian', icon='basket2-fill', description='Apriori Implementation'),
        sac.MenuItem('Tren dan Prediksi Penjualan', icon='bar-chart-line-fill', description='Recurrent Neural Network (RNN)'), 
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
        
# Inisialisasi info data di awal
update_info_data()


# --- Logic Halaman Utama ---

if selected_menu == "HOME":
    project_description()

elif selected_menu == "Upload Data":
    df_uploaded = upload_data()

    if df_uploaded is not None:
        # <<< PERBAIKAN: Panggil satu fungsi cache untuk memproses seluruh data
        # Fungsi ini akan membaca, memeriksa, dan membersihkan data.
        # Karena di-cache, proses ini hanya berjalan sekali untuk file yang sama.
        with st.spinner("Memeriksa dan memproses data untuk pertama kali..."):
            final_df = process_uploaded_data(df_uploaded)
        
        if final_df is not None:
            st.session_state.df = final_df
            update_info_data() # Update info setelah df baru disimpan
        else:
            # Jika process_uploaded_data mengembalikan None, berarti ada error
            st.error("Gagal memproses data. Silakan periksa format file Anda.")

elif selected_menu == "Transactions":
    if st.session_state.df is not None:
        transactions(st.session_state.df, st.session_state.start_date, st.session_state.end_date, st.session_state.info_data)
    else:
        st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")

elif selected_menu == "Items":
    if st.session_state.df is not None:
        items(st.session_state.df, st.session_state.start_date, st.session_state.end_date, st.session_state.info_data)
    else:
        st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")
        
elif selected_menu == "Pola Pembelian":
    if st.session_state.df is not None:
        # <<< PERUBAHAN DI SINI >>>
        # Kita panggil fungsi generate_rules baru yang sudah di-cache
        # dan simpan hasilnya ke st.session_state agar sisa kode Anda tetap berfungsi
        from option_menu.pola_pembelian.apriori import generate_rules # Pastikan impor ini ada

        table_result = generate_rules(st.session_state.df)
        
        # Pembersihan kolom yang mungkin diperlukan setelah dibaca dari cache
        table_result["antecedents"] = table_result["antecedents"].apply(lambda x: frozenset(eval(x)) if isinstance(x, str) else x)
        table_result["consequents"] = table_result["consequents"].apply(lambda x: frozenset(eval(x)) if isinstance(x, str) else x)

        table_result = table_result[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
        st.session_state.apriori_table_result = table_result.copy()

        # Tampilkan UI asli Anda
        st.header("Pola Pembelian")
        days_selected = (st.session_state.end_date - st.session_state.start_date).days + 1
        day_text = "day" if days_selected == 1 else "days"
        st.caption(f"Based on data from {st.session_state.start_date} to {st.session_state.end_date} ({days_selected} {day_text}).")

        with st.expander("Table Result"):
            st.dataframe(table_result, height=200)
            st.caption("Keterangan Kolom")
            st.caption("""
            - **antecedents**: Item yang muncul terlebih dahulu.
            - **consequents**: Item yang cenderung muncul setelah antecedents.
            - **support**: Seberapa sering kombinasi tersebut muncul di seluruh transaksi.
            - **confidence**: Seberapa besar kemungkinan item consequents muncul jika item antecedents sudah ada.
            - **lift**: Mengukur seberapa kuat hubungan antara antecedents dan consequents. Nilai >1 berarti ada hubungan yang kuat.
            """)

        with st.expander("Filter Rules"):
            rules_to_show = st.slider(
                'Jumlah rules untuk divisualisasikan dan dianalisis',
                min_value=1,
                max_value=len(table_result),
                value=min(3, len(table_result)),
                step=1,
            )

        apriori_visual(table_result, rules_to_show)
        analyze_rules(table_result, rules_to_show)

    else:
        st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")

elif selected_menu == "Tren dan Prediksi Penjualan": 
    if st.session_state.df is None:
        st.warning("Silakan unggah data terlebih dahulu di menu 'Upload Data'.")
    else:
        # <<< PERBAIKAN: Dapatkan kembali hasil Apriori dengan memanggil fungsi cache lagi.
        # Ini sangat cepat dan memastikan data konsisten.
        apriori_result = generate_rules(st.session_state.df)
        if apriori_result is None or apriori_result.empty:
            st.warning("Jalankan analisis 'Pola Pembelian' atau pastikan data Anda dapat menghasilkan aturan asosiasi.")
        else:
            show_rnn_prediction_page(st.session_state.df, apriori_result)

