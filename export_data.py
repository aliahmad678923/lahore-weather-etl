"""Export the analysis from SQLite into website/data.json for the website.

Run it after main.py:  python export_data.py
All the calculations happen here in Python; the website only draws the results.
"""

import json
import sqlite3
from pathlib import Path

import pandas as pd

from load import DATABASE_FILE, TABLE_NAME

OUTPUT_FILE = Path(__file__).parent / "website" / "data.json"
SEASON_ORDER = ["Winter", "Spring", "Summer", "Monsoon", "Autumn"]
WEATHER_COLUMNS = ["temp_max", "temp_min", "rainfall", "humidity", "wind_speed"]


def export_data():
    connection = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", connection, parse_dates=["date"])
    connection.close()

    # Heatwave detection, same rule as the notebook:
    # a hot day is 40 °C or more, a heatwave day is part of 3+ hot days in a row
    df["hot_day"] = df["temp_max"] >= 40
    run_number = (df["hot_day"] != df["hot_day"].shift()).cumsum()
    run_length = df.groupby(run_number)["hot_day"].transform("size")
    df["heatwave_day"] = df["hot_day"] & (run_length >= 3)

    hottest = df.loc[df["temp_max"].idxmax()]
    yearly_temp = df.groupby("year")[["temp_max", "temp_min"]].mean().round(1)
    monthly_rain = df.groupby(["year", "month"])["rainfall"].sum().groupby("month").mean().round(1)
    yearly_rain = df.groupby("year")["rainfall"].sum()
    monsoon_rain = df[df["season"] == "Monsoon"].groupby("year")["rainfall"].sum()
    season_table = df.groupby("season")[WEATHER_COLUMNS].mean().round(1).loc[SEASON_ORDER]
    correlation = df[WEATHER_COLUMNS].corr().round(2)
    heat_per_year = df.groupby("year")[["hot_day", "heatwave_day"]].sum()

    data = {
        "summary": {
            "days": len(df),
            "avg_high": round(float(df["temp_max"].mean()), 1),
            "hottest_temp": float(hottest["temp_max"]),
            "hottest_date": hottest["date"].strftime("%d %b %Y"),
            "total_rain": int(round(df["rainfall"].sum())),
            "heatwave_days": int(df["heatwave_day"].sum()),
        },
        "years": yearly_temp.index.tolist(),
        "yearly_high": yearly_temp["temp_max"].tolist(),
        "yearly_low": yearly_temp["temp_min"].tolist(),
        "monthly_rain": monthly_rain.tolist(),
        "monsoon_rain": monsoon_rain.round(0).tolist(),
        "other_rain": (yearly_rain - monsoon_rain).round(0).tolist(),
        "seasons": season_table.reset_index().to_dict("records"),
        "correlation": correlation.values.tolist(),
        "hot_days": heat_per_year["hot_day"].tolist(),
        "heatwave_days": heat_per_year["heatwave_day"].tolist(),
        # Every day, for the daily heatwave chart, the season boxplot and the data table
        "days": df.assign(date=df["date"].dt.strftime("%Y-%m-%d"))
                  [["date", *WEATHER_COLUMNS, "season", "heatwave_day"]]
                  .to_dict("records"),
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(data), encoding="utf-8")
    print(f"Exported {len(df)} days to {OUTPUT_FILE.relative_to(Path(__file__).parent)}")


if __name__ == "__main__":
    export_data()
