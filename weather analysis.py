"""Small weather data-processing project for Addis Ababa.

The included CSV is illustrative sample data for practicing data cleaning and analysis.
It is not an official weather record or a live forecast.
"""
from pathlib import Path
import json
from urllib.parse import urlencode
from urllib.request import urlopen
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "date", "temperature_c", "rainfall_mm", "humidity_pct", "wind_speed_kmh"
]

def load_weather_data(source):
    """Load weather data from a CSV path or a list of dictionaries."""
    if isinstance(source, (str, Path)):
        data = pd.read_csv(source)
    elif isinstance(source, list):
        data = pd.DataFrame(source)
    else:
        raise TypeError("source must be a CSV path or a list of dictionaries")

    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    return data.copy()


def download_real_weather(start_date="2025-01-01", end_date="2025-12-31"):
    """Download historical daily weather estimates for Addis Ababa from Open-Meteo.

    Data are reanalysis/model-based historical estimates, not direct station readings.
    The returned columns match the project's analysis schema.
    """
    params = {
        "latitude": 9.03,
        "longitude": 38.74,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join([
            "temperature_2m_mean",
            "precipitation_sum",
            "relative_humidity_2m_mean",
            "wind_speed_10m_mean",
        ]),
        "timezone": "Africa/Addis_Ababa",
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urlencode(params)
    with urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("error"):
        raise RuntimeError(payload.get("reason", "Weather API request failed."))

    daily = payload.get("daily", {})
    if not daily.get("time"):
        raise ValueError("The weather API returned no daily records for this date range.")

    return pd.DataFrame({
        "date": daily["time"],
        "temperature_c": daily.get("temperature_2m_mean"),
        "rainfall_mm": daily.get("precipitation_sum"),
        "humidity_pct": daily.get("relative_humidity_2m_mean"),
        "wind_speed_kmh": daily.get("wind_speed_10m_mean"),
    })


def clean_weather_data(data):
    """Standardize columns, parse dates, and replace invalid values with missing values."""
    cleaned = data.copy()
    cleaned.columns = [str(column).strip().lower() for column in cleaned.columns]

    # Convert measurement columns to numbers; text that cannot be converted becomes NaN.
    numeric_columns = [
        "temperature_c", "rainfall_mm", "humidity_pct", "wind_speed_kmh"
    ]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")

    # Negative rainfall/wind and humidity outside 0–100 are invalid measurements.
    cleaned.loc[cleaned["rainfall_mm"] < 0, "rainfall_mm"] = np.nan
    cleaned.loc[cleaned["wind_speed_kmh"] < 0, "wind_speed_kmh"] = np.nan
    cleaned.loc[
        (cleaned["humidity_pct"] < 0) | (cleaned["humidity_pct"] > 100),
        "humidity_pct"
    ] = np.nan

    # Remove rows without a usable date and duplicate dates.
    cleaned = cleaned.dropna(subset=["date"])
    cleaned = cleaned.drop_duplicates(subset=["date"], keep="first")
    cleaned = cleaned.sort_values("date").reset_index(drop=True)

    # Fill missing numeric values with each column's median.
    for column in numeric_columns:
        if cleaned[column].notna().any():
            cleaned[column] = cleaned[column].fillna(cleaned[column].median())

    return cleaned

def summarize_weather(data):
    """Use NumPy to calculate summary statistics and simple weather counts."""
    if data.empty:
        raise ValueError("There are no rows to summarize.")

    temperature = data["temperature_c"].to_numpy(dtype=float)
    rainfall = data["rainfall_mm"].to_numpy(dtype=float)
    humidity = data["humidity_pct"].to_numpy(dtype=float)
    wind = data["wind_speed_kmh"].to_numpy(dtype=float)

    rainy_days = int(np.count_nonzero(rainfall > 0))
    return {
        "days_recorded": int(len(data)),
        "average_temperature_c": float(np.mean(temperature)),
        "minimum_temperature_c": float(np.min(temperature)),
        "maximum_temperature_c": float(np.max(temperature)),
        "total_rainfall_mm": float(np.sum(rainfall)),
        "average_rainfall_mm": float(np.mean(rainfall)),
        "rainy_days": rainy_days,
        "average_humidity_pct": float(np.mean(humidity)),
        "average_wind_speed_kmh": float(np.mean(wind)),
        "temperature_std_dev_c": float(np.std(temperature)),
    }

def monthly_summary(data):
    """Return monthly average temperature and total rainfall."""
    result = data.copy()
    result["month"] = result["date"].dt.to_period("M").astype(str)
    return result.groupby("month", as_index=False).agg(
        average_temperature_c=("temperature_c", "mean"),
        total_rainfall_mm=("rainfall_mm", "sum"),
        average_humidity_pct=("humidity_pct", "mean"),
    ).round(2)
