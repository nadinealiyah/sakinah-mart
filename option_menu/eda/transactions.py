import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from helper.custom_metric_card import metric_card

@st.cache_data
def get_transaction_calculations(df, start_date, end_date, days_selected):
    """Fungsi ini hanya melakukan semua perhitungan transaksi dan hasilnya di-cache."""
    df_unique = df.drop_duplicates(subset='NO TRANSAKSI').copy()
    df_unique['TANGGAL'] = pd.to_datetime(df_unique['TANGGAL'])

    # Filter data untuk rentang waktu yang dipilih
    filtered_df = df_unique[(df_unique['TANGGAL'] >= start_date) & (df_unique['TANGGAL'] <= end_date)]
    total_transactions = filtered_df['NO TRANSAKSI'].nunique()

    # Menentukan rentang waktu sebelumnya
    prev_start_date = start_date - pd.Timedelta(days=days_selected)
    prev_end_date = start_date - pd.Timedelta(days=1)
    prev_filtered_df = df_unique[(df_unique['TANGGAL'] >= prev_start_date) & (df_unique['TANGGAL'] <= prev_end_date)]

    # Mengecek apakah data tersedia untuk rentang sebelumnya
    day_text = "day" if days_selected == 1 else "days"
    if not prev_filtered_df.empty:
        total_transactions_prev = prev_filtered_df['NO TRANSAKSI'].nunique()
        total_transactions_diff = total_transactions - total_transactions_prev
        description_transactions = f"+{total_transactions_diff}" if total_transactions_diff > 0 else f"{total_transactions_diff}"
        description = f"{description_transactions} from the previous {days_selected} {day_text}."
    else:
        description = f"No previous data available for the selected range ({days_selected} {day_text})."

    # Aktivitas transaksi per hari
    filtered_df['DAY_OF_WEEK'] = filtered_df['TANGGAL'].dt.day_name()
    transaction_per_day = filtered_df.groupby('DAY_OF_WEEK')['NO TRANSAKSI'].count()
    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    transaction_per_day = transaction_per_day.reindex(ordered_days, fill_value=0)

    # Weekend vs weekday
    filtered_df['WEEKDAY'] = filtered_df['TANGGAL'].dt.weekday
    filtered_df['IS_WEEKEND'] = np.where(filtered_df['WEEKDAY'] >= 5, 'Weekend', 'Weekday')
    weekend_weekday_counts = filtered_df['IS_WEEKEND'].value_counts()
    
    return {
        "total_transactions": total_transactions,
        "description": description,
        "transaction_per_day": transaction_per_day,
        "weekend_weekday_counts": weekend_weekday_counts,
    }

def transactions(df, start_date, end_date, info_data):
    st.header("EDA - Transactions")
    
    placeholder = st.empty()
    cols = st.columns(3)
    with cols[0]:
        with st.expander("Filter"):
            dates_transactions = st.date_input(
                label="Select the date",
                value=(start_date, end_date),
                min_value=start_date,
                max_value=end_date,
                help=info_data
            )
            if len(dates_transactions) != 2:
                st.warning("Please select start and end dates.")
                st.stop()
            selected_start, selected_end = dates_transactions

    # Hitung jumlah hari yang dipilih
    days_selected = (selected_end - selected_start).days + 1
    day_text = "day" if days_selected == 1 else "days"
    placeholder.caption(f"Based on data from {selected_start} to {selected_end} ({days_selected} {day_text}).")
    calc_results = get_transaction_calculations(df, pd.to_datetime(selected_start), pd.to_datetime(selected_end), days_selected)

    cols = st.columns(3)
    with cols[0]:
        metric_card(
            title="Total Transaction:",
            icon="bi bi-people-fill",
            content=f"{calc_results['total_transactions']}",
            description=calc_results['description'],
            color='#05AF58'
        )
    st.write("")

    # Visualisasi hari-an 
    transaction_per_day = calc_results['transaction_per_day']
    cols = st.columns(2)
    with cols[0]:
        st.markdown(
            "<div style='text-align: center; font-weight: bold; font-size: 18px;'>Aktivitas Transaksi Hari-an</div>",
            unsafe_allow_html=True
        )
        plt.figure(figsize=(6, 5))
        bars = plt.bar(transaction_per_day.index, transaction_per_day.values, color='#abce19')
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), va='bottom', ha='center', fontsize=10)
        plt.gca().set_facecolor("#F0F2F6")
        plt.gcf().patch.set_facecolor("#F0F2F6") 
        plt.xticks(fontsize=8.5)
        plt.xlabel('Day', fontsize=12)
        plt.ylabel('Total Transactions', fontsize=12)
        plt.tight_layout()
        st.pyplot(plt.gcf())

    # Visualisasi weekend vs weekday 
    with cols[1]:
        st.markdown(
            "<div style='text-align: center; font-weight: bold; font-size: 18px;'>Aktivitas Transaksi: Weekend vs Weekday</div>",
            unsafe_allow_html=True
        )
        weekend_weekday_counts = calc_results['weekend_weekday_counts']
        if weekend_weekday_counts.empty:
            st.write("No data available for Weekend vs Weekday analysis.")
        else:
            def func(pct, allvals):
                absolute = int(np.round(pct / 100. * np.sum(allvals)))
                return f'{pct:.1f}%\n({absolute} Transaksi)'
            plt.figure(figsize=(5, 5))
            plt.pie(
                weekend_weekday_counts,
                labels=weekend_weekday_counts.index,
                autopct=lambda pct: func(pct, weekend_weekday_counts),
                startangle=180,
                colors=['#abce19', '#05AF58'],
                textprops={'fontsize': 10}
            )
            plt.gca().set_facecolor("#F0F2F6")
            plt.gcf().patch.set_facecolor("#F0F2F6") 
            plt.tight_layout()
            st.pyplot(plt.gcf())