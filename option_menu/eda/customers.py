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

    placeholder = st.empty()

    cols = st.columns(2)
    with cols[0]:
        with st.expander("Filter Date"):
            st.caption(info_data)
            cols = st.columns(2)
            with cols[0]:
                selected_month = st.selectbox("Select Month:", df_unique['MONTH'].unique())
            with cols[1]:
                selected_week = st.selectbox("Select Week:", df_unique['MONTH'].unique())
    
    placeholder.caption(f"Based on data from Week {selected_week} of {selected_month}.")

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
            plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center', fontsize=10)

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