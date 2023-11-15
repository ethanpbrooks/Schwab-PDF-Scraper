from typing import Dict

import numpy as np
import pandas as pd
import os


_sectors_csv_path = "4. Sectors"


def get_sector_tickers() -> Dict[str, np.array]:
    """
    Retrieves a mapping of sectors to their corresponding ticker symbols from CSV files.

    :returns Dict[str, np.array]: A dictionary where keys are sector names and values are arrays of ticker symbols.
    """

    # Get a list of CSV files in the specified path
    sector_paths = os.listdir(_sectors_csv_path)

    sector_ticker_map: Dict[str, np.array] = {}

    # Loop through each CSV file in the specified path
    for path in sector_paths:
        # Build the full path to the CSV file
        full_path = f"{_sectors_csv_path}/{path}"

        # Add the sector-ticker mapping to the dictionary
        tickers = pd.read_csv(full_path)["Symbol"].to_numpy()
        sector_name = path.removesuffix(".csv")

        sector_ticker_map[sector_name] = tickers

    return sector_ticker_map
