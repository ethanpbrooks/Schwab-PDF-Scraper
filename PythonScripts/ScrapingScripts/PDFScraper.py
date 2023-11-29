import fitz
import os
import pandas as pd

from dataclasses import dataclass, field
from typing import List, Dict, Callable, Any

from datetime import datetime
from dateutil.relativedelta import relativedelta

# _________________________Custom Modules_________________________
import PythonScripts.ScrapingScripts.FileManagement as FileManagement

from PythonScripts.ScrapingScripts.PDFTextAnalyst import PDFTextAnalyst


# Dataframe columns
equity_columns = ["Symbol", "Name", "Quantity", "Price"]
equity_numeric = ["Quantity", "Price"]

option_columns = ["Symbol", "Name", "Quantity", "Price", "Market Value"]
option_numeric = ["Quantity", "Price", "Market Value"]

fixed_income_columns = ["CUSIP", "Name", "Par", "Market Price", "Market Value"]
fi_numeric = ["Par", "Market Price", "Market Value"]


# _________________________Read from PDF_________________________
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


@dataclass
class PDFScraper(PDFTextAnalyst):
    """
    A class for extracting and processing investment data from PDF documents.

    This class provides methods to extract investment data from PDF documents,
    process the data, and convert it into pandas DataFrames for further analysis.
    It supports extracting data related to different asset types, such as stocks,
    fixed income, exchange-traded funds (ETFs), and more.

    """

    _currently_opened_statement: str = field(init=False)

    # _________________________Properties_________________________
    @property
    def symbols_of_fixed_income_etfs(self) -> List[str]:
        return FileManagement.extract_fixed_income_etf_tickers()

    @property
    def currently_opened_statement(self) -> str:
        """
        Get the currently opened Schwab statement file.

        This property performance the file name of the currently opened Schwab statement. It allows you to
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
        return self._pdf_file

    # _________________________Asset Class Getters_________________________
    @property
    def scraped_options(self) -> pd.DataFrame:
        """
        Retrieve and convert options data from the PDF statement into a DataFrame.

        This property extracts options data from the PDF statement, converts it into a DataFrame, and performance it.
        The resulting DataFrame contains information about options, including columns like symbol,
        quantity, market value, etc.

        :return: A DataFrame containing options data.
        """
        return self._convert_generator_of_asset_data_to_dataframe(
            "Options", option_columns, option_numeric
        )

    @property
    def scraped_stocks(self) -> pd.DataFrame:
        """
        Get the DataFrame containing equity investment information.

        :return: A DataFrame containing equity investment data.
        """
        return self._convert_generator_of_asset_data_to_dataframe("Equities", equity_columns,
                                                                  equity_numeric)

    @property
    def scraped_bond_funds(self) -> pd.DataFrame:
        """
        Get the DataFrame containing bond fund investment information.

        :return: A DataFrame containing equity investment data.
        """
        return self._convert_generator_of_asset_data_to_dataframe("Bond Funds", equity_columns, equity_numeric)

    @property
    def scraped_equity_funds(self) -> pd.DataFrame:
        """
        Get the DataFrame containing equity fund investment information.

        :return: A DataFrame containing equity investment data.
        """

        return self._convert_generator_of_asset_data_to_dataframe("Equity Funds", equity_columns, equity_numeric)

    @property
    def scraped_exchange_traded_funds(self) -> pd.DataFrame:
        """
        Get the DataFrame containing Exchange Traded Fund (ETF) investment information.

        :return: A DataFrame containing ETF investment data.
        """
        return self._convert_generator_of_asset_data_to_dataframe(
            "Exchange Traded Funds", equity_columns, equity_numeric)

    @property
    def scraped_other_assets(self) -> pd.DataFrame:
        """
        Get a DataFrame containing information about other assets (e.g., ETFs) from the statements.

        :return: A pandas DataFrame containing information about other assets.
        """
        return self._convert_generator_of_asset_data_to_dataframe("Other Assets", equity_columns, equity_numeric)

    @property
    def scraped_money_market_funds(self) -> pd.DataFrame:
        """
        Property to retrieve a DataFrame containing investment details for Money Market Funds.

        :return: A pandas DataFrame containing investment details for Money Market Funds.
        """
        return self._convert_generator_of_asset_data_to_dataframe("Fund Name", equity_columns, equity_numeric)

    @property
    def scraped_corporate_bonds(self) -> pd.DataFrame:
        """
        Property to retrieve a DataFrame containing investment details for Corporate Bonds.

        :return: A pandas DataFrame containing investment details for Corporate Bonds.
        """
        return self._convert_generator_of_asset_data_to_dataframe(
            "Corporate Bonds", fixed_income_columns, fi_numeric
        )

    @property
    def scraped_bond_partial_calls(self) -> pd.DataFrame:
        """
        Retrieve a DataFrame containing information about bond partial calls.

        This property method extracts and processes data related to bond partial calls
        from the PDFScraper instance. It converts the extracted data into a pandas DataFrame
        and performance it.

        :return: A pandas DataFrame containing information about bond partial calls.
        :rtype: pd.DataFrame
        """
        return self._convert_generator_of_asset_data_to_dataframe(
            "Other Fixed Income", fixed_income_columns, fi_numeric
        )

    @property
    def scraped_treasuries(self) -> pd.DataFrame:
        """
        Property to retrieve a DataFrame containing investment details for U.S. Treasuries.

        :return: A pandas DataFrame containing investment details for U.S. Treasuries.
        """
        return self._convert_generator_of_asset_data_to_dataframe(
            "U.S. Treasuries", fixed_income_columns, fi_numeric
        )

    # _________________________Additional Data Getters_________________________
    @property
    def scraped_cash_transactions(self) -> float:
        try:
            return self.scraped_cash_transaction_summary["This Period"].loc["Total Cash Transaction Detail"]
        except KeyError:
            return self.scraped_cash_transaction_summary["This Period"].loc["Total Transaction Detail"]

    @property
    def scraped_cash_transaction_summary(self):
        """
        Get a summary DataFrame of cash transactions for the portfolio.

        This property retrieves and performance a summary DataFrame of cash transactions for the portfolio, which can
        provide insights into the cash flow activity within the portfolio.

        :return: A DataFrame summarizing cash transactions.
        """
        return self._cash_transaction_summary()

    @property
    def change_in_account_value(self) -> pd.DataFrame:
        """
        Get a DataFrame showing changes in the account's value.

        This property retrieves and performance a DataFrame that shows the changes in the account's value over time.
        It can be useful for tracking the performance and fluctuations of the portfolio.

        :return: A DataFrame with changes in account value.
        """
        return self._change_in_account_value()

    @property
    def account_value(self):
        """
        Get the total value of the account for the current period.

        :return: Total account value for the current period.
        """
        return self.change_in_account_value["This Period"][-1]

    @property
    def year_to_date_numerical_value(self) -> float:
        return datetime.strptime(self.currently_opened_statement.split(".")[0], "%Y-%B").month

    @property
    def asset_composition(self) -> pd.DataFrame:
        """
        Get the DataFrame containing asset assets information.

        :return: A DataFrame containing asset assets data.
        """
        return self._provided_asset_composition()

    # _________________________Decorators_________________________
    def standard_iterator(self, func: Callable[..., Any]) -> pd.DataFrame:
        # Convert the input string to a datetime object
        start_date = datetime.strptime(
            self._currently_opened_statement.split(".")[0],
            "%Y-%B"
        )

        months_to_subtract = [3, start_date.month, 12, 12 * 3, 12 * 5]
        periods = ["3 Month", "Year to Date", "1 Year", "3 Year", "5 Year"]

        schwab_statements = {}
        for months, period in zip(months_to_subtract, periods):
            statement_date = (start_date - relativedelta(months=months)).strftime("%Y-%B")
            statement_path = f"{statement_date}.pdf"

            schwab_statements[statement_path] = period

        def wrapper():
            dataframe = pd.DataFrame()
            for path, statement_period in schwab_statements.items():
                self.swap_statement(path)
                dataframe[statement_period] = func()

            return dataframe

        self.revert_to_original_pdf_file()
        return wrapper()

    def monthly_iterator(self, func: Callable[..., Any], add_additional_month: bool):
        # Convert the input string to a datetime object
        start_date = datetime.strptime(
            self._currently_opened_statement.split(".")[0],
            "%Y-%B"
        )

        schwab_statements = {}
        additional_months = 2 if add_additional_month else 1

        for months in range((12 * 5) + additional_months):
            statement_date = (start_date - relativedelta(months=months)).strftime("%Y-%B")
            statement_path = f"{statement_date}.pdf"

            schwab_statements[statement_path] = statement_date

        def wrapper():
            dataframe = pd.DataFrame()
            for path, month in schwab_statements.items():
                self.swap_statement(path)
                dataframe[month] = func()

            return dataframe

        return wrapper()

    def monthly_iterator_multi_column_frame(
            self, func: Callable[..., Any], add_additional_month: bool, columns: List[str]):

        # Convert the input string to a datetime object
        start_date = datetime.strptime(
            self._currently_opened_statement.split(".")[0],
            "%Y-%B"
        )

        additional_months = 2 if add_additional_month else 1
        schwab_statements = {}

        for months in range((12 * 5) + additional_months):
            statement_date = (start_date - relativedelta(months=months)).strftime("%Y-%B")
            statement_path = f"{statement_date}.pdf"

            schwab_statements[statement_path] = statement_date

        def wrapper():
            retrieved_data = []

            for path, month in schwab_statements.items():
                self.swap_statement(path)
                retrieved_data.append(func())

            dataframe = pd.DataFrame(retrieved_data, columns=columns, index=schwab_statements.values())

            return dataframe

        return wrapper()

    # _________________________Class Methods_________________________
    def revert_to_original_pdf_file(self):
        self.swap_statement(FileManagement.extract_schwab_statements())

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
        self._pdf_file = new_pdf_content
        self._currently_opened_statement = new_file_name

    def __post_init__(self):
        self._currently_opened_statement = FileManagement.extract_schwab_statements()


# FileManagement.validate_statement_files(statement_folder_path=statements_directory_path)

pdf_file_data: Dict[int, str] = _read_pdf(FileManagement.extract_schwab_statements())

pdf_scraper = PDFScraper(
    _pdf_file=pdf_file_data,
)
