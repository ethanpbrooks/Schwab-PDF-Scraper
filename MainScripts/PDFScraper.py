import fitz
import os
import pandas as pd
import MainScripts.FileManagement as FileManagement

from dataclasses import dataclass, field
from typing import List, Optional, Dict


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


def _read_pdf(pdf_name: str) -> Dict[int, str]:
    """
    Extracts and splits text content from each page_number of a PDF document.

    This method reads a PDF file, extracts the text content from each page_number, and splits the text into lines.

    :param pdf_name: The name of the PDF file.
    :return: A dictionary where the keys represent page_number numbers and the values represent the extracted and
             split text content from each page_number.
    :raises FileNotFoundError: If the specified PDF file is not found in the folder.
    """

    pdf_path = os.path.join(FileManagement.statement_directory_path, pdf_name)

    # Check if the PDF file exists
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"File {pdf_name} was not found in the folder.")

    # Initialize an empty dictionary to store extracted and split text content
    extracted_pages = {}

    # Open the PDF document using fitz
    with fitz.Document(pdf_path) as file:
        # Iterate through each page_number in the PDF document
        for page_number in file:

            # Extract text content from the current page_number and split it into lines
            text_lines = page_number.get_textpage().extractText()
            extracted_pages[page_number.number + 1] = text_lines

    return extracted_pages


def _convert_columns_to_numeric(df: pd.DataFrame, columns: List[str]) -> None:
    """
    Clean and convert specified columns in a Pandas DataFrame to numeric format.

    This function processes the values in the specified columns, removing trailing ' S', commas, and '$ ' from the
    values. Additionally, it handles negative values enclosed in parentheses, converting them to their negative
    numeric counterparts.

    :param df: The Pandas DataFrame to process.
    :type df: pd.DataFrame
    :param columns: A list of column names in the DataFrame to clean and convert.
    :type columns: List[str]
    """
    # Define a custom function to clean and convert values
    def clean_and_convert(value):
        value = str(value)
        value = value.rstrip(' S').replace(",", "").replace("$ ", "")
        value = value.replace("<", "").replace("%", "")
        if value.startswith('(') and value.endswith(')'):
            return -float(value[1:-1])

        return float(value)

    # Apply the custom function to the specified columns
    df[columns] = df[columns].applymap(clean_and_convert)


def _text_lines_to_dataframe(text_lines: List[str], columns: List[str]) -> pd.DataFrame:
    """
    Transform a list of text lines into a Pandas DataFrame with specified columns.

    This function takes a list of text lines and organizes the data into columns as per the specified column names.
    It also applies the _convert_columns_to_numeric function to clean and convert the values in the DataFrame.

    :param text_lines: A list of text lines to be transformed into a DataFrame.
    :type text_lines: List[str]
    :param columns: A list of column names to organize the data.
    :type columns: List[str]

    :return: A Pandas DataFrame with data organized into the specified columns.
    :rtype: pd.DataFrame
    """
    n_columns = len(columns)
    data = {col: [] for col in columns}

    for index, line in enumerate(text_lines):
        column_index = columns[index % n_columns]
        data[column_index].append(line)

    dataframe = pd.DataFrame(data).set_index(columns[0])
    _convert_columns_to_numeric(dataframe, columns[1:])

    return dataframe


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


def _sorted_miscellaneous_text_lines(page_text: str, start: str, end: str) -> List[str]:
    """
    Extract and clean text lines related to cash transactions summary from a PDF page.

    :param page_text: Text content of a PDF page.
    :return: A list of cleaned and processed text lines related to cash transactions summary.
    """

    # Extract the relevant section based on the start and end points
    section_text = page_text[page_text.index(start):page_text.index(end)]

    # Split the section into lines and remove empty or whitespace-only lines
    text_lines = [line.strip() for line in section_text.split("\n") if line.strip()]

    return text_lines


def _sorted_asset_class_text_lines(page_text: str, asset: str, partial_section_name: str) -> Optional[List[str]]:
    """
    Extract and process the text lines related to a specific asset from a PDF page.

    :param page_text: Text content of a PDF page.
    :param asset: The asset type to extract.
    :param partial_section_name: The partial name of the asset section.
    :return: A list of cleaned and processed text lines related to the asset, or None if the asset is not found.
    """

    asset_page_data = page_text

    # Check if the asset is present on the page
    if asset not in asset_page_data:
        return None

    # Remove text after the end of the asset section
    end_of_section = f"Total {asset}"
    if end_of_section in asset_page_data:
        page_text = asset_page_data[:asset_page_data.index(end_of_section)]

    # Find the start of the asset section
    first_start_of_section_index = asset_page_data.index(partial_section_name) + len(partial_section_name) + 1
    asset_page_data = page_text[first_start_of_section_index:]

    if asset not in asset_page_data:
        return None

    second_start_of_section_index = asset_page_data.index(asset) + len(asset) + 1
    asset_page_data = asset_page_data[second_start_of_section_index:]

    # Get line items to remove from the config
    line_items_to_remove = FileManagement.config["Line Items to Remove"] + ["(continued)", "[Non-Sweep]"]

    # Process and clean the text lines
    reduced_text_lines = [line.strip() for line in asset_page_data.split("\n") if not line.startswith(
        tuple(line_items_to_remove)) and line]

    return reduced_text_lines


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
    It supports extracting data related to different asset types, such as stocks,
    fixed income, exchange-traded funds (ETFs), and more.

    :param _pdf: A dictionary containing extracted text content from each page of a PDF document.
    """

    _pdf: Dict[int, str]
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
        return self._provided_asset_composition()

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
            "Options", option_columns, option_numeric
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

    @property
    def cash_transaction_summary_dataframe(self):
        return self._cash_transaction_summary()

    def revert_to_original_pdf_file(self):
        self.swap_statement(self.selected_schwab_statements["Most Recent"])

    def swap_statement(self, new_file_name: str) -> None:
        """
        Swap the PDF content with a new PDF file.

        This method replaces the current PDF content with the content of a new PDF file.
        It reads and extracts the text content from each page of the new PDF and updates the internal PDF dictionary.

        :param new_file_name: The name of the new PDF file.
        """
        # Read and extract text content from each page of the new PDF
        new_pdf_content = _read_pdf(new_file_name)

        # Update the internal PDF dictionary with the new PDF content
        self._pdf = new_pdf_content
        self._currently_opened_statement = new_file_name

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
            pdf_page_text: str = self.pdf[page_number]
            if partial_section_name in pdf_page_text:
                yield _sorted_asset_class_text_lines(pdf_page_text, asset, partial_section_name)

    def _search_item_in_pdf(self, item: str, lower: int, upper: int) -> Optional[str]:
        """
        Search for a specific item within the PDF text in a range of pages.

        :param item: The item to search for in the PDF text.
        :param lower: The lower page number to start the search.
        :param upper: The upper page number to end the search (inclusive).
        :return: The text containing the found item or None if not found.
        """
        for page in range(lower, upper + 1):
            page_text = self.pdf[page]
            if item in page_text:
                return page_text

        return None

    def _cash_transaction_summary(self) -> Optional[pd.DataFrame]:
        """
        Extract and return the Cash Transaction Summary data from the PDF if available.

        :return: A Pandas DataFrame containing the Cash Transaction Summary or None if not found.
        """
        transactions_summary = self._search_item_in_pdf("Cash Transactions Summary", 4, 8)
        if transactions_summary is None:
            return None

        text_lines: List[str] = _sorted_miscellaneous_text_lines(
            transactions_summary, "Cash Transactions Summary","Ending Cash"
        )

        columns = ["Index", "This Period", "Year to Date"]

        # Skip the first three lines as they are headers
        return _text_lines_to_dataframe(text_lines[3:], columns)

    def _provided_asset_composition(self) -> Optional[pd.DataFrame]:
        """
        Extract and return the provided Asset Composition data from the PDF if available.

        :return: A Pandas DataFrame containing the Asset Composition data or None if not found.
        """
        asset_composition = self._search_item_in_pdf("Asset Composition", 3, 6)
        if asset_composition is None:
            return None

        text_lines: List[str] = _sorted_miscellaneous_text_lines(
            asset_composition, "Asset Composition", "Total Assets Long"
        )

        columns = ["Index", "Market Value", "% of Account Assets"]

        # Skip the first three lines as they are headers and delete the last column
        return _text_lines_to_dataframe(text_lines[3:], columns).drop(columns[-1], axis=1)

    def change_in_account_value(self) -> Optional[pd.DataFrame]:
        change_in_account_value = self._search_item_in_pdf("Change in Account Value", 3, 6)
        if change_in_account_value is None:
            return None

        text_lines: List[str] = _sorted_miscellaneous_text_lines(
            change_in_account_value, "Change in Account Value", "Accrued Income"
        )

        columns = ["Index", "This Period", "Year to Date"]

        # Skip the first three lines as they are headers and delete the last column
        return _text_lines_to_dataframe(text_lines[3:], columns).drop(columns[-1], axis=1)

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
        _convert_columns_to_numeric(df, numeric_columns)

        return df

    def __post_init__(self):
        self._currently_opened_statement = self.selected_schwab_statements["Most Recent"]


# FileManagement.validate_statement_files(statement_folder_path=statements_directory_path)

_fixed_income_etfs = FileManagement.extract_fixed_income_etf_tickers()

_most_recent_file = _schwab_statement_paths["Most Recent"]
pdf_file_data: Dict[int, str] = _read_pdf(_most_recent_file)

pdf_scraper = PDFScraper(
    pdf_file_data,
    _schwab_statement_paths,
    _fixed_income_etfs
)
