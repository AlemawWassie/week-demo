# Addis Ababa Weather Analysis

A small Python data-processing project that loads a CSV or a list of records, cleans the data with functions, and uses NumPy to analyze weather measurements. It can be run from a Jupyter notebook, Google Colab, or a Python terminal.

## Project files

- `data/addis_ababa_weather.csv` — CSV populated when you run the notebook using historical data from Open-Meteo.
- `weather_analysis.py` — reusable loading, cleaning, and analysis functions.
- `notebooks/weather_analysis.ipynb` — notebook workflow with tables, NumPy summaries, and charts.
- `requirements.txt` — Python packages needed for the project.

**Data note:** Run the notebook while connected to the internet to download historical daily weather estimates for Addis Ababa from Open-Meteo. The source is reanalysis/model-based, not necessarily direct local weather-station observations. Historical data may have a delay. See https://open-meteo.com/en/docs/historical-weather-api.

## 1. Create and activate a virtual environment

Run these commands from the project folder.

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Run the notebook

The notebook downloads historical weather for 2025 by default and overwrites `data/addis_ababa_weather.csv` with the downloaded records. Edit `START_DATE` and `END_DATE` in the notebook to choose another period. An internet connection is required for the download.


```bash
jupyter notebook
```

Open `notebooks/weather_analysis.ipynb` and run the cells in order. If you use Google Colab, upload the notebook, `weather_analysis.py`, and the CSV while keeping the CSV in a `data` folder, or update the data path in the notebook to match where you uploaded it.

## 3. Run the script directly

From the project root:

```bash
python -c "from weather_analysis import load_weather_data, clean_weather_data, summarize_weather; data=clean_weather_data(load_weather_data('data/addis_ababa_weather.csv')); print(summarize_weather(data))"
```

## Data columns

| Column | Meaning | Unit |
|---|---|---|
| `date` | Observation date | YYYY-MM-DD |
| `temperature_c` | Temperature | °C |
| `rainfall_mm` | Daily rainfall | mm |
| `humidity_pct` | Relative humidity | % |
| `wind_speed_kmh` | Wind speed | km/h |

## Cleaning rules

1. Convert measurement columns to numeric values.
2. Parse dates and remove rows with invalid dates.
3. Treat negative rainfall/wind values and humidity outside 0–100% as missing.
4. Remove duplicate dates.
5. Fill missing numeric measurements with their column median.

The project is intentionally small so each step can be read and modified easily.
