import os
import json
import re
from datetime import datetime
from typing import Dict, List


def _configuration_file(file_path: str) -> dict:
    with open(file_path, "r") as config_file:
        return json.load(config_file)


config = _configuration_file("PythonScripts/ScrapingScripts/config.json")
statement_directory_path = config["Schwab Statements Directory Path"]
file_names = os.listdir(statement_directory_path)


asset_types_as_shown_per_section: Dict[str, str] = config["Asset Types as Shown per Section"]


def extract_schwab_statements() -> str:
    """
    Extract the "Schwab Portfolio 1. Schwab Statements" dictionary from the given JSON configuration file.
    :return: The "Schwab Portfolio 1. Schwab Statements" dictionary from the configuration file.
    """
    statements = config.get('Schwab Portfolio Statements', {})

    return config["Most Recent Schwab Statement"]


def extract_fixed_income_etf_tickers() -> List[str]:
    """
    Extract a list of fixed income ETF tickers from the given JSON configuration file.
    :return: A list of fixed income ETF tickers.
    """

    fixed_income_tickers = config.get("Fixed Income ETFs", [])
    return fixed_income_tickers


def validate_statement_files() -> bool:
    """
    Validates the PDF statement files in the specified folder.

    This function validates the filenames of the PDF statement files in the specified folder.
    The filenames should be in the format 'YYYY-Month.pdf' where 'YYYY' is a valid year
    within the last 10 years and 'Month' is a valid lowercase month name.

    :return: True if all filenames are valid, False otherwise.
    :raises ValueError: If a filename does not match the expected format.
    """

    # Regular expression pattern to match year and lowercase month
    pattern = r'(\d{4})-(\w+)\.pdf'

    # Iterate through each file name and validate
    for file_name in file_names:
        if file_name == "empty_file.txt":
            continue

        try:
            match = re.match(pattern, file_name.lower())
            if not match:
                raise ValueError(f"Invalid filename format: {file_name}")

            year, month = match.groups()

            # Convert year to an integer
            year = int(year)

            # Check if the year is within the last 10 years
            current_year = datetime.now().year
            if not (current_year - 10 <= year <= current_year):
                raise ValueError(f"Invalid year: {year}")

            # Check if the month is valid
            valid_months = [
                "january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december"
            ]
            if month not in valid_months:
                raise ValueError(f"Invalid month: {month}")

        except (ValueError, IndexError):
            raise ValueError(f"Invalid filename: {file_name}")

    return True

