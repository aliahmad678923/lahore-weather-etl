# Lahore Weather ETL + EDA

 
## Tools we used

| Tool | What it does here |
|---|---|
| **Python** | The language everything is written in |
| **requests** | Calls the weather API (Extract) |
| **pandas** | Cleans and reshapes the data (Transform) |
| **Pydantic** | Checks every row follows our rules (Transform) |
| **SQLite** | Stores the clean data in one file, `lahore_weather.db` (Load) |
| **Jupyter Notebook** | Where the analysis lives (EDA) |
| **matplotlib + seaborn** | Draw the charts in the notebook |
| **HTML + Plotly.js** | The website's page and its interactive charts (hover, zoom) |
| **Vercel** | Hosts the website for free |

The data comes from the free **Open-Meteo Historical Weather API**. No account or API key needed.

**Live website:** https://lahore-weather-etl-eta.vercel.app/

## Setting it up

You just need **Python 3.10 or newer** installed.

1. Open a terminal inside this folder.
2. Install the libraries:

   ```
   pip install -r requirements.txt
   ```

That's it.

## Running it

**Step 1: run the pipeline** (needs internet, takes a few seconds):

```
python main.py
```

You should see something like:

```
Step 1: Extract
Extracted 2192 days of weather data

Step 2: Transform
Missing values found: 0
2192 of 2192 days passed validation

Step 3: Load
Loaded 2192 rows into lahore_weather.db (table: daily_weather)
```

**Step 2: open the analysis:**

```
jupyter notebook eda.ipynb
```

It opens in your browser. Click **Run → Run All Cells** to rerun everything. The notebook already has its results saved, so you can also just read it without running anything (GitHub shows it too).

**Step 3: update and open the website:**

```
python export_data.py
python -m http.server 8000 -d website
```

The first command saves the results into `website/data.json`. The second one serves the website: open http://localhost:8000 in your browser. Press `Ctrl+C` in the terminal to stop it.

Running `main.py` again is safe. It rebuilds the table from scratch, so no duplicate rows.

## How it works

```
Open-Meteo API  →  extract.py  →  transform.py  →  load.py  →  lahore_weather.db  →  eda.ipynb
                                                                                  →  export_data.py  →  website/
```

**`extract.py`**: asks the API for Lahore's daily max/min temperature, rainfall, humidity and wind speed from 1 Jan 2020 to 31 Dec 2025, and returns the response.

**`transform.py`**: turns the response into a pandas table, then:
- gives the columns short names (`temp_max`, `temp_min`, `rainfall`, `humidity`, `wind_speed`)
- turns the date text into real dates
- handles missing values: gaps in temperature, humidity or wind are filled from the days around them; days with no rainfall value are dropped (rain can't be guessed)
- validates every row with a Pydantic model (`WeatherDay`). A row is dropped if humidity isn't between 0 and 100, rainfall or wind speed is negative, or the low temperature is higher than the high
- adds `year`, `month` and `season` columns

Seasons follow Pakistan's calendar: Winter (Dec–Feb), Spring (Mar–Apr), Summer (May–Jun), Monsoon (Jul–Sep), Autumn (Oct–Nov).

**`load.py`**: writes the table into `lahore_weather.db` as a table called `daily_weather`, then counts the rows to confirm.

**`main.py`**: runs the three steps above in order.

**`eda.ipynb`**: reads the data back from SQLite and goes through:
1. Summary statistics
2. Yearly temperature trends
3. Monthly and monsoon rainfall patterns
4. Season comparison
5. Correlation heatmap
6. Heatwave days (a *hot day* is 40°C or more; a *heatwave day* is part of 3+ hot days in a row)

**`export_data.py`**: reads `lahore_weather.db`, does the same calculations as the notebook (yearly averages, monthly rain, seasons, correlation, heatwave days) and saves the results into `website/data.json`. All the maths stays in Python.

**`website/index.html`**: the website. It loads `data.json` and draws it: summary cards, six tabs with interactive charts (hover for exact values, drag to zoom, double-click to zoom out, click a legend item to hide it), a year picker for the heatwave chart and a table of the data. It never calls the weather API, so it keeps working even if Open-Meteo is down.

## Deploying the website

The website is just two files (`index.html` and `data.json`), so Vercel hosts it as a plain static site. `vercel.json` tells Vercel exactly that: use no framework and serve the `website/` folder. Without it, Vercel sees `main.py` and wrongly treats the whole repo as a Python web server.

Vercel is connected to this GitHub repo, so every push to `main` publishes a new version automatically. So to update the live site: run `python main.py`, then `python export_data.py`, then commit and push.

## Project files

```
lahore-weather-etl/
├── extract.py          Step 1: get the data from the API
├── transform.py        Step 2: clean + validate
├── load.py             Step 3: save into SQLite
├── main.py             Runs steps 1–3
├── eda.ipynb           The analysis
├── export_data.py      Saves the results for the website
├── website/
│   ├── index.html      The website
│   └── data.json       The website's data (created by export_data.py)
├── vercel.json         Tells Vercel to serve the website folder
├── lahore_weather.db   The database (created by main.py)
└── requirements.txt    Libraries to install
```

## If something goes wrong

- **`pip` or `python` not found**: try `py -m pip install -r requirements.txt` and `py main.py` (Windows).
- **Connection error when running `main.py`**: check your internet. The API needs to be reachable.
- **Notebook says `no such table: daily_weather`**: run `python main.py` first so the database exists.
- **Website is blank when you double-click `index.html`**: browsers block it from loading `data.json` that way. Use `python -m http.server 8000 -d website` and open http://localhost:8000 instead.
