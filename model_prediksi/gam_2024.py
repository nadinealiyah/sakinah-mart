# -*- coding: utf-8 -*-
"""gam_2024.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IdD6i7g9aaZcsXxxirFYZtOBzVUzi9sa

### **Import Library**
"""

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from pygam import LinearGAM, s
import logging
import plotly.express as px
import matplotlib.pyplot as plt
# Matikan logger pygam agar output tidak terlalu banyak
logging.getLogger('pygam').setLevel(logging.WARNING)

"""### **Import Data Hasil Rules**"""

df = pd.read_csv('data/rules2024.csv')
df.head()

# Pastikan semua elemen dalam kolom antecedents dan consequents adalah frozenset
df["antecedents"] = df["antecedents"].apply(lambda x: frozenset(eval(x)) if isinstance(x, str) else x)
df["consequents"] = df["consequents"].apply(lambda x: frozenset(eval(x)) if isinstance(x, str) else x)

# Mengambil semua item unik
all_items = set()
for col in ["antecedents", "consequents"]:
    for items in df[col]:
        all_items.update(items)

all_items

"""### **Import Data Transaksi**"""

groceries = pd.read_excel('data/final_data2024.xlsx')
groceries

"""### **Filter Data Transaksi**"""

df_filtered = groceries[groceries['NAMA BARANG'].isin(all_items)]
df_filtered

# Menampilkan jumlah unik nama barang
jumlah_nama_barang = df_filtered['NAMA BARANG'].nunique()
print("Jumlah nama barang unik:", jumlah_nama_barang)

# Menampilkan isi nama barang yang unik
nama_barang_unik = df_filtered['NAMA BARANG'].unique()
print("Nama barang unik:")
for nama in nama_barang_unik:
    print("-", nama)

"""### **Agregasi Data Mingguan**"""

# Agregasi jumlah QTY per tanggal dan nama barang
df_grouped = df_filtered.groupby(['TANGGAL', 'NAMA BARANG'], as_index=False)['QTY'].sum()

tanggal_range = pd.date_range(start='2024-01-01', end='2024-12-31')
all_items = df_filtered['NAMA BARANG'].unique()

# Buat kombinasi semua tanggal dan item
multi_index = pd.MultiIndex.from_product([tanggal_range, all_items], names=['TANGGAL', 'NAMA BARANG'])
all_combinations = pd.DataFrame(index=multi_index).reset_index()

# Gabungkan dengan hasil groupby
df_joined = pd.merge(all_combinations, df_grouped, on=['TANGGAL', 'NAMA BARANG'], how='left')
df_joined['QTY'] = df_joined['QTY'].fillna(0)

# Pastikan TANGGAL dalam datetime
df_joined['TANGGAL'] = pd.to_datetime(df_joined['TANGGAL'])

# Urutkan dulu datanya
df_joined = df_joined.sort_values('TANGGAL')

# Ambil tanggal paling awal
start_date = df_joined['TANGGAL'].min()

# Hitung minggu ke-n secara manual (tiap 7 hari)
df_joined['WEEK_NUMBER'] = ((df_joined['TANGGAL'] - start_date).dt.days // 7) + 1

# Agregasi berdasarkan minggu dan nama barang
df_weekly = df_joined.groupby(['WEEK_NUMBER', 'NAMA BARANG'], as_index=False)['QTY'].sum()

# (Opsional) Tambahkan kolom tanggal mulai minggu
df_weekly['TANGGAL'] = start_date + pd.to_timedelta((df_weekly['WEEK_NUMBER'] - 1) * 7, unit='D')

# Visualisasi
fig = px.line(df_weekly, x='TANGGAL', y='QTY', color='NAMA BARANG',
              title='Jumlah Penjualan per Minggu (Setiap 7 Hari)')
fig.update_layout(legend_title_text='Klik untuk tampilkan/sembunyikan item')
fig.show()

df_weekly

"""### **Pivot Data**"""

df_pivoted= df_weekly.pivot(index='TANGGAL', columns='NAMA BARANG', values='QTY')
df_pivoted.columns.name = None  # hilangkan nama kolom atas
df_pivoted = df_pivoted.reset_index()
df_pivoted.head()

# 1. Pisahkan kolom tanggal dan kolom produk
produk_df = df_pivoted.drop(columns=["TANGGAL"])

# 2. Hitung jumlah 0 per kolom
zero_counts = (produk_df == 0).sum()

# 3. Ambil item yang jumlah 0-nya <= 5
filtered_items = zero_counts[zero_counts <= 5].index

# 4. Filter dataframe hanya dengan item yang lolos kriteria 0
filtered_df = produk_df[filtered_items]

# 5. Hitung total penjualan per item
total_sales = filtered_df.sum().sort_values(ascending=False).index

# 6. Ambil 15 item dengan total penjualan tertinggi
# top_3_items = total_sales.head(15).index

# 7. Final dataframe dengan 15 item terbaik
df_final = df_pivoted[["TANGGAL"] + total_sales.tolist()]

df_final.head()

df_final.info()

# Ubah kolom TANGGAL menjadi datetime
df_final["TANGGAL"] = pd.to_datetime(df_final["TANGGAL"])

# Ubah dari wide ke long format agar cocok untuk plotly express
df_long = df_final.melt(id_vars="TANGGAL", var_name="NAMA BARANG", value_name="QTY")

# Buat line chart
fig = px.line(
    df_long,
    x="TANGGAL",
    y="QTY",
    color="NAMA BARANG",
    title="Jumlah Penjualan per Minggu per Item",
    markers=True,
    labels={"TANGGAL": "Tanggal", "QTY": "Jumlah Terjual", "NAMA BARANG": "Nama Produk"},
    hover_data={"TANGGAL": True, "QTY": True, "NAMA BARANG": True}
)

# Layout tambahan
fig.update_layout(
    legend_title_text='Klik nama produk untuk tampilkan/sembunyikan',
    xaxis_title='Tanggal',
    yaxis_title='Jumlah Terjual',
    template='plotly_white',
    height=500,
    width=900
)

fig.show()

df_final.info()

# Mengubah kolom TANGGAL menjadi datetime dan menjadikannya index
df_final['TANGGAL'] = pd.to_datetime(df_final['TANGGAL'])
df_final= df_final.set_index('TANGGAL')
df_final = df_final.asfreq('W-MON') # Menetapkan frekuensi mingguan (Senin)

df_final.head()

# --- Pra-Pemrosesan Data ---
# 1. Mengubah index 'TANGGAL' menjadi kolom biasa (jika TANGGAL adalah index)
if df_final.index.name == 'TANGGAL':
    df_final = df_final.reset_index()
    df_final.rename(columns={'index': 'TANGGAL'}, inplace=True)
elif 'TANGGAL' not in df_final.columns:
    df_final = df_final.reset_index()
    df_final.rename(columns={df_final.columns[0]: 'TANGGAL'}, inplace=True)

# 2. Pastikan kolom 'TANGGAL' adalah tipe datetime
df_final['TANGGAL'] = pd.to_datetime(df_final['TANGGAL'])

# 3. Identifikasi kolom produk
product_columns = [col for col in df_final.columns if col != 'TANGGAL']

# 4. Pastikan kolom produk adalah numerik dan tangani nilai yang tidak bisa diubah
for col in product_columns:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce')
    df_final[col] = df_final[col].fillna(0)
    df_final[col] = np.maximum(0, df_final[col]) # Pastikan tidak negatif

# --- Fungsi Evaluasi ---
def evaluate_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-8))) * 100
    return mae, rmse, mape

# --- Hyperparameter ---
LOOK_BACK_OPTIONS = [1, 2, 3]
LAMBDAS = [0.1, 1.0, 10]
FORECAST_HORIZON = 4
SPLITS = 3

# --- Preprocessing ---
if df_final.index.name == 'TANGGAL':
    df_final = df_final.reset_index()
df_final['TANGGAL'] = pd.to_datetime(df_final['TANGGAL'])
product_columns = [col for col in df_final.columns if col != 'TANGGAL']

for col in product_columns:
    df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
    df_final[col] = np.maximum(0, df_final[col])

# --- Inisialisasi Output ---
best_models = {}
evaluation_summary = {}
future_forecasts_df_list = []

print("="*80)
print("                    GAM-VAR FORECASTING with GRID SEARCH")
print("="*80)

# --- Per Produk ---
for product in product_columns:
    print(f"\n⏳ Memproses Produk: {product}")
    best_score = float("inf")
    best_result = {}

    for LOOK_BACK in LOOK_BACK_OPTIONS:
        df_feat = df_final.copy()
        for col in product_columns:
            for lag in range(1, LOOK_BACK+1):
                df_feat[f'{col}_lag{lag}'] = df_feat[col].shift(lag)
        df_feat.dropna(inplace=True)
        X_cols = [col for col in df_feat.columns if '_lag' in col]
        X_all = df_feat[X_cols].values
        y_all = df_feat[product].values
        tscv = TimeSeriesSplit(n_splits=SPLITS)

        for lam_val in LAMBDAS:
            fold_maes, fold_rmses, fold_mapes = [], [], []
            for train_index, test_index in tscv.split(X_all):
                X_train, X_test = X_all[train_index], X_all[test_index]
                y_train, y_test = y_all[train_index], y_all[test_index]

                formula = s(0)
                for i in range(1, X_train.shape[1]):
                    formula += s(i)
                gam = LinearGAM(formula).fit(X_train, y_train)
                gam.lam = lam_val
                y_pred = gam.predict(X_test)
                y_pred = np.maximum(0, y_pred)
                mae, rmse, mape = evaluate_metrics(y_test, y_pred)
                fold_maes.append(mae)
                fold_rmses.append(rmse)
                fold_mapes.append(mape)

            avg_mae = np.mean(fold_maes)
            if avg_mae < best_score:
                best_score = avg_mae
                best_result = {
                    'LOOK_BACK': LOOK_BACK,
                    'lam': lam_val,
                    'features': df_feat,
                    'X_cols': X_cols,
                    'gam': gam,
                    'avg_mae': avg_mae,
                    'avg_rmse': np.mean(fold_rmses),
                    'avg_mape': np.mean(fold_mapes)
                }

    # --- Forecast ke Depan ---
    df_used = best_result['features']
    X_all = df_used[best_result['X_cols']]
    y_all = df_used[product]
    train_size = int(0.8 * len(df_used))
    formula_final = s(0)
    for i in range(1, X_all.shape[1]):
        formula_final += s(i)
    gam_final = LinearGAM(formula_final, lam=best_result['lam']).fit(X_all[:train_size].values, y_all[:train_size].values)

    y_pred_test = gam_final.predict(X_all[train_size:].values)
    y_pred_test = np.maximum(0, y_pred_test)
    y_test_actual = y_all[train_size:]
    mae, rmse, mape = evaluate_metrics(y_test_actual.values, y_pred_test)

    best_models[product] = gam_final
    evaluation_summary[product] = {
        'LOOK_BACK': best_result['LOOK_BACK'],
        'lambda': best_result['lam'],
        'MAE': mae, 'RMSE': rmse, 'MAPE': mape
    }

    # --- Forecast Future (Recursive) ---
    current_data = df_final[product_columns].tail(best_result['LOOK_BACK']).values.copy()
    forecast_list = []

    for _ in range(FORECAST_HORIZON):
        X_input = []
        for col_name in product_columns:
            for lag in range(1, best_result['LOOK_BACK'] + 1):
                val = current_data[-lag, product_columns.index(col_name)]
                X_input.append(val)
        X_input = np.array(X_input).reshape(1, -1)
        pred_val = gam_final.predict(X_input)[0]
        pred_val = max(0, round(pred_val))
        forecast_list.append(pred_val)

        new_row = np.zeros((1, len(product_columns)))
        new_row[0, product_columns.index(product)] = pred_val
        current_data = np.concatenate((current_data[1:], new_row), axis=0)

    future_forecasts_df_list.append(forecast_list)

    # --- Visualisasi per Produk ---
    plt.figure(figsize=(10, 5))
    plt.plot(df_used['TANGGAL'].iloc[:train_size], y_all.iloc[:train_size], label='Train', color='blue')
    plt.plot(df_used['TANGGAL'].iloc[train_size:], y_test_actual, label='Actual', color='green')
    plt.plot(df_used['TANGGAL'].iloc[train_size:], y_pred_test, label='Predicted', color='red', linestyle='--')
    future_dates = pd.date_range(start=df_final['TANGGAL'].iloc[-1] + pd.Timedelta(weeks=1), periods=FORECAST_HORIZON, freq='W')
    plt.plot(future_dates, forecast_list, label='Future Forecast', color='orange', linestyle='-.')
    plt.title(f'Forecast: {product}\nMAE={mae:.2f}%, RMSE={rmse:.2f}, MAPE={mape:.2f}%')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# --- Ringkasan Hasil ---
eval_df = pd.DataFrame.from_dict(evaluation_summary, orient='index')
eval_df_sorted = eval_df.sort_values(by='MAPE')
print("\n📊 Rangkuman Evaluasi:")
print(eval_df_sorted.to_string())

print("\n📈 Rata-rata Performa Semua Produk:")
print(f"Avg MAE: {eval_df_sorted['MAE'].mean():.2f}")
print(f"Avg RMSE: {eval_df_sorted['RMSE'].mean():.2f}")
print(f"Avg MAPE: {eval_df_sorted['MAPE'].mean():.2f}%")

# --- Future Forecasts DF ---
future_dates_final = pd.date_range(start=df_final['TANGGAL'].iloc[-1] + pd.Timedelta(weeks=1), periods=FORECAST_HORIZON, freq='W')
future_forecasts_df = pd.DataFrame(np.array(future_forecasts_df_list).T, columns=product_columns, index=future_dates_final)
future_forecasts_df.index.name = 'TANGGAL'
print("\n🔮 Prediksi Penjualan (mingguan ke depan):")
print(future_forecasts_df.to_string())