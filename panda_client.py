#!/usr/bin/env python3
"""
Script to query day-ahead prices for tomorrow using EntsoePandasClient and save the result to a CSV file.
The filename is based on tomorrow's date (YYYYMMDD). If the file already exists, the script exits.
Only data with tomorrow's date is saved.
The result file is stored in the 'data' directory, which is created if necessary.
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

    # Format tomorrow's date for the filename (YYYYMMDD) and for filtering (YYYY-MM-DD)
    timestamp_str = tomorrow.strftime('%Y%m%d')
    filename = f"fi_{timestamp_str}.csv"

    # Create the 'data' directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Define the full file path within the 'data' directory
    file_path = data_dir / filename

    # Exit if the file already exists
    if file_path.exists():
        print(f"File '{file_path}' exists. Exiting the script.")
        sys.exit(1)

    # Initialize the EntsoePandasClient with your API key
    api_key = os.getenv('ENTSO_API_KEY')
    client = EntsoePandasClient(api_key=api_key)

    # Define the time range for tomorrow in the Helsinki timezone
    start = pd.Timestamp(tomorrow, tz='Europe/Helsinki')
    end = pd.Timestamp(tomorrow + timedelta(days=1), tz='Europe/Helsinki')

    # Query the day-ahead prices for the specified time range
    ts = client.query_day_ahead_prices('FI', start=start, end=end)

    # Filter the data to only include rows with tomorrow's date (YYYY-MM-DD)
    target_date_str = tomorrow.strftime("%Y-%m-%d")
    ts = ts[ts.index.strftime("%Y-%m-%d") == target_date_str]

    # Give the Series a name for a nicer header and reset the index to create a DataFrame
    ts.name = "price"
    df = ts.reset_index().rename(columns={"index": "timestamp"})

    # Save the DataFrame to a CSV file without an extra index column
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")


if __name__ == "__main__":
    main()
