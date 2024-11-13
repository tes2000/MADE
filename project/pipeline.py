import os
import pandas as pd
import sqlite3
import requests
from io import BytesIO
import gzip

class CrimeWeatherPipeline:
    def __init__(self):
        # Define paths and filenames
        self.crime_data_url = '/mnt/data/Crime_Data_from_2020_to_Present.csv'
        self.weather_data_url = "https://bulk.meteostat.net/v2/monthly/72295.csv.gz"
        self.database_path = '/data/crime_weather_data.db'

    def extract(self) -> None:
        # Extract crime data
        print("Extracting crime data...")
        self.crime_data = pd.read_csv(self.crime_data_url)

        # Extract weather data from the Meteostat API endpoint
        print("Extracting weather data...")
        response = requests.get(self.weather_data_url)
        if response.status_code == 200:
            with gzip.open(BytesIO(response.content), 'rt') as f:
                self.weather_data = pd.read_csv(f)
        else:
            raise Exception("Failed to download weather data")

    def transform(self) -> None:
        print("Transforming crime data...")
        # Drop specified columns
        columns_to_drop = [
            "Date Rptd", "Vict Sex", "Vict Age", "Vict Descent",
            "Weapon Desc", "Weapon Used Cd", "Crm Cd 2", "Crm Cd 3", "Crm Cd 4"
        ]
        self.crime_data.drop(columns=columns_to_drop, inplace=True, errors='ignore')

        # Change DATE OCC column format to date
        self.crime_data['DATE OCC'] = pd.to_datetime(self.crime_data['DATE OCC'], errors='coerce')

        print("Transforming weather data...")
        # Example transformation on weather data if needed
        # Ensure date column in weather data is properly formatted as datetime
        if 'time' in self.weather_data.columns:
            self.weather_data['time'] = pd.to_datetime(self.weather_data['time'], errors='coerce')

    def load(self) -> None:
        print("Loading data into SQLite database...")
        os.makedirs('/data', exist_ok=True)
        
        # Connect to SQLite database
        conn = sqlite3.connect(self.database_path)
        
        # Load crime data into the database
        self.crime_data.to_sql('crime_data', conn, if_exists='replace', index=False)
        
        # Load weather data into the database
        self.weather_data.to_sql('weather_data', conn, if_exists='replace', index=False)
        
        # Close the connection
        conn.close()
        print("Data successfully loaded into SQLite database")

    def run_pipeline(self) -> None:
        self.extract()
        self.transform()
        self.load()


if __name__ == "__main__":
    pipeline = CrimeWeatherPipeline()
    pipeline.run_pipeline()
