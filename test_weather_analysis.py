import unittest
import pandas as pd
from weather_analysis import load_weather_data, clean_weather_data, summarize_weather

class WeatherAnalysisTests(unittest.TestCase):
    def test_load_list_and_clean_invalid_measurements(self):
        rows = [{
            "date": "2025-01-01",
            "temperature_c": 20,
            "rainfall_mm": -1,
            "humidity_pct": 130,
            "wind_speed_kmh": 5,
        }, {
            "date": "2025-01-02",
            "temperature_c": 21,
            "rainfall_mm": 2,
            "humidity_pct": 60,
            "wind_speed_kmh": 6,
        }]
        cleaned = clean_weather_data(load_weather_data(rows))
        self.assertEqual(len(cleaned), 2)
        self.assertGreaterEqual(cleaned.loc[0, "rainfall_mm"], 0)
        self.assertGreaterEqual(cleaned.loc[0, "humidity_pct"], 0)
        self.assertLessEqual(cleaned.loc[0, "humidity_pct"], 100)

    def test_summary_counts_rows(self):
        rows = [{
            "date": "2025-01-01",
            "temperature_c": 20,
            "rainfall_mm": 0,
            "humidity_pct": 50,
            "wind_speed_kmh": 5,
        }]
        result = summarize_weather(clean_weather_data(load_weather_data(rows)))
        self.assertEqual(result["days_recorded"], 1)
        self.assertEqual(result["rainy_days"], 0)

if __name__ == "__main__":
    unittest.main()
