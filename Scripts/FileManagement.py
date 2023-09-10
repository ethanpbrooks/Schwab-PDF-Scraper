import os
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional

# File Paths
_config_file_path = "./config.json"
_statements_directory_path = "./Statements"

with open(_config_file_path, "r") as config_file:
    config = json.load(config_file)


# Configure logging and Create a logger instance for the current module
logging.basicConfig(
    filename='../app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get a list of statement filenames in the folder
_statement_folder_path = "Statements"
_statement_filepaths = os.listdir("Statements")
file_names = [
    filename for filename in _statement_filepaths if os.path.isfile(os.path.join("Statements", filename))
]

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

asset_types_as_shown_per_section: Dict[str, str] = config["Asset Types as Shown per Section"]


def symbol_corresponding_to_asset(asset: str) -> str:
    """
    Get the symbol corresponding to a given asset type.

    This function takes an asset type as input and checks if it exists in
    the 'asset_types_as_shown_per_section' dictionary. If it does, it
    translates the asset name to the corresponding section name and
    retrieves the symbol for that asset type from the 'config' dictionary.

    :param asset: The asset type for which to retrieve the symbol.
    :type asset: str
    :return: The symbol corresponding to the input asset type.
    :rtype: str
    :raises KeyError: If the input asset type is not found in the 'asset_types_as_shown_per_section' dictionary.
    """
    if asset not in asset_types_as_shown_per_section:
        raise KeyError(f"'{asset}' not found in configuration file!")

    translated_asset_name = asset_types_as_shown_per_section[asset]
    return config["Symbols Corresponding to Each Asset Type"][translated_asset_name]


def clean_text_lines_from_page(text_lines: List[str], asset: str) -> Optional[List[str]]:
    """
    Clean text lines from a page by removing specified line items.

    This function takes a list of text lines from a page and removes specific
    line items based on the configuration. It retains lines that start with
    the 'asset' string and stops processing when it encounters a line indicating
    the end of sections (e.g., "Total asset").

    :param text_lines: List of text lines from a page.
    :type text_lines: List[str]
    :param asset: The asset string to identify lines to retain.
    :type asset: str
    :return: Cleaned list of text lines.
    :rtype: List[str]
    """
    cleaned_text_lines: List[str] = []  # Initialize a list to store cleaned text lines
    items_to_remove: List[str] = config["Line Items to Remove"]  # Get line items to remove from the configuration
    end_of_sections = f"Total {asset}"

    index_of_start_of_section = next((index for index, text_line in enumerate(text_lines) if asset in text_line), None)
    if index_of_start_of_section is None:
        return None


    for text_line in text_lines[index_of_start_of_section:]:
        # Check if the end of sections is reached, and stop processing if found
        if end_of_sections in text_line:
            break

        # Check if the text line starts with any asset type
        line_contains_asset_type = any(
            text_line.startswith(asset_types) for asset_types in asset_types_as_shown_per_section
        )

        # Check if the text line contains any item to remove
        line_contains_an_item_to_remove = any(item in text_line for item in items_to_remove)

        # Retain the line if it doesn't contain any item to remove, or it starts with the 'asset' string
        if not (line_contains_an_item_to_remove and not line_contains_asset_type):
            cleaned_text_lines.append(text_line)

    return cleaned_text_lines[1:]


def extract_schwab_statements() -> Dict[str, str]:
    """
    Extract the "Schwab Portfolio Statements" dictionary from the given JSON configuration file.
    :return: The "Schwab Portfolio Statements" dictionary from the configuration file.
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
    file_path = os.path.join(_statement_folder_path, f"{base_file_name}.pdf")
    file_was_found = os.path.isfile(file_path)

    if file_was_found:
        return file_path
    else:
        raise ValueError(f"PDF file '{base_file_name}.pdf' not found in the statement folder.")
