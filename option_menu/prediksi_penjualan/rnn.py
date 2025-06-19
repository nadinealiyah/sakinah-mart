# rnn.py (REVISI - FOKUS HANYA PADA CACHE)
import streamlit as st
import pandas as pd
import numpy as np
# import os
# import logging
import plotly.graph_objects as go
from datetime import timedelta
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error

DEFAULT_LOOK_BACK = 5
DEFAULT_LSTM_UNITS = 50
DEFAULT_EPOCHS = 200 
DEFAULT_BATCH_SIZE = 8
DEFAULT_RECURRENT_DROPOUT = 0.2
FORECAST_HORIZON_WEEKS = 4 

# Di dalam rnn.py

def get_all_items_from_apriori_rules(apriori_table_result):
    """
    Versi yang diperbaiki: Langsung memproses frozenset tanpa eval().
    """
    all_items = set()
    if apriori_table_result is not None and not apriori_table_result.empty:
        # Iterasi langsung melalui kolom yang berisi objek frozenset
        for item_set in apriori_table_result['antecedents']:
            all_items.update(item_set)
        for item_set in apriori_table_result['consequents']:
            all_items.update(item_set)
    return list(all_items)

# Fungsi ini dari kode asli Anda sudah benar menggunakan @st.cache_data
@st.cache_data(show_spinner=False)
def preprocess_data_for_time_series_model(df_original, items_from_apriori):
    # ... (Isi fungsi ini SAMA PERSIS seperti kode asli Anda) ...
    # ... saya tidak akan menempelkannya lagi agar tidak terlalu panjang, biarkan seperti aslinya ...
    df = df_original.copy()
    df.rename(columns={'ITEM DESCRIPTION': 'NAMA BARANG', 'QUANTITY': 'QTY'}, inplace=True)
    df['TANGGAL'] = pd.to_datetime(df['TANGGAL'])
    if not items_from_apriori:
        st.warning("Tidak ada item dari aturan Apriori. Menggunakan semua item unik dari data transaksi.")
        items_to_model = df['NAMA BARANG'].unique().tolist()
    else:
        items_to_model = [str(item) for item in items_from_apriori]
    df_filtered = df[df['NAMA BARANG'].isin(items_to_model)].copy()
    if df_filtered.empty:
        st.error("Tidak ada data yang cocok dengan item dari aturan Apriori.")
        return pd.DataFrame(), []
    df_grouped = df_filtered.groupby(['TANGGAL', 'NAMA BARANG'], as_index=False)['QTY'].sum()
    min_date, max_date = df_grouped['TANGGAL'].min(), df_grouped['TANGGAL'].max()
    tanggal_range = pd.date_range(start=min_date, end=max_date, freq='D')
    multi_index = pd.MultiIndex.from_product([tanggal_range, items_to_model], names=['TANGGAL', 'NAMA BARANG'])
    all_combinations = pd.DataFrame(index=multi_index).reset_index()
    df_joined = pd.merge(all_combinations, df_grouped, on=['TANGGAL', 'NAMA BARANG'], how='left')
    df_joined['QTY'] = df_joined['QTY'].fillna(0)
    df_joined = df_joined.sort_values('TANGGAL')
    start_date = df_joined['TANGGAL'].min()
    df_joined['WEEK_NUMBER'] = ((df_joined['TANGGAL'] - start_date).dt.days // 7) + 1
    df_weekly = df_joined.groupby(['WEEK_NUMBER', 'NAMA BARANG'], as_index=False)['QTY'].sum()
    df_weekly['TANGGAL'] = start_date + pd.to_timedelta((df_weekly['WEEK_NUMBER'] - 1) * 7, unit='D')
    df_weekly = df_weekly.sort_values(['TANGGAL', 'NAMA BARANG'])
    df_pivoted = df_weekly.pivot(index='TANGGAL', columns='NAMA BARANG', values='QTY').reset_index()
    product_columns_raw = [col for col in df_pivoted.columns if col != 'TANGGAL']
    product_df_raw = df_pivoted[product_columns_raw]
    zero_counts = (product_df_raw == 0).sum()
    filtered_items_by_zero_count = zero_counts[zero_counts <= 5].index.tolist()
    if not filtered_items_by_zero_count:
        st.warning("Tidak ada item yang memenuhi kriteria 'jumlah nol <= 5'. Menggunakan semua item unik.")
        final_product_columns = product_columns_raw
    else:
        df_filtered_by_zero_count = product_df_raw[filtered_items_by_zero_count]
        final_product_columns = df_filtered_by_zero_count.sum().sort_values(ascending=False).index.tolist()
    df_final = df_pivoted[["TANGGAL"] + final_product_columns].copy()
    df_final['TANGGAL'] = pd.to_datetime(df_final['TANGGAL'])
    for col in final_product_columns:
        df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0).apply(lambda x: max(0, x))
    return df_final, final_product_columns

def calculate_metrics(y_true, y_pred):
    # ... (Isi fungsi ini SAMA PERSIS seperti kode asli Anda) ...
    mae = mean_absolute_error(y_true, y_pred)
    non_zero_indices = y_true != 0
    mape = np.mean(np.abs((y_true[non_zero_indices] - y_pred[non_zero_indices]) / y_true[non_zero_indices])) * 100 if np.sum(non_zero_indices) > 0 else np.nan
    return mae, mape

def create_sequences(data, look_back):
    # ... (Isi fungsi ini SAMA PERSIS seperti kode asli Anda) ...
    X, y = [], []
    for i in range(len(data) - look_back):
        X.append(data[i:(i + look_back), 0])
        y.append(data[i + look_back, 0])
    return np.array(X), np.array(y)


# <<< PERUBAHAN UTAMA: @st.cache_resource menjadi @st.cache_data >>>
@st.cache_data(show_spinner=False)
def train_and_forecast_rnn_for_item(df_final_preprocessed, selected_item, look_back=DEFAULT_LOOK_BACK, lstm_units=DEFAULT_LSTM_UNITS, epochs=DEFAULT_EPOCHS, batch_size=DEFAULT_BATCH_SIZE, recurrent_dropout=DEFAULT_RECURRENT_DROPOUT, forecast_horizon=FORECAST_HORIZON_WEEKS):
    # ... (Isi fungsi ini SAMA PERSIS seperti kode asli Anda, tidak ada yang berubah) ...
    tf.keras.backend.clear_session()
    if df_final_preprocessed.empty or selected_item not in df_final_preprocessed.columns:
        return pd.DataFrame(), pd.DataFrame(), {'MAE': np.nan, 'MAPE': np.nan}
    product_series = df_final_preprocessed[selected_item].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(product_series)
    train_size = int(len(df_final_preprocessed) * 0.8)
    if len(scaled_data) <= look_back + 1:
        return pd.DataFrame(), pd.DataFrame(), {'MAE': np.nan, 'MAPE': np.nan}
    train_scaled = scaled_data[:train_size]
    test_scaled_with_history = scaled_data[train_size - look_back:]
    if len(train_scaled) <= look_back or len(test_scaled_with_history) <= look_back:
        return pd.DataFrame(), pd.DataFrame(), {'MAE': np.nan, 'MAPE': np.nan}
    X_train, y_train = create_sequences(train_scaled, look_back)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test, y_test_actual_scaled = create_sequences(test_scaled_with_history, look_back)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    model = Sequential([LSTM(lstm_units, recurrent_dropout=recurrent_dropout, input_shape=(look_back, 1)), Dense(1)])
    model.compile(optimizer='adam', loss='mse')
    early_stopping = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=0)
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0, validation_split=0.1, callbacks=[early_stopping])
    y_pred_scaled = model.predict(X_test, verbose=0)
    y_pred_unscaled = scaler.inverse_transform(y_pred_scaled)
    y_test_actual_unscaled = scaler.inverse_transform(y_test_actual_scaled.reshape(-1, 1))
    y_pred_unscaled[y_pred_unscaled < 0] = 0
    mae, mape = calculate_metrics(y_test_actual_unscaled.flatten(), y_pred_unscaled.flatten())
    metrics_result = {'MAE': mae, 'MAPE': mape}
    plot_df = df_final_preprocessed[['TANGGAL', selected_item]].rename(columns={selected_item: 'Actual Sales'})
    current_input = scaled_data[-look_back:].reshape(1, look_back, 1)
    product_future_forecast_scaled = []
    for _ in range(forecast_horizon):
        predicted_scaled = model.predict(current_input, verbose=0)[0, 0]
        product_future_forecast_scaled.append(predicted_scaled)
        current_input = np.concatenate((current_input[:, 1:, :], np.array([[[predicted_scaled]]])), axis=1)
    product_future_forecast_unscaled = scaler.inverse_transform(np.array(product_future_forecast_scaled).reshape(-1, 1))
    product_future_forecast_unscaled[product_future_forecast_unscaled < 0] = 0
    product_future_forecast_unscaled = np.round(product_future_forecast_unscaled).astype(int)
    df_future_forecast = pd.DataFrame({'Tanggal': [df_final_preprocessed['TANGGAL'].max() + timedelta(weeks=i+1) for i in range(forecast_horizon)], 'Prediksi Penjualan': product_future_forecast_unscaled.flatten()})
    return plot_df, df_future_forecast, metrics_result

def visualize_rnn_forecast(plot_df, df_future_forecast, selected_item, metrics):
    # ... (Isi fungsi ini SAMA PERSIS seperti kode asli Anda) ...
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_df['TANGGAL'], y=plot_df['Actual Sales'], mode='lines',name='Penjualan Asli', line=dict(color='#004e26'), hovertemplate='<b>%{x|%d %b %Y}</b><br>Penjualan: %{y} pcs<extra></extra>'))
    if not df_future_forecast.empty:
        pred_col_name = 'Prediksi Penjualan'
        fig.add_trace(go.Scatter(x=df_future_forecast['Tanggal'],y=df_future_forecast[pred_col_name],mode='lines+markers',name='Prediksi',line=dict(color='red'),hovertemplate='<b>%{x|%d %b %Y}</b><br>Prediksi: %{y} pcs<extra></extra>'))
    if not plot_df.empty:
        last_actual_date = plot_df['TANGGAL'].max()
        fig.add_vline(x=last_actual_date, line_width=2, line_dash="dot", line_color="black")
    mape_text = f"MAPE: {metrics['MAPE']:.2f}%" if not pd.isna(metrics['MAPE']) else "MAPE: N/A"
    title_text = f'Tren Penjualan Minggu-an & Prediksi 4 Minggu ke depan untuk {selected_item}<br><sup>MAE: {metrics["MAE"]:.2f} | {mape_text}</sup>'
    fig.update_layout(title={'text': title_text,'y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top','font': {'size': 20}}, xaxis_title='Bulan', yaxis_title='Jumlah Penjualan (Pcs)', hovermode='closest', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=500)
    return fig


def show_rnn_prediction_page(df_full, apriori_table_result=None):
    # ... (Isi fungsi ini SAMA PERSIS seperti kode asli Anda, tidak ada yang berubah) ...
    st.header("Tren dan Prediksi Penjualan")
    if not df_full.empty:
        df_full['TANGGAL'] = pd.to_datetime(df_full['TANGGAL'])
        start_date = df_full['TANGGAL'].min().strftime('%Y-%m-%d')
        end_date = df_full['TANGGAL'].max().strftime('%Y-%m-%d')
        total_days = (df_full['TANGGAL'].max() - df_full['TANGGAL'].min()).days + 1
        day_text = "day" if total_days == 1 else "days"
        st.caption(f"Based on data from {start_date} to {end_date} ({total_days} {day_text}).")
    items_from_apriori = get_all_items_from_apriori_rules(apriori_table_result)
    df_final_preprocessed, product_columns_to_model = preprocess_data_for_time_series_model(df_full, items_from_apriori)
    if df_final_preprocessed.empty or not product_columns_to_model:
        st.warning("Tidak dapat melanjutkan prediksi karena data tidak tersedia atau tidak ada item yang memenuhi kriteria pemodelan.")
        return
    selected_item = st.selectbox("Pilih Item yang ingin diprediksi:",options=product_columns_to_model,index=0)
    if selected_item:
        with st.spinner(f"Memproses data dengan model RNN untuk '{selected_item}'. Ini mungkin memakan waktu sebentar."):
            try:
                plot_df, next_week_forecast, metrics = train_and_forecast_rnn_for_item(df_final_preprocessed, selected_item, look_back=DEFAULT_LOOK_BACK, lstm_units=DEFAULT_LSTM_UNITS, epochs=DEFAULT_EPOCHS, batch_size=DEFAULT_BATCH_SIZE, recurrent_dropout=DEFAULT_RECURRENT_DROPOUT, forecast_horizon=FORECAST_HORIZON_WEEKS)
                if plot_df.empty:
                    st.warning("Tidak cukup data untuk memprediksi dengan model RNN.")
                    return
                fig = visualize_rnn_forecast(plot_df, next_week_forecast, selected_item, metrics)
                with st.container(border=True):
                    st.plotly_chart(fig, use_container_width=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div style='font-weight: bold; font-size: 18px;'>Tabel Prediksi Penjualan</div>", unsafe_allow_html=True)
                if not next_week_forecast.empty:
                    df_display = next_week_forecast.copy()
                    df_display['Tanggal'] = df_display['Tanggal'].dt.strftime('%d-%m-%Y')
                    df_display['Prediksi Penjualan'] = df_display['Prediksi Penjualan'].apply(lambda x: f"{x} pcs")
                    st.dataframe(df_display.set_index('Tanggal'))
                else:
                    st.info("Tidak ada prediksi masa depan yang dapat ditampilkan.")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses prediksi RNN untuk '{selected_item}':")
                st.exception(e)
    else:
        st.info("Silakan pilih item dari dropdown untuk memulai prediksi.")