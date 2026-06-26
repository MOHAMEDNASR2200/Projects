# Weather Temperature Forecasting — ML vs Deep Learning

A two-notebook project comparing classical machine learning and recurrent neural networks for short-term temperature forecasting using the [Szeged Weather History dataset](https://www.kaggle.com/datasets/budincsevity/szeged-weather) (hourly meteorological records).

---

## Project Structure

```
├── Weather_Classical_ML_clean.ipynb   # Classical ML benchmark with feature engineering
├── Weather_RNN_LSTM_GRU_clean.ipynb   # Deep learning comparison: LSTM, GRU, SimpleRNN
└── README.md
```

---

## Notebooks

### `Weather_Classical_ML_clean.ipynb`

Tests all viable scikit-learn regressors on a feature-engineered dataset, with the hypothesis that 12-hour rolling statistics can give classical models temporal awareness competitive with RNNs.

**Pipeline:**
1. Date parsing — extract Year, Month, Day, Hour from timestamp
2. Temporal feature engineering — 12-hour rolling mean and std for all 7 meteorological variables (14 new features), shifted by 1 step to prevent leakage
3. IQR-based outlier clipping
4. Drop non-numeric and zero-variance columns; drop `Apparent Temperature` (data leakage — derived from target)
5. Temporal 80/20 train/test split (`shuffle=False`)
6. Automated benchmark of all compatible sklearn regressors
7. Detailed evaluation of the best model

**Key result:**

| Model | R² | RMSE | Train Time |
|---|---|---|---|
| HistGradientBoostingRegressor | **0.9755** | **1.40 °C** | ~1.4s |
| ExtraTreesRegressor | 0.9743 | 1.43 °C | ~70s |
| RandomForestRegressor | 0.9720 | 1.50 °C | ~263s |

**Outputs:** `regressor_comparison_results.csv`, `model_comparison.png`, `best_model_predictions.png`

---

### `Weather_RNN_LSTM_GRU_clean.ipynb`

Trains three recurrent architectures on the same preprocessing pipeline for a fair comparison.

**Pipeline:**
1. Same date parsing and outlier clipping as the classical notebook
2. Features: Temperature, Humidity, Visibility, Pressure (4 direct measurements; `Apparent Temperature` excluded as leakage)
3. MinMaxScaler on features and target
4. Sliding window sequence construction — `TIME_STEPS=12` (12 consecutive hours → predict next hour)
5. Temporal 80/20 split (`shuffle=False`)
6. Train LSTM, SimpleRNN, and GRU — 50 epochs, batch size 32

**Model architectures:**

| Model | Layer 1 | Dropout | Layer 2 | Output |
|---|---|---|---|---|
| LSTM | LSTM(26, return_seq=True) | 0.3 | LSTM(26) | Dense(1) |
| SimpleRNN | SimpleRNN(52, return_seq=True) | 0.3 | SimpleRNN(52) | Dense(1) |
| GRU | GRU(30, return_seq=True) | 0.3 | GRU(30) | Dense(1) |

**Outputs:** per-model prediction plots, `deep_learning_vs_classical_comparison.csv`, `training_loss_curves.png`

---

## Overall Comparison

| Model | R² | RMSE |
|---|---|---|
| Deep Learning (LSTM/GRU/RNN) | *see notebook output* | *see notebook output* |
| HistGBT — classical + rolling features | **0.9755** | **1.40 °C** |

**Takeaway:** With 12-hour rolling mean + std features, classical ML achieves R²=0.9755 and RMSE=1.40 °C in ~1.4 seconds of training — competitive with recurrent neural networks at a fraction of the compute cost.

---

## Dataset

**Szeged Weather History** — available on Kaggle: `szeged-weather/weatherHistory.csv`

Variables: Temperature, Apparent Temperature, Humidity, Wind Speed, Wind Bearing, Visibility, Pressure, Precip Type, Summary.

Place the CSV at:
- Classical ML notebook (Kaggle): `/kaggle/input/szeged-weather/weatherHistory.csv`
- Deep Learning notebook (Kaggle): `/kaggle/input/datasets/mohamednasra/weather/weatherHistory.csv`
- Colab: `/content/weatherHistory.csv` (update the `pd.read_csv(...)` path in whichever notebook you use)

---

## Requirements

```
numpy
pandas
matplotlib
scikit-learn
tensorflow >= 2.x
```

Install with:

```bash
pip install numpy pandas matplotlib scikit-learn tensorflow
```

---

## Key Design Decisions

- **`shuffle=False`** in all train/test splits — shuffling time series data causes future leakage, inflating metrics artificially.
- **`Apparent Temperature` excluded** — it is a derived function of Temperature × Humidity × Wind Speed; including it as a feature constitutes data leakage for temperature prediction.
- **`ffill()` instead of `fillna(method='ffill')`** — the method-based syntax is deprecated in recent pandas versions.
- **50 epochs** for deep learning models — increased from the original 10 for a fair comparison against the classical baseline.
- **`shift(1)` before rolling** — ensures rolling statistics use only past data, preventing look-ahead bias.
