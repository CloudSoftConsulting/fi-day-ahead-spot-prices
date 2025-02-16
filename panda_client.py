#!/usr/bin/env python3
"""
Script to query day-ahead prices for tomorrow using EntsoePandasClient and save the result to a CSV file.
The filename is based on tomorrow's date (day portion) and stored in a directory structure:
    data/<year>/<month>/<day>.csv
If the file already exists or if the API returns an incomplete dataset, the script exits.
The last record (midnight of the following day) is dropped before saving.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from entsoe import EntsoePandasClient


def main():
    # Set 'now' to today's date at midnight
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # Compute tomorrow's date (at midnight)
    tomorrow = now + timedelta(days=1)

    # Define time range for tomorrow (from tomorrow's midnight to day after tomorrow's midnight)
    start = pd.Timestamp(tomorrow, tz='Europe/Helsinki')
    end = pd.Timestamp(tomorrow + timedelta(days=1), tz='Europe/Helsinki')

    # Initialize the EntsoePandasClient with your API key from environment variable
    client = EntsoePandasClient(api_key=os.getenv('ENTSO_API_KEY'))

    # Query the day-ahead prices for the specified time range
    ts = client.query_day_ahead_prices('FI', start=start, end=end)

    # If the API returns an incomplete dataset (fewer than 25 records), do not save the file.
    if len(ts) < 25:
        print("Incomplete data set received (fewer than 25 records). Not saving file.")
        sys.exit(0)

    # Give the Series a name for a nicer header and reset the index to create a DataFrame
    ts.name = "price"
    df = ts.reset_index().rename(columns={"index": "timestamp"})

    # Drop the last record (belongs to the next day)
    df = df.iloc[:-1]

    # Prepare directory structure: data/<year>/<month>/
    year = tomorrow.strftime('%Y')
    month = tomorrow.strftime('%m')
    day = tomorrow.strftime('%d')  # We'll use the day as the filename

    base_dir = Path("data") / year / month
    base_dir.mkdir(parents=True, exist_ok=True)

    file_path = base_dir / f"{day}.csv"

    # Exit if the file already exists
    if file_path.exists():
        print(f"File '{file_path}' exists. Exiting the script.")
        sys.exit(0)

    # Save the DataFrame to CSV without an extra index column
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")


if __name__ == "__main__":
    main()
