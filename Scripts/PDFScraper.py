import fitz
import os
import pandas as pd
import logging
import Scripts.FileManagement as FileManagement

from dataclasses import dataclass, field
from typing import List, Optional, Dict

# File Paths
config_file_path = "./config.json"
statements_directory_path = "./Statements"
_schwab_statement_paths: Dict[str, str] = FileManagement.extract_schwab_statements()

_months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


# Dataframe columns
equity_columns = ["Symbol", "Name", "Quantity", "Price"]
equity_numeric = ["Quantity", "Price"]

option_columns = ["Symbol", "Name", "Quantity", "Price", "Market Value"]
option_numeric = ["Quantity", "Price", "Market Value"]

fixed_income_columns = ["CUSIP", "Name", "Par", "Market Price", "Market Value"]
fi_numeric = ["Par", "Market Price", "Market Value"]


def _read_pdf(pdf_name: str) -> Dict[int, list]:
    """
    Extracts and splits text content from each page_number of a PDF document.

    This method reads a PDF file, extracts the text content from each page_number, and splits the text into lines.

    :param pdf_name: The name of the PDF file.
    :return: A dictionary where the keys represent page_number numbers and the values represent the extracted and
             split text content from each page_number.
    :raises FileNotFoundError: If the specified PDF file is not found in the folder.
    """
    logging.info(f"Extracting and splitting text content from PDF: {pdf_name}")

    pdf_path = os.path.join(statements_directory_path, pdf_name)

    # Check if the PDF file exists
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"File {pdf_name} was not found in the folder.")

    # Initialize an empty dictionary to store extracted and split text content
    extracted_pages = {}

    # Open the PDF document using fitz
    with fitz.Document(pdf_path) as file:
        # Iterate through each page_number in the PDF document
        for page_number in file:
            logging.info(f"Extracting text content from page {page_number.number + 1}")

            # Extract text content from the current page_number and split it into lines
            text_lines = page_number.get_textpage().extractText().split("\n")

            # Remove empty lines from the split text
            cleaned_text_lines = [line for line in text_lines if line.strip() != ""]

            # Store the cleaned text lines in the dictionary with the page_number number as the key
            extracted_pages[page_number.number + 1] = cleaned_text_lines

            logging.info(f"Extracted {len(cleaned_text_lines)} lines from page {page_number.number + 1}")

    logging.info(f"Extraction of text content from PDF {pdf_name} completed")
    return extracted_pages


def _symbol_corresponding_to_asset(asset: str) -> str:
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
    if asset not in FileManagement.asset_types_as_shown_per_section:
        raise KeyError(f"'{asset}' not found in configuration file!")


    if asset == "Other Fixed Income":
        return FileManagement.config["Symbols Corresponding to Each Asset Type"]["Partial Call"]


    translated_asset_name = FileManagement.asset_types_as_shown_per_section[asset]
    return FileManagement.config["Symbols Corresponding to Each Asset Type"][translated_asset_name]


def _clean_text_lines_from_page(text_lines: List[str], asset: str) -> Optional[List[str]]:
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

    # Initialize a list to store cleaned text lines and Get line items to remove from the configuration
    cleaned_text_lines: List[str] = []
    items_to_remove: List[str] = FileManagement.config["Line Items to Remove"]
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
            text_line.startswith(asset_types) for asset_types in FileManagement.asset_types_as_shown_per_section
        )

        # Check if the text line contains any item to remove
        line_contains_an_item_to_remove = any(item in text_line for item in items_to_remove)

        # Retain the line if it doesn't contain any item to remove, or it starts with the 'asset' string
        if not (line_contains_an_item_to_remove and not line_contains_asset_type):
            cleaned_text_lines.append(text_line)

    return cleaned_text_lines[1:]


def _extract_asset_data_from_text_lines(text_lines: List[str], asset: str) -> List[tuple]:
    """
    Extract asset data from a list of text lines.

    This function takes a list of text lines and extracts relevant data for a
    specific asset type. It identifies the asset symbol keyword, extracts the
    corresponding symbols, and processes the data lines accordingly.

    Note: Assumes that the input data has been previously validated for accuracy
    and consistency.

    :param text_lines: List of text lines to extract data from.
    :type text_lines: List[str]
    :param asset: The asset type for which to extract data.
    :type asset: str
    :return: List of tuples containing extracted asset data.
    :rtype: List[tuple]
    """
    # Get the asset symbol keyword
    asset_symbol_keyword = _symbol_corresponding_to_asset(asset)

    # Extract symbols and their indices
    symbols = [line.split(asset_symbol_keyword)[-1] for line in text_lines if asset_symbol_keyword in line]
    symbol_indices = [0] + [text_lines.index(line) - 1 for line in text_lines if asset_symbol_keyword in line]

    data_list = []

    # Iterate through symbol indices to extract data
    for idx in symbol_indices[:-1]:
        starting_index = idx + 2 if idx > 0 else idx
        data_range = slice(starting_index, starting_index + 6)
        selected_asset_data: List[str] = [x for x in text_lines[data_range]]

        # Check if the first element is numeric and exclude it if necessary
        if selected_asset_data[0].replace(",", "").replace(".", "").isdigit():
            selected_asset_data = selected_asset_data[1:]

        data_list.append(selected_asset_data)

    # Determine the number of columns based on asset type
    n_of_columns = 4 if FileManagement.asset_types_as_shown_per_section[asset] in [
        "Fixed Income", "Options", "Other Fixed Income"] else 3

    # Create tuples with symbols and extracted data
    data_list = [tuple([symbol] + data[:n_of_columns]) for symbol, data in zip(symbols, data_list.copy())]

    return data_list


@dataclass
class PDFScraper:
    """
    A class for extracting and processing investment data from PDF documents.

    This class provides methods to extract investment data from PDF documents,
    process the data, and convert it into pandas DataFrames for further analysis.
    It supports extracting data related to different asset types, such as equities,
    fixed income, exchange-traded funds (ETFs), and more.

    :param _pdf: A dictionary containing extracted text content from each page of a PDF document.
    """

    _pdf: Dict[int, list]
    _selected_statements_to_analyze: Dict[str, str]
    _list_of_fixed_income_etf: List[str]
    _currently_opened_statement: str = field(init=False)

    @property
    def selected_schwab_statements(self) -> Dict[str, str]:
        """
        Get the list of selected Schwab statements for analysis.

        This property returns a list of selected Schwab statement file names that have been chosen for analysis.
        These statements are typically the ones that match the specified criteria or time periods.

        :return: A list of selected Schwab statement file names.
        """
        return self._selected_statements_to_analyze

    @property
    def symbols_of_fixed_income_etfs(self) -> List[str]:
        return self._list_of_fixed_income_etf

    @property
    def currently_opened_statement(self) -> str:
        """
        Get the currently opened Schwab statement file.

        This property returns the file name of the currently opened Schwab statement. It allows you to
        identify which statement is currently being processed or analyzed.

        :return: The file name of the currently opened Schwab statement.
        """
        return self._currently_opened_statement

    @property
    def pdf(self):
        """
        Get the dictionary of extracted PDF content.

        :return: A dictionary where keys represent page numbers and values represent extracted text content.
        """
        return self._pdf

    @property
    def asset_composition(self) -> pd.DataFrame:
        """
        Get the DataFrame containing asset composition information.

        :return: A DataFrame containing asset composition data.
        """
        return self._asset_composition()

    @property
    def options_dataframe(self) -> pd.DataFrame:
        """
        Retrieve and convert options data from the PDF statement into a DataFrame.

        This property extracts options data from the PDF statement, converts it into a DataFrame, and returns it.
        The resulting DataFrame contains information about options, including columns like symbol,
        quantity, market value, etc.

        :return: A DataFrame containing options data.
        """
        return self._convert_generator_of_asset_data_to_dataframe(
            FileManagement.options, option_columns, option_numeric
        )


    @property
    def equity_dataframe(self) -> pd.DataFrame:
        """
        Get the DataFrame containing equity investment information.

        :return: A DataFrame containing equity investment data.
        """
        return self._convert_generator_of_asset_data_to_dataframe("Equities", equity_columns,
                                                                  equity_numeric)

    @property
    def bond_funds_dataframe(self) -> pd.DataFrame:
        """
        Get the DataFrame containing bond fund investment information.

        :return: A DataFrame containing equity investment data.
        """
        return self._convert_generator_of_asset_data_to_dataframe("Bond Funds", equity_columns, equity_numeric)

    @property
    def equity_funds_dataframe(self) -> pd.DataFrame:
        """
        Get the DataFrame containing equity fund investment information.

        :return: A DataFrame containing equity investment data.
        """

        return self._convert_generator_of_asset_data_to_dataframe("Equity Funds", equity_columns, equity_numeric)

    @property
    def exchange_traded_funds_dataframe(self) -> pd.DataFrame:
        """
        Get the DataFrame containing Exchange Traded Fund (ETF) investment information.

        :return: A DataFrame containing ETF investment data.
        """
        return self._convert_generator_of_asset_data_to_dataframe(
            "Exchange Traded Funds", equity_columns, equity_numeric)

    @property
    def other_assets_dataframe(self) -> pd.DataFrame:
        """
        Get a DataFrame containing information about other assets (e.g., ETFs) from the statements.

        :return: A pandas DataFrame containing information about other assets.
        """
        return self._convert_generator_of_asset_data_to_dataframe("Other Assets", equity_columns, equity_numeric)

    @property
    def money_market_fund_dataframe(self) -> pd.DataFrame:
        """
        Property to retrieve a DataFrame containing investment details for Money Market Funds.

        :return: A pandas DataFrame containing investment details for Money Market Funds.
        """
        return self._convert_generator_of_asset_data_to_dataframe("Fund Name", equity_columns, equity_numeric)

    @property
    def corporate_bonds_dataframe(self) -> pd.DataFrame:
        """
        Property to retrieve a DataFrame containing investment details for Corporate Bonds.

        :return: A pandas DataFrame containing investment details for Corporate Bonds.
        """
        return self._convert_generator_of_asset_data_to_dataframe(
            "Corporate Bonds", fixed_income_columns, fi_numeric
        )

    @property
    def bond_partial_calls(self) -> pd.DataFrame:
        """
        Retrieve a DataFrame containing information about bond partial calls.

        This property method extracts and processes data related to bond partial calls
        from the PDFScraper instance. It converts the extracted data into a pandas DataFrame
        and returns it.

        :return: A pandas DataFrame containing information about bond partial calls.
        :rtype: pd.DataFrame
        """
        return self._convert_generator_of_asset_data_to_dataframe(
            "Other Fixed Income", fixed_income_columns, fi_numeric
        )

    @property
    def treasuries_dataframe(self) -> pd.DataFrame:
        """
        Property to retrieve a DataFrame containing investment details for U.S. Treasuries.

        :return: A pandas DataFrame containing investment details for U.S. Treasuries.
        """
        return self._convert_generator_of_asset_data_to_dataframe(
            "U.S. Treasuries", fixed_income_columns, fi_numeric
        )

    def swap_statement(self, new_file_name: str) -> None:
        """
        Swap the PDF content with a new PDF file.

        This method replaces the current PDF content with the content of a new PDF file.
        It reads and extracts the text content from each page of the new PDF and updates the internal PDF dictionary.

        :param new_file_name: The name of the new PDF file.
        """
        # Read and extract text content from each page of the new PDF
        logging.info(f"Swapping PDF content with '{new_file_name}'...")
        new_pdf_content = _read_pdf(new_file_name)

        # Update the internal PDF dictionary with the new PDF content
        self._pdf = new_pdf_content
        self._currently_opened_statement = new_file_name
        logging.info(f"PDF content swapped with '{new_file_name}'.")

    def _asset_composition(self) -> pd.DataFrame:
        """
        Extracts the asset composition information from the PDF and returns it as a DataFrame.

        This method extracts the relevant section of asset composition information from the PDF,
        processes the data, and creates a DataFrame with columns for "Type" and "Market Value".

        :return: A pandas DataFrame containing asset composition data with columns "Type" and "Market Value".
        """
        logging.info("Extracting asset composition information from the PDF...")

        # Extract lines of text from the PDF and retrieve the relevant section
        text_lines: List[str] = self._asset_composition_text_lines()
        if text_lines is None:
            return pd.DataFrame()

        data_list = text_lines[text_lines.index("Asset Composition") + 3:text_lines.index("Total Assets Long")]

        # Group the data into rows of three elements each
        grouped_data = [data_list[i:i + 3] for i in range(0, len(data_list), 3)]

        # Create a DataFrame from the grouped data
        logging.debug("Creating DataFrame from the grouped data...")
        asset_composition = pd.DataFrame(grouped_data, columns=["Type", "Market Value", "% of Account Assets"])

        # Remove dollar signs and commas from "Market Value" and convert to float
        logging.debug("Cleaning up and transforming data...")
        translation_table = str.maketrans('', '', '$,')
        asset_composition["Market Value"] = asset_composition["Market Value"].str.translate(
            translation_table).astype(float)

        # Delete % of Account Assets column
        asset_composition = asset_composition.drop("% of Account Assets", axis=1)

        options_asset_name = "Options (Short)"
        if options_asset_name not in text_lines:
            return asset_composition

        market_value = text_lines[text_lines.index(options_asset_name):][1]
        shorts_dataframe = pd.DataFrame({"Type": [options_asset_name], "Market Value": [market_value]})

        shorts_dataframe["Market Value"] = shorts_dataframe["Market Value"].str.replace(",", "")
        shorts_dataframe["Market Value"] = shorts_dataframe["Market Value"].str.replace(
            r'\(([^)]+)\)', r'-\1', regex=True).astype(float)

        asset_composition = pd.concat([asset_composition, shorts_dataframe], ignore_index=True)

        logging.info("Asset composition information extracted and processed.")
        return asset_composition

    def _asset_composition_text_lines(self) -> Optional[List[str]]:
        """
        Extract the text lines containing asset composition information from the Schwab statement.

        This method searches through the first 5 pages of the Schwab statement to find the section
        that contains asset composition information. If found, it returns the list of text lines
        containing this information.

        :return: A list of text lines containing asset composition information if found, else None.
        """
        for page in range(1, 6):
            text_lines: List[str] = self.pdf[page]
            if "Asset Composition" in text_lines:
                return text_lines

        return None

    def _find_asset_section_in_statement(self, asset: str):
        """
        Find the start of the asset section in the PDF pages.

        This function searches for the start of the asset section within the PDF
        pages starting from a specified page number.

        :param asset: The asset type for which to find the section.
        :type asset: str
        :return: Generator that yields text lines of the section found on each page.
        """

        asset_name_as_shown_per_section = FileManagement.asset_types_as_shown_per_section[asset]
        partial_section_name = f"Investment Detail - {asset_name_as_shown_per_section}"

        for page_number in range(5, len(self.pdf)):
            pdf_page_lines: List[str] = self.pdf[page_number]

            for index, text_lines in enumerate(pdf_page_lines):
                if partial_section_name in text_lines:
                    yield _clean_text_lines_from_page(pdf_page_lines[index:], asset)
                    break

    def _convert_generator_of_asset_data_to_dataframe(self, asset: str, columns: List[str],
                                                      numeric_columns: List[str]) -> pd.DataFrame:
        """
        Convert a generator of asset data into a Pandas DataFrame.

        This function takes a generator of asset data sections, extracts the data,
        and converts it into a Pandas DataFrame.

        :param asset: The asset string to identify data sections.
        :type asset: str
        :param columns: List of column names for the DataFrame.
        :type columns: List[str]
        :param numeric_columns: List of column names to clean and convert to numeric type.
        :type numeric_columns: List[str]
        :return: A Pandas DataFrame containing the extracted asset data.
        :rtype: pd.DataFrame
        """
        asset_sections = self._find_asset_section_in_statement(asset)
        data_list = []

        # Iterate through the asset sections and extract data
        for text_lines in asset_sections:

            if text_lines is None:
                continue

            data_list += _extract_asset_data_from_text_lines(text_lines, asset)

        df = pd.DataFrame(data_list, columns=columns)

        # Clean up specified numeric columns by removing commas and converting to float
        for col in numeric_columns:
            df[col] = df[col].str.rstrip(' S')
            df[col] = df[col].str.replace(",", "")
            df[col] = df[col].str.replace(r'\(([^)]+)\)', r'-\1', regex=True).astype(float)

        return df

    def __post_init__(self):
        self._currently_opened_statement = self.selected_schwab_statements["Most Recent"]


# FileManagement.validate_statement_files(statement_folder_path=statements_directory_path)

_fixed_income_etfs = FileManagement.extract_fixed_income_etf_tickers()

_most_recent_file = _schwab_statement_paths["Most Recent"]
pdf_file_data: Dict[int, list] = _read_pdf(_most_recent_file)

pdf_scraper = PDFScraper(
    pdf_file_data,
    _schwab_statement_paths,
    _fixed_income_etfs
)
