import os
import json
import re
import logging
from datetime import datetime
from typing import Dict, List


def _configuration_file(file_path: str) -> dict:
    with open(file_path, "r") as config_file:
        return json.load(config_file)


def _standard_selection_of_schwab_statements() -> Dict[str, str]:
    ...


def _lookup_statements_directory():
    ...


def _list_of_asset_types():
    # Asset types
    equities = "Equities"
    treasuries = "U.S. Treasuries"
    corporate_bonds = "Corporate Bonds"
    exchange_traded_funds = "Exchange Traded Funds"
    bond_funds = "Bond Funds"
    equity_funds = "Equity Funds"
    money_market_funds = "Fund Name"  # Money Market Funds (Non-Sweep)
    other_assets = "Other Assets"
    other_fixed_income = "Other Fixed Income"
    options = "Options"

    all_asset_types = [
        equities, treasuries, corporate_bonds, exchange_traded_funds, bond_funds, equity_funds, money_market_funds,
        other_assets, options, other_fixed_income
    ]

    return all_asset_types


config = _configuration_file("MainScripts/config.json")
statement_directory_path = config["Schwab Statements Directory Path"]
file_names = os.listdir(statement_directory_path)


# Configure logging and Create a logger instance for the current module
logging.basicConfig(
    filename='../app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)




asset_types_as_shown_per_section: Dict[str, str] = config["Asset Types as Shown per Section"]


def extract_schwab_statements() -> Dict[str, str]:
    """
    Extract the "Schwab Portfolio 1. Schwab Statements" dictionary from the given JSON configuration file.
    :return: The "Schwab Portfolio 1. Schwab Statements" dictionary from the configuration file.
    """
    logging.info("Extracting 'Schwab Portfolio Statements' dictionary from config.json")
    statements = config.get('Schwab Portfolio Statements', {})
    logging.info("'Schwab Portfolio Statements' dictionary extracted")

    return statements


def extract_fixed_income_etf_tickers() -> List[str]:
    """
    Extract a list of fixed income ETF tickers from the given JSON configuration file.
    :return: A list of fixed income ETF tickers.
    """

    fixed_income_tickers = config.get("Fixed Income ETFs", [])
    logging.info("Fixed income ETF tickers extracted")
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


def validated_file_path(base_file_name: str) -> str:
    """
    Validate and retrieve the full file path for a PDF statement.

    This function takes a base file name, appends it to the statement folder path, and checks if the corresponding
    PDF file exists. If the file is found, it returns the full file path; otherwise, it raises a `ValueError` with
    an informative message.

    :param base_file_name: The base name of the PDF statement file.
    :type base_file_name: str
    :return: The full file path for the PDF statement.
    :rtype: str
    :raises ValueError: If the specified PDF file does not exist in the statement folder.
    """
    file_path = os.path.join(statement_directory_path, f"{base_file_name}.pdf")
    file_was_found = os.path.isfile(file_path)

    if file_was_found:
        return file_path
    else:
        raise ValueError(f"PDF file '{base_file_name}.pdf' not found in the statement folder.")
