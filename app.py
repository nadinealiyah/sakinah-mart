import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_antd_components as sac

from option_menu.home.project_description import project_description
from option_menu.eda.items import items
from option_menu.eda.customers import customers

# Menampilkan menu di sidebar
with st.sidebar:
    main_menu = option_menu("Sakinah Mart Analytics", 
                            ["HOME", "Exploratory Data Analysis (EDA)", "Pola Pembelian", "Prediksi Stok Barang"], 
                            icons=["house-fill", "pie-chart-fill", "basket2-fill", "bar-chart-line-fill"],
                            menu_icon="shop",
                            default_index=0)
    
    st.markdown("""<div style="text-align: center;">Created By: Nadine Aliyah Mustafa</div>""", unsafe_allow_html=True)

# import data
df = pd.read_excel('final_data.xlsx')
df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')

# Info data
df['DATE'] = pd.to_datetime(df['DATE'])
start_date = df['DATE'].min().date() 
end_date = df['DATE'].max().date() 
record_count = len(df)
info_data = f"Data contains from **{start_date}** to **{end_date}** (Record data: {record_count})"

if main_menu == "HOME":
    project_description()

elif main_menu == "Exploratory Data Analysis (EDA)":
    st.header("Exploratory Data Analysis (EDA)")
    st.caption(info_data)

    button = sac.buttons(
        items=["Customers", "Items"],
        index=0,
        direction='horizontal',
        radius='lg',
        return_index=False,
    )

    if button == "Customers":
        customers(df)
    elif button == "Items":
        items(df)