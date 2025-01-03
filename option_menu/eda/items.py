import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import streamlit_shadcn_ui as ui

def items(df, info_data):
    st.header("EDA - Items")
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['MONTH'] = df['DATE'].dt.month_name()
    df['WEEK'] = (df['DATE'].dt.day - 1) // 7 + 1

    placeholder = st.empty()

    cols = st.columns(2)
    with cols[0]:
        with st.expander("Filter Date"):
            st.caption(info_data)
            cols = st.columns(2)
            with cols[0]:
                selected_month = st.selectbox("Select Month:", df['MONTH'].unique())
            with cols[1]:
                selected_week = st.number_input("Select Week:", min_value=df['WEEK'].min(), max_value=df['WEEK'].max())
    
    placeholder.caption(f"Based on data from Week {selected_week} of {selected_month}.")

    filtered_data = df[(df['MONTH'] == selected_month) & (df['WEEK'] == selected_week)]

    total_qty = filtered_data["QTY"].sum()
    unique_items = filtered_data["DESCRIPTION"].nunique()

    # Ambil minggu sebelumnya
    if selected_month == 'January' and selected_week == 1:
        prev_week = None  # Tidak ada minggu sebelumnya untuk Januari minggu 1
    else:
        prev_week = selected_week - 1 if selected_week > 1 else 5  # Jika minggu 1, maka ambil minggu 5

    # Jika minggu sebelumnya ada, ambil data minggu sebelumnya
    if prev_week is not None:
        prev_week_data = df[(df['MONTH'] == selected_month) & (df['WEEK'] == prev_week)]

        # Hitung total dan jenis barang minggu sebelumnya
        total_qty_prev_week = prev_week_data["QTY"].sum()
        unique_items_prev_week = prev_week_data["DESCRIPTION"].nunique()

        # Menghitung kenaikan atau penurunan
        total_qty_diff = total_qty - total_qty_prev_week
        unique_items_diff = unique_items - unique_items_prev_week

        # Metrik dan deskripsi dengan perubahan
        cols = st.columns(3)
        with cols[0]:
            description_qty = f"+{total_qty_diff}" if total_qty_diff > 0 else f"{total_qty_diff}"
            ui.metric_card(
                title="Total Barang yang Dibeli:",
                content=f"{int(total_qty)}",
                description=f"{description_qty} from last week")

        with cols[1]:
            description_items = f"+{unique_items_diff}" if unique_items_diff > 0 else f"{unique_items_diff}"
            ui.metric_card(
                title="Jenis Barang yang Dibeli:",
                content=f"{int(unique_items)}",
                description=f"{description_items} from last week")
    else:
        # Jika tidak ada minggu sebelumnya (misalnya Januari minggu 1), tampilkan informasi tanpa perubahan
        cols = st.columns(3)
        with cols[0]:
            ui.metric_card(
                title="Total Barang yang Dibeli:",
                content=f"{int(total_qty)}",
                description="No previous week data available")

        with cols[1]:
            ui.metric_card(
                title="Jenis Barang yang Dibeli:",
                content=f"{int(unique_items)}",
                description="No previous week data available")

    # Bar chart untuk Top 10 Barang
    st.markdown(
            "<div style='text-align: center; font-weight: bold; font-size: 18px;'>Top 10 Produk yang Laku Dibeli</div>", 
            unsafe_allow_html=True
            )
    top_products = filtered_data.groupby('DESCRIPTION')['QTY'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(6, 3))
    ax = sns.barplot(x=top_products.values, y=top_products.index, palette="viridis")
    plt.xticks(fontsize=5)
    plt.yticks(fontsize=5)
    plt.xlabel("Jumlah Terjual", fontsize=6)
    plt.ylabel("Deskripsi Produk", fontsize=6)
    for i, v in enumerate(top_products.values):
        ax.text(int(v) + 0.2, i, f'{int(v)}', color='black', va='center', fontsize=5)
    plt.tight_layout()
    st.pyplot(plt.gcf())