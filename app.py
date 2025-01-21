import pandas as pd
import streamlit as st
from PIL import Image
import streamlit_antd_components as sac
from helper.logo_img import get_logo_pens, get_logo_sakinah
from option_menu.home.project_description import project_description
from option_menu.eda.items import items
from option_menu.eda.customers import customers
from option_menu.pola_pembelian.apriori import data_apriori, apriori_algorithm, apriori_visual, analyze_rules

st.set_page_config(layout="wide")

# import data
df = pd.read_excel('final_data.xlsx')
df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')

# info data
df['DATE'] = pd.to_datetime(df['DATE'])
start_date = df['DATE'].min().date() 
end_date = df['DATE'].max().date() 
record_count = len(df)
info_data = f"Transaction data 2023 (Record data: {record_count})"

with st.sidebar:
    st.markdown("# Sakinah Mart Analytics")
    selected_menu = sac.menu([
        sac.MenuItem('HOME', icon='house-fill'),
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
    cols = st.columns(6)
    with cols[2]:
        logo_path = get_logo_pens()
        logo_image = Image.open(logo_path)
        st.image(logo_image, width=50)
    with cols[3]:
        logo_path = get_logo_sakinah()
        logo_image = Image.open(logo_path)
        st.image(logo_image, width=300)

if selected_menu == "HOME":
    project_description()
elif selected_menu == "Customers":
    customers(df, start_date, end_date, info_data)
elif selected_menu == "Items":
    items(df, start_date, end_date, info_data)
elif selected_menu == "Pola Pembelian":
    basket_sets = data_apriori(df, start_date, end_date)
    table_result = apriori_algorithm(basket_sets)
    table_result = table_result[['antecedents','consequents','support','confidence','lift']]
    st.dataframe(table_result, height=200)
    visual_result = apriori_visual(table_result)
    analyze_rules(table_result)