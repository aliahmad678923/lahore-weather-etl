"""Step 3 - LOAD: save the clean data into a SQLite database."""

import sqlite3
from pathlib import Path

# The database file is created right next to this script
DATABASE_FILE = Path(__file__).parent / "lahore_weather.db"
TABLE_NAME = "daily_weather"


def load(df):
    df = df.copy()
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")  # store dates as plain text, e.g. 2020-01-31

    connection = sqlite3.connect(DATABASE_FILE)
    # "replace" means running the pipeline again gives a fresh table, not duplicate rows
    df.to_sql(TABLE_NAME, connection, if_exists="replace", index=False)

    # Quick check that everything made it in
    row_count = connection.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
    connection.close()

    print(f"Loaded {row_count} rows into {DATABASE_FILE.name} (table: {TABLE_NAME})")
