import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import streamlit_shadcn_ui as ui

def customers(df):
    df_unique = df.drop_duplicates(subset='NO.TRANSAKSI')
    df_unique['DATE'] = pd.to_datetime(df_unique['DATE'])
    df_unique['MONTH'] = df_unique['DATE'].dt.month_name()

    with st.expander("Filter Date"):
        cols = st.columns(2)
        with cols[0]:
            selected_month = st.selectbox("Select Month:", df_unique['MONTH'].unique())
        with cols[1]:
            selected_week = st.selectbox("Select week:", df_unique['MONTH'].unique())
        st.write(f"**Minggu ke-{selected_week} bulan {selected_month}**")        

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
        bars = plt.bar(transaction_per_day.index, transaction_per_day.values, color='#abce19')
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center', fontsize=12)

        plt.title(f'Aktivitas Pelanggan Hari-an', fontsize=14)
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
                colors=['#009b4c', '#abce19'])
        plt.title('Aktivitas Pelanggan: Weekend vs Weekday')
        st.pyplot(plt.gcf())