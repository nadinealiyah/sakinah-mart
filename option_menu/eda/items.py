# eda/items.py (REVISI - FOKUS HANYA PADA CACHE)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from helper.custom_metric_card import metric_card
import streamlit_toggle as tog

# <<< FUNGSI BARU UNTUK KALKULASI YANG DI-CACHE >>>
@st.cache_data
def get_item_calculations(df, start_date, end_date, days_selected):
    """Fungsi ini hanya melakukan semua perhitungan dan hasilnya di-cache."""
    
    # Filter data untuk rentang waktu yang dipilih
    filtered_df = df[(df['TANGGAL'] >= start_date) & (df['TANGGAL'] <= end_date)]

    # Menentukan rentang waktu sebelumnya
    prev_start_date = start_date - pd.Timedelta(days=days_selected)
    prev_end_date = start_date - pd.Timedelta(days=1) # Revisi kecil di sini untuk perbandingan yang lebih akurat
    
    prev_filtered_df = df[(df['TANGGAL'] >= prev_start_date) & (df['TANGGAL'] <= prev_end_date)]

    # Menghitung total dan jenis barang
    total_qty = filtered_df["QTY"].sum()
    unique_items = filtered_df["NAMA BARANG"].nunique()

    # Mengecek apakah data tersedia untuk rentang sebelumnya
    day_text = "day" if days_selected == 1 else "days"
    if not prev_filtered_df.empty:
        total_qty_prev = prev_filtered_df["QTY"].sum()
        unique_items_prev = prev_filtered_df["NAMA BARANG"].nunique()
        total_qty_diff = int(total_qty - total_qty_prev)
        unique_items_diff = int(unique_items - unique_items_prev)
        description_qty = f"+{total_qty_diff}" if total_qty_diff > 0 else f"{total_qty_diff}"
        description_items = f"+{unique_items_diff}" if unique_items_diff > 0 else f"{unique_items_diff}"
        description_qty_text = f"{description_qty} from the previous {days_selected} {day_text}."
        description_items_text = f"{description_items} from the previous {days_selected} {day_text}."
    else:
        description_qty_text = f"No previous data available for the selected range ({days_selected} {day_text})."
        description_items_text = f"No previous data available for the selected range ({days_selected} {day_text})."

    # Perhitungan produk terlaris dan tidak laku
    filtered_products = filtered_df.groupby("NAMA BARANG")["QTY"].sum()
    least_products = filtered_products[filtered_products == 1].sort_values()
    top_products = filtered_products.sort_values(ascending=False).head(10)

    # Mengembalikan semua hasil kalkulasi dalam satu paket (dictionary)
    return {
        "total_qty": total_qty,
        "unique_items": unique_items,
        "description_qty_text": description_qty_text,
        "description_items_text": description_items_text,
        "least_products": least_products,
        "top_products": top_products,
    }

# <<< FUNGSI ASLI ANDA, DIMODIFIKASI SEDIKIT UNTUK MENGGUNAKAN CACHE >>>
def items(df, start_date, end_date, info_data):
    # Semua kode tampilan ini 100% milik Anda
    st.header("EDA - Items")
    df['TANGGAL'] = pd.to_datetime(df['TANGGAL'])

    placeholder = st.empty()

    # Filter (Tampilan asli Anda)
    cols = st.columns(3)
    with cols[0]:
        with st.expander("Filter"):
            dates_items = st.date_input(
                label="Select the date",
                value=(start_date, end_date),
                min_value=start_date,
                max_value=end_date,
                help=info_data
            )
            if len(dates_items) != 2:
                st.warning("Please select start and end dates.")
                st.stop()
            
            # Ambil tanggal dari input
            selected_start, selected_end = dates_items

    # Hitung jumlah hari yang dipilih
    days_selected = (selected_end - selected_start).days + 1
    day_text = "day" if days_selected == 1 else "days"
    placeholder.caption(f"Based on data from {selected_start} to {selected_end} ({days_selected} {day_text}).")

    # <<< PANGGIL FUNGSI YANG DI-CACHE UNTUK MENDAPATKAN SEMUA HASIL PERHITUNGAN >>>
    # Ini akan berjalan cepat setelah pertama kali
    calc_results = get_item_calculations(df, pd.to_datetime(selected_start), pd.to_datetime(selected_end), days_selected)

    # Metric Card (Tampilan asli Anda, menggunakan hasil dari cache)
    cols = st.columns(3)
    with cols[0]:
        metric_card(
            title="Total Barang yang Dibeli:",
            content=f"{int(calc_results['total_qty'])}",
            description=calc_results['description_qty_text'],
            color='#05AF58',
            icon="bi bi-inboxes"
        )
    with cols[1]:
        metric_card(
            title="Jenis Barang yang Dibeli:",
            content=f"{int(calc_results['unique_items'])}",
            description=calc_results['description_items_text'],
            color='#05AF58',
            icon="bi bi-inbox"
        )
    st.write("")

    # Toggle switch (Tampilan dan logika asli Anda)
    platform_toggle = st.session_state.get("product_toggle", False)
    product_toggle = tog.st_toggle_switch(
        label="Least" if platform_toggle else "Top",
        key="product_toggle",
        default_value=False,
        label_after=False,
        inactive_color='#D3D3D3',
        active_color="#009452",
        track_color="#05AF58"
    )

    # Menentukan produk berdasarkan toggle (Menggunakan hasil dari cache)
    if product_toggle:
        least_products = calc_results['least_products']
        st.markdown(
            "<div style='text-align: center; font-weight: bold; font-size: 18px;'>Produk yang Tidak Laku Dibeli</div>",
            unsafe_allow_html=True
        )
        styled_df = (
            least_products
            .reset_index()
            .rename(columns={"QTY": "Jumlah Dibeli"})
            .style.set_properties(**{'text-align': 'center'})
            .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
        )
        st.dataframe(styled_df, use_container_width=True)
    else:
        top_products = calc_results['top_products']
        st.markdown(
            "<div style='text-align: center; font-weight: bold; font-size: 18px;'>10 Produk yang Laku Dibeli</div>",
            unsafe_allow_html=True
        )
        # Membuat bar chart (Kode plotting asli Anda)
        plt.figure(figsize=(8, 3))
        ax = sns.barplot(x=top_products.values, y=top_products.index, color="#abce19")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        for i, v in enumerate(top_products.values):
            if v > 0:
                ax.text(int(v), i, f"{int(v)}", color="black", va="center", fontsize=7)
        plt.gca().set_facecolor("#F0F2F6")
        plt.gcf().patch.set_facecolor("#F0F2F6")
        plt.yticks(fontsize=8)
        plt.xticks([])
        plt.xlabel("")
        plt.ylabel("")
        st.pyplot(plt.gcf())