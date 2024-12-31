import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_antd_components as sac
import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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
    cols = st.columns(2)
    with cols[0]:
        st.header("HOME")
        st.markdown("**Project ini menampilkan analisis data\n dari hasil penjualan Sakinah Mart pada tahun 2023.**")
        st.markdown(
                        """
                        <a href="https://sakinahmart.com/" target="_blank">
                            <button style="background-color:#009b4c; color:white; border:none; padding:10px 20px; text-align:center; text-decoration:none; font-size:14px; border-radius:20px; cursor:pointer;">
                                Sakinah Mart Website
                            </button>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )
        
    with cols[1]:
        st.image("sakinah-mart.png")

    st.markdown("""<div style="text-align: justify;">
    Sakinah Mart adalah ritel modern berbasis syariah dengan 20 cabang di Jawa Timur, 
    yang bertujuan memberikan manfaat bagi masyarakat melalui produk berkualitas dengan harga terjangkau. 
    Namun, data transaksi yang melimpah seperti waktu pembelian, produk yang dibeli, dan frekuensi pembelian belum diolah secara optimal, 
    sehingga berisiko menimbulkan waste of inventory.
    Untuk mengatasi hal ini dan tetap bersaing di pasar, project kali ini menggunakan algoritma Apriori untuk mengidentifikasi pola pembelian konsumen, seperti product bundling dan penataan letak barang, 
    serta metode Vector Autoregressive (VAR) untuk memprediksi kebutuhan pelanggan dan mengelola persediaan secara efisien. Kombinasi kedua metode ini diharapkan dapat mengoptimalkan strategi penjualan, meningkatkan efisiensi operasional, dan menjaga kepuasan pelanggan.
    </div>""", unsafe_allow_html=True)

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
        df_unique = df.drop_duplicates(subset='NO.TRANSAKSI')
        df_unique['DATE'] = pd.to_datetime(df_unique['DATE'])
        df_unique['MONTH'] = df_unique['DATE'].dt.month_name()
        selected_month = st.selectbox("Pilih Bulan:", df_unique['MONTH'].unique())
        filtered_df = df_unique[df_unique['MONTH'] == selected_month]

        total_customers = filtered_df['NO.TRANSAKSI'].nunique()
        cols = st.columns(3)
        with cols[0]:
            ui.metric_card(
                title="Total Customers:",
                content=f"{total_customers}")
        filtered_df['DAY_OF_WEEK'] = filtered_df['DATE'].dt.day_name()
        transaction_per_day = filtered_df.groupby('DAY_OF_WEEK')['NO.TRANSAKSI'].count()
        ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        transaction_per_day = transaction_per_day.reindex(ordered_days)

        cols = st.columns(2)
        with cols[0]:
            plt.figure(figsize=(6, 6))
            bars = plt.bar(transaction_per_day.index, transaction_per_day.values, color='skyblue')
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center', fontsize=12)

            plt.title(f'Jumlah Transaksi Per Hari di Bulan {selected_month} (Senin - Minggu)', fontsize=14)
            plt.xlabel('Hari', fontsize=12)
            plt.ylabel('Jumlah Transaksi', fontsize=12)
            plt.tight_layout()
            st.pyplot(plt.gcf())

        with cols[1]:
            filtered_df['WEEKDAY'] = filtered_df['DATE'].dt.weekday
            filtered_df['IS_WEEKEND'] = np.where(filtered_df['WEEKDAY'] >= 5, 'Weekend', 'Weekday')
            weekend_weekday_counts = filtered_df['IS_WEEKEND'].value_counts()
            def func(pct, allvals):
                absolute = int(np.round(pct/100. * np.sum(allvals)))
                return f'{pct:.1f}%\n({absolute} Pelanggan)'

            plt.figure(figsize=(6, 6))
            plt.pie(weekend_weekday_counts, 
                    labels=weekend_weekday_counts.index, 
                    autopct=lambda pct: func(pct, weekend_weekday_counts),
                    startangle=90, 
                    colors=['#ff9999', '#66b3ff'])
            plt.title('Aktivitas Pelanggan: Weekend vs Weekday')
            st.pyplot(plt.gcf())

    elif button == "Items":
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