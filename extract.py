"""Step 1 - EXTRACT: download Lahore's daily weather from the Open-Meteo API."""

import requests

API_URL = "https://archive-api.open-meteo.com/v1/archive"

# Lahore's coordinates and the years we want
LATITUDE = 31.5204
LONGITUDE = 74.3587
START_DATE = "2020-01-01"
END_DATE = "2025-12-31"

# The daily values we ask the API for
DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "relative_humidity_2m_mean",
    "wind_speed_10m_max",
]


def extract():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": "Asia/Karachi",
    }

    response = requests.get(API_URL, params=params, timeout=60)
    response.raise_for_status()  # stop here if the API returned an error

    data = response.json()
    print(f"Extracted {len(data['daily']['time'])} days of weather data")
    return data
