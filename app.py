import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_antd_components as sac
from option_menu.home.project_description import project_description
from option_menu.eda.items import items
from option_menu.eda.customers import customers

st.set_page_config(layout="wide")

# import data
df = pd.read_excel('final_data.xlsx')
df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')

# info data
df['DATE'] = pd.to_datetime(df['DATE'])
start_date = df['DATE'].min().date() 
end_date = df['DATE'].max().date() 
record_count = len(df)
info_data = f"Data contains from **{start_date}** to **{end_date}** (Record data: {record_count})"

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
    ], size='lg', open_all=True, variant='left-bar', indent=30)
    st.caption("Created By: Nadine Aliyah Mustafa")

if selected_menu == "HOME":
    project_description()
elif selected_menu == "Customers":
    customers(df, info_data)
elif selected_menu == "Items":
    items(df)
