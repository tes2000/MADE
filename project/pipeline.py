import os
import json
import requests
import pandas as pd
import sqlite3
import io
import gzip

# Define paths
DATA_DIR = r"C:\Users\HP\Documents\MADE\data"
SOURCE_INFO_FILE = r"C:\Users\HP\Documents\MADE\project"

# Function to fetch data
def fetch_data():
    with open(SOURCE_INFO_FILE, "r") as f:
        sources = json.load(f)["data_sources"]
        
    datasets = {}
    
    for source in sources:
        print(f"Fetching data from {source['source_name']}...")
        
        if source["data_type"] == "csv":
            # Download CSV data directly
            response = requests.get(source["data_urls"])
            df = pd.read_csv(io.StringIO(response.text))
            datasets[source["source_name"]] = df
        elif source["data_type"] == "gzip":
            # Download and extract gzip CSV data
            response = requests.get(source["api_endpoint"], stream=True)
            with gzip.open(io.BytesIO(response.content), 'rb') as f:
                df = pd.read_csv(f)
            datasets[source["source_name"]] = df

    return datasets

# Function to transform data
def transform_data(datasets):
    transformed_data = {}
    for name, df in datasets.items():
        print(f"Transforming data for {name}...")
        
        if name == 'Los Angeles Data Portal':
            # Drop specified columns
            columns_to_drop = [
                "Date Rptd", "Vict Sex", "Vict Age", "Vict Descent",
                "Weapon Desc", "Weapon Used Cd", "Crm Cd 2", "Crm Cd 3", "Crm Cd 4"
            ]
            df = df.drop(columns=columns_to_drop, errors='ignore')
            
            # Convert DATE OCC column to date format
            df['DATE OCC'] = pd.to_datetime(df['DATE OCC'], errors='coerce')
            
            # Filter by date range
            start_date = '2020-01-01'
            end_date = '2021-08-16'
            df = df[(df['DATE OCC'] >= start_date) & (df['DATE OCC'] <= end_date)]
            print(f"Filtered crime data from {start_date} to {end_date}")

    
    return transformed_data

# Function to save datasets
def save_data(datasets):
    os.makedirs(DATA_DIR, exist_ok=True)
    for name, df in datasets.items():
        output_path = os.path.join(DATA_DIR, f"{name.replace(' ', '_').lower()}.sqlite")
        print(f"Saving data for {name} at {output_path}...")
        with sqlite3.connect(output_path) as conn:
            df.to_sql(name.replace(' ', '_').lower(), conn, if_exists="replace", index=False)
    print("Data successfully saved in /data directory.")

# Main pipeline function
def run_pipeline():
    print("Starting data extraction...")
    datasets = fetch_data()
    
    print("Transforming data...")
    transformed_data = transform_data(datasets)
    
    print("Saving data...")
    save_data(transformed_data)

# Entry point
if __name__ == "__main__":
    run_pipeline()
