"""Step 2 - TRANSFORM: clean the data with pandas and validate it with Pydantic."""

from datetime import date

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, model_validator


class WeatherDay(BaseModel):
    """The rules every day of weather has to follow."""

    date: date
    temp_max: float
    temp_min: float
    rainfall: float = Field(ge=0)          # rain can't be negative
    humidity: float = Field(ge=0, le=100)  # humidity is a percentage
    wind_speed: float = Field(ge=0)        # wind speed can't be negative

    @model_validator(mode="after")
    def min_not_above_max(self):
        if self.temp_min > self.temp_max:
            raise ValueError("temp_min is higher than temp_max")
        return self


def get_season(month):
    """Pakistan's seasons."""
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4):
        return "Spring"
    if month in (5, 6):
        return "Summer"
    if month in (7, 8, 9):
        return "Monsoon"
    return "Autumn"  # October and November


def transform(raw_data):
    # 1. Turn the API response into a table with short column names
    df = pd.DataFrame(raw_data["daily"]).rename(columns={
        "time": "date",
        "temperature_2m_max": "temp_max",
        "temperature_2m_min": "temp_min",
        "precipitation_sum": "rainfall",
        "relative_humidity_2m_mean": "humidity",
        "wind_speed_10m_max": "wind_speed",
    })

    # 2. Parse the date text into real dates
    df["date"] = pd.to_datetime(df["date"])

    # 3. Handle missing values
    print(f"Missing values found: {df.isna().sum().sum()}")
    # Temperature, humidity and wind change gradually from day to day,
    # so a gap is filled using the days before and after it
    gradual_columns = ["temp_max", "temp_min", "humidity", "wind_speed"]
    df[gradual_columns] = df[gradual_columns].interpolate(limit_direction="both")
    # Rainfall can't be guessed, so any day still missing a value is dropped
    df = df.dropna()

    # 4. Validate every row with Pydantic and keep only the valid ones
    valid_rows = []
    for row in df.to_dict("records"):
        try:
            WeatherDay(**row)
            valid_rows.append(row)
        except ValidationError as error:
            print(f"Dropped {row['date'].date()}: {error.errors()[0]['msg']}")
    print(f"{len(valid_rows)} of {len(df)} days passed validation")
    df = pd.DataFrame(valid_rows)

    # 5. Add year, month and season columns for the analysis
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["season"] = df["month"].apply(get_season)

    return df
