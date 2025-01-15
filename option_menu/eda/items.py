import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from helper.custom_metric_card import metric_card

def items(df, start_date, end_date, info_data):
    st.header("EDA - Items")
    df['DATE'] = pd.to_datetime(df['DATE'])

    placeholder = st.empty()

    # Filter 
    cols = st.columns(3)
    with cols[0]:
        with st.expander("Filter"):
            dates = st.date_input(
                label="Select the date",
                value=(start_date, end_date),
                min_value=start_date,
                max_value=end_date,
                help=info_data
            )
            if len(dates) != 2:
                st.warning("Please select start and end dates.")
                st.stop()

            start_date, end_date = dates

    # Hitung jumlah hari yang dipilih
    days_selected = (end_date - start_date).days + 1
    day_text = "day" if days_selected == 1 else "days"
    placeholder.caption(f"Based on data from {start_date} to {end_date} ({days_selected} {day_text}).")

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Menentukan rentang waktu sebelumnya
    prev_start_date = start_date - pd.Timedelta(days=days_selected)
    prev_end_date = end_date - pd.Timedelta(days=days_selected)

    # Memastikan rentang waktu sebelumnya masih dalam range dataset
    if prev_start_date < df['DATE'].min() or prev_end_date < df['DATE'].min():
        prev_filtered_df = pd.DataFrame()  # Rentang sebelumnya di luar data
    else:
        prev_filtered_df = df[(df['DATE'] >= prev_start_date) & (df['DATE'] <= prev_end_date)]

    # Filter data untuk rentang waktu yang dipilih
    filtered_df = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]

    # Menghitung total dan jenis barang
    total_qty = filtered_df["QTY"].sum()
    unique_items = filtered_df["DESCRIPTION_CLEANED"].nunique()

    # Mengecek apakah data tersedia untuk rentang sebelumnya
    if not prev_filtered_df.empty:
        total_qty_prev = prev_filtered_df["QTY"].sum()
        unique_items_prev = prev_filtered_df["DESCRIPTION_CLEANED"].nunique()

        # Menghitung kenaikan atau penurunan
        total_qty_diff = int(total_qty - total_qty_prev)
        unique_items_diff = int(unique_items - unique_items_prev)

        description_qty = f"+{total_qty_diff}" if total_qty_diff > 0 else f"{total_qty_diff}"
        description_items = f"+{unique_items_diff}" if unique_items_diff > 0 else f"{unique_items_diff}"
        description_qty_text = f"{description_qty} from the previous {days_selected} {day_text}."
        description_items_text = f"{description_items} from the previous {days_selected} {day_text}."
    else:
        description_qty_text = f"No previous data available for the selected range ({days_selected} {day_text})."
        description_items_text = f"No previous data available for the selected range ({days_selected} {day_text})."

    # Metric Card
    cols = st.columns(3)
    with cols[0]:
        metric_card(
            title="Total Barang yang Dibeli:",
            content=f"{int(total_qty)}",
            description=description_qty_text,
            color='#009b4c',
            icon="bi bi-inboxes"
        )
    with cols[1]:
        metric_card(
            title="Jenis Barang yang Dibeli:",
            content=f"{int(unique_items)}",
            description=description_items_text,
            color='#009b4c',
            icon="bi bi-inbox"
        )
    st.write("")

    # Bar chart untuk Top 10 Barang
    top_products = filtered_df.groupby('DESCRIPTION_CLEANED')['QTY'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(8, 3))
    ax = sns.barplot(x=top_products.values, y=top_products.index, color='#abce19')
    ax.spines['top'].set_visible(False) 
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    for i, v in enumerate(top_products.values):
        ax.text(int(v), i, f'{int(v)}', color='black', va='center', fontsize=7)

    plt.gca().set_facecolor("#F0F2F6")  # Warna latar belakang area grafik
    plt.gcf().patch.set_facecolor("#F0F2F6") 
    plt.yticks(fontsize=8)
    plt.xticks([])
    plt.xlabel('')
    plt.ylabel('')
    plt.title("Top 10 Produk yang Laku Dibeli", fontsize=10)
    st.pyplot(plt.gcf())

    
