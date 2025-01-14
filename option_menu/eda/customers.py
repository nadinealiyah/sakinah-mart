import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from helper.custom_metric_card import metric_card

def customers(df, start_date, end_date, info_data):
    plt.style.use("default")

    st.header("EDA - Customers")
    df_unique = df.drop_duplicates(subset='NO.TRANSAKSI')
    df_unique['DATE'] = pd.to_datetime(df_unique['DATE'])

    placeholder = st.empty()

    # Filter
    cols = st.columns(3)
    with cols[0]:
        with st.expander("Filter"):
            dates = st.date_input(
                label="Select the date",
                value=(),
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
    if prev_start_date < df_unique['DATE'].min() or prev_end_date < df_unique['DATE'].min():
        prev_filtered_df = pd.DataFrame()  # Rentang sebelumnya di luar data
    else:
        # Filter data untuk rentang waktu sebelumnya
        prev_filtered_df = df_unique[(df_unique['DATE'] >= prev_start_date) & (df_unique['DATE'] <= prev_end_date)]

    # Filter data untuk rentang waktu yang dipilih
    filtered_df = df_unique[(df_unique['DATE'] >= start_date) & (df_unique['DATE'] <= end_date)]
    total_customers = filtered_df['NO.TRANSAKSI'].nunique()

    # Mengecek apakah data tersedia untuk rentang sebelumnya
    if not prev_filtered_df.empty:
        total_customers_prev = prev_filtered_df['NO.TRANSAKSI'].nunique()
        total_customers_diff = total_customers - total_customers_prev
        description_customers = f"+{total_customers_diff}" if total_customers_diff > 0 else f"{total_customers_diff}"
        description = f"{description_customers} from the previous {days_selected} {day_text}."
    else:
        total_customers_prev = 0
        description = f"No previous data available for the selected range ({days_selected} {day_text})."

    # Metric Card
    cols = st.columns(3)
    with cols[0]:
        metric_card(
            title="Total Customers:",
            icon="bi bi-people-fill",
            content=f"{total_customers}",
            description=description,
            color='#009b4c'
        )
    st.write("")

    # Aktivitas pelanggan per hari
    filtered_df['DAY_OF_WEEK'] = filtered_df['DATE'].dt.day_name()
    transaction_per_day = filtered_df.groupby('DAY_OF_WEEK')['NO.TRANSAKSI'].count()
    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    transaction_per_day = transaction_per_day.reindex(ordered_days, fill_value=0)

    cols = st.columns(2)
    # Visualisasi hari-an
    with cols[0]:
        st.markdown(
            "<div style='text-align: center; font-weight: bold; font-size: 18px;'>Aktivitas Pelanggan Hari-an</div>",
            unsafe_allow_html=True
        )
        plt.figure(figsize=(6, 5))
        bars = plt.bar(transaction_per_day.index, transaction_per_day.values, color='#abce19')

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), va='bottom', ha='center', fontsize=10)

        plt.gca().set_facecolor("#F0F2F6")  # Warna latar belakang area grafik
        plt.gcf().patch.set_facecolor("#F0F2F6") 
        plt.xticks(fontsize=8.5)
        plt.xlabel('Day', fontsize=12)
        plt.ylabel('Total Transactions', fontsize=12)
        plt.tight_layout()
        st.pyplot(plt.gcf())

    # Visualisasi weekend vs weekday
    with cols[1]:
        st.markdown(
            "<div style='text-align: center; font-weight: bold; font-size: 18px;'>Aktivitas Pelanggan: Weekend vs Weekday</div>",
            unsafe_allow_html=True
        )
        filtered_df['WEEKDAY'] = filtered_df['DATE'].dt.weekday
        filtered_df['IS_WEEKEND'] = np.where(filtered_df['WEEKDAY'] >= 5, 'Weekend', 'Weekday')
        weekend_weekday_counts = filtered_df['IS_WEEKEND'].value_counts()

        if weekend_weekday_counts.empty:
            st.write("No data available for Weekend vs Weekday analysis.")
        else:
            def func(pct, allvals):
                absolute = int(np.round(pct / 100. * np.sum(allvals)))
                return f'{pct:.1f}%\n({absolute} Pelanggan)'

            plt.figure(figsize=(5, 5))
            plt.pie(
                weekend_weekday_counts,
                labels=weekend_weekday_counts.index,
                autopct=lambda pct: func(pct, weekend_weekday_counts),
                startangle=180,
                colors=['#abce19', '#009b4c'],
                textprops={'fontsize': 10}
            )
            
            plt.gca().set_facecolor("#F0F2F6")  # Warna latar belakang area grafik
            plt.gcf().patch.set_facecolor("#F0F2F6") 
            plt.tight_layout()
            st.pyplot(plt.gcf())