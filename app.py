import pandas as pd
import streamlit as st
from PIL import Image
import streamlit_antd_components as sac
from helper.logo_img import get_logo_pens, get_logo_sakinah
from option_menu.home.project_description import project_description
from option_menu.eda.items import items
from option_menu.eda.customers import customers
# from mlxtend.frequent_patterns import apriori, association_rules

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
# elif selected_menu == "Pola Pembelian":

#     # Judul dan informasi aplikasi
#     st.title("Pola Pembelian")
#     st.subheader("Data contains transaction records for Apriori analysis")

#     # Membaca data lokal
#     DATA_PATH = "final_data.xlsx"  # Pastikan file ini ada di direktori yang sama dengan kode Streamlit
#     groceries = pd.read_excel(DATA_PATH)

#     # Pra-pemrosesan data
#     groceries.rename(columns={'NO.TRANSAKSI': 'id', 'DESCRIPTION': 'item', 'DATE': 'DATE'}, inplace=True)
#     groceries['DATE'] = pd.to_datetime(groceries['DATE'])
#     groceries['year'] = groceries['DATE'].dt.year
#     groceries['month'] = groceries['DATE'].dt.month
#     groceries['day'] = groceries['DATE'].dt.day
#     groceries['weekday'] = groceries['DATE'].dt.weekday

#     # Mengatur ulang kolom
#     groceries = groceries[['id', 'DATE', 'year', 'month', 'day', 'weekday', 'item']]

#     # Membuat sparse matrix
#     temp = groceries.copy()
#     temp['qty_purchased'] = groceries['id'].map(groceries['id'].value_counts())
#     basket = (temp.groupby(['id', 'item'])['qty_purchased']
#             .sum().unstack().reset_index().fillna(0).set_index('id'))

#     def encode(x):
#         return 1 if x > 0 else 0

#     basket_sets = basket.applymap(encode)

#     # Sidebar untuk parameter model
#     st.sidebar.title("Model Parameters")
#     st.sidebar.write("Set thresholds for Apriori analysis")
#     fixed_support = 0.001  # Support tetap
#     min_confidence = st.sidebar.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.01)
#     min_lift = st.sidebar.slider("Minimum Lift", 0.0, 10.0, 1.0, 0.1)

#     # Menjalankan algoritma Apriori
#     frequent_itemsets = apriori(basket_sets, min_support=fixed_support, use_colnames=True, low_memory=True)
#     rules = association_rules(frequent_itemsets, num_itemsets=len(frequent_itemsets),  min_threshold=1)
#     filtered_rules = rules[(rules['confidence'] >= min_confidence) & (rules['lift'] >= min_lift)]

#     # Tampilkan rentang data
#     st.write(f"Data contains from {groceries['DATE'].min().date()} to {groceries['DATE'].max().date()} "
#             f"(Record count: {len(groceries)})")

#     # Tampilkan hasil rule
#     st.subheader("Hasil Rule")
#     if not filtered_rules.empty:
#         st.dataframe(filtered_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])
#     else:
#         st.write("No rules meet the specified criteria.")

#     # Analisis hasil
#     st.subheader("Hasil Analisis")
#     if not filtered_rules.empty:
#         st.write(f"{len(filtered_rules)} rules identified with Support >= {fixed_support}, "
#                 f"Confidence >= {min_confidence}, and Lift >= {min_lift}.")
#     else:
#         st.write("No significant patterns found with the current thresholds.")

