import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import streamlit_shadcn_ui as ui

def items(df):
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['MONTH'] = df['DATE'].dt.month_name()

    selected_month = st.selectbox("Pilih Bulan", options=df['MONTH'].unique(), index=0)
    filtered_data = df[df['MONTH'] == selected_month]

    total_qty = filtered_data["QTY"].sum()
    unique_items = filtered_data["DESCRIPTION"].nunique()

    # Ambil bulan sebelumnya
    prev_month = pd.to_datetime(df['DATE']).dt.month_name().shift(1).unique()[0]
    prev_month_data = df[df['MONTH'] == prev_month]
    
    # Hitung total dan jenis barang bulan sebelumnya
    total_qty_prev_month = prev_month_data["QTY"].sum()
    unique_items_prev_month = prev_month_data["DESCRIPTION"].nunique()

    # Menghitung kenaikan atau penurunan
    total_qty_diff = total_qty - total_qty_prev_month
    unique_items_diff = unique_items - unique_items_prev_month

    # Metrik dan deskripsi dengan perubahan
    cols = st.columns(3)
    with cols[0]:
        description_qty = f"+{total_qty_diff}" if total_qty_diff > 0 else f"{total_qty_diff}"
        ui.metric_card(
            title="Total Barang yang Dibeli:",
            content=f"{total_qty}",
            description=f"{description_qty} from last month")

    with cols[1]:
        description_items = f"+{unique_items_diff}" if unique_items_diff > 0 else f"{unique_items_diff}"
        ui.metric_card(
            title="Jenis Barang yang Dibeli:",
            content=f"{unique_items}",
            description=f"{description_items} from last month")
    
    # Bar chart untuk Top 10 Barang
    top_products = filtered_data.groupby('DESCRIPTION')['QTY'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=top_products.values, y=top_products.index, palette="viridis")
    plt.title("Top 10 Produk yang Laku Dibeli", fontsize=16)
    plt.xlabel("Jumlah Terjual", fontsize=12)
    plt.ylabel("Deskripsi Produk", fontsize=12)
    for i, v in enumerate(top_products.values):
        ax.text(v + 0.2, i, f'{v}', color='black', va='center')
    plt.tight_layout()
    st.pyplot(plt.gcf())