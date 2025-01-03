import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import streamlit_shadcn_ui as ui

def customers(df, info_data):
    st.header("EDA - Customers")
    df_unique = df.drop_duplicates(subset='NO.TRANSAKSI')
    df_unique['DATE'] = pd.to_datetime(df_unique['DATE'])
    df_unique['MONTH'] = df_unique['DATE'].dt.month_name()
    df_unique['WEEK'] = (df_unique['DATE'].dt.day - 1) // 7 + 1

    placeholder = st.empty()

    cols = st.columns(2)
    with cols[0]:
        with st.expander("Filter Date"):
            st.caption(info_data)
            cols = st.columns(2)
            with cols[0]:
                selected_month = st.selectbox("Select Month:", df_unique['MONTH'].unique())
            with cols[1]:
                selected_week = st.number_input("Select Week:", min_value=df_unique['WEEK'].min(), max_value=df_unique['WEEK'].max())
    
    placeholder.caption(f"Based on data from Week {selected_week} of {selected_month}.")

    filtered_df = df_unique[(df_unique['MONTH'] == selected_month) & (df_unique['WEEK'] == selected_week)]
    total_customers = filtered_df['NO.TRANSAKSI'].nunique()

    # Ambil minggu sebelumnya
    if selected_month == 'January' and selected_week == 1:
        prev_week = None  # Tidak ada minggu sebelumnya untuk Januari minggu 1
    else:
        prev_week = selected_week - 1 if selected_week > 1 else 5  # Jika minggu 1, maka ambil minggu 5

    # Jika minggu sebelumnya ada, ambil data minggu sebelumnya
    if prev_week is not None:
        prev_week_data = df_unique[(df_unique['MONTH'] == selected_month) & (df_unique['WEEK'] == prev_week)]
        total_customers_prev_week = prev_week_data['NO.TRANSAKSI'].nunique()

        # Menghitung kenaikan atau penurunan
        total_customers_diff = total_customers - total_customers_prev_week
        description_customers = f"+{total_customers_diff}" if total_customers_diff > 0 else f"{total_customers_diff}"

        # Menampilkan metrik dan deskripsi
        cols = st.columns(3)
        with cols[0]:
            ui.metric_card(
                title="Total Customers:",
                content=f"{total_customers}",
                description=f"{description_customers} from last week")
    else:
        # Jika tidak ada minggu sebelumnya (misalnya Januari minggu 1)
        cols = st.columns(3)
        with cols[0]:
            ui.metric_card(
                title="Total Customers:",
                content=f"{total_customers}",
                description="No previous week data available")

    # Aktivitas pelanggan per hari
    filtered_df['DAY_OF_WEEK'] = filtered_df['DATE'].dt.day_name()
    transaction_per_day = filtered_df.groupby('DAY_OF_WEEK')['NO.TRANSAKSI'].count()
    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    transaction_per_day = transaction_per_day.reindex(ordered_days)

    cols = st.columns(2)
    # Visualisasi hari-an
    with cols[0]:
        st.markdown(
                    "<div style='text-align: center; font-weight: bold; font-size: 18px;'>Aktivitas Pelanggan Hari-an</div>", 
                    unsafe_allow_html=True
                    )
        if transaction_per_day.empty:
            # Jika data kosong, buat dummy data dengan nilai 0
            transaction_per_day = pd.Series(0, index=['No Data'])

        plt.figure(figsize=(6, 5))
        bars = plt.bar(transaction_per_day.index, transaction_per_day.values, color='#abce19')

        for bar in bars:
            yval = bar.get_height()
            if pd.notna(yval):
                plt.text(bar.get_x() + bar.get_width() / 2, yval, int(yval) if yval > 0 else 0, 
                        va='bottom', ha='center', fontsize=10)
        plt.xticks(fontsize=8.5)
        plt.xlabel('Day', fontsize=12)
        plt.ylabel('Total Transactions', fontsize=12)
        plt.tight_layout()
        st.pyplot(plt.gcf())

    # Visualisasi minggu-an
    with cols[1]:
        st.markdown(
                    "<div style='text-align: center; font-weight: bold; font-size: 18px;'>Aktivitas Pelanggan: Weekend vs Weekday</div>", 
                    unsafe_allow_html=True
                    )
        filtered_df['WEEKDAY'] = filtered_df['DATE'].dt.weekday
        filtered_df['IS_WEEKEND'] = np.where(filtered_df['WEEKDAY'] >= 5, 'Weekend', 'Weekday')
        weekend_weekday_counts = filtered_df['IS_WEEKEND'].value_counts()
        def func(pct, allvals):
            absolute = int(np.round(pct/100. * np.sum(allvals)))
            return f'{pct:.1f}%\n({absolute} Pelanggan)'

        plt.figure(figsize=(5, 5))
        plt.pie(weekend_weekday_counts, 
                labels=weekend_weekday_counts.index, 
                autopct=lambda pct: func(pct, weekend_weekday_counts),
                startangle=180, 
                colors=['#abce19', '#009b4c'],
                textprops={'fontsize': 10})
        plt.tight_layout()
        st.pyplot(plt.gcf())
