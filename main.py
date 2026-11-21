"""Runs the whole ETL pipeline: Extract -> Transform -> Load."""

from extract import extract
from load import load
from transform import transform

print("Step 1: Extract")
raw_data = extract()

print("\nStep 2: Transform")
clean_df = transform(raw_data)

print("\nStep 3: Load")
load(clean_df)

print("\nDone! Open eda.ipynb to explore the data.")
