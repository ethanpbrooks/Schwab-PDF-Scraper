import fitz
import os
import pandas as pd
import numpy as np

from dataclasses import dataclass
from typing import Dict, Optional, List

# _________________________Custom Modules_________________________
import PythonScripts.ScrapingScripts.TextProcessing as Tp
import PythonScripts.ScrapingScripts.TextExtraction as Te
import PythonScripts.ScrapingScripts.FileManagement as FileManagement


@dataclass
class PDFTextAnalyst:
    _pdf_file: Dict[int, str]

    def _find_asset_section_in_statement(self, asset: str, section_name: str):
        """
        Find the start of the asset section in the PDF pages.

        This function searches for the start of the asset section within the PDF
        pages starting from a specified page number.

        :param asset: The asset type for which to find the section.
        :type asset: str
        :return: Generator that yields text lines of the section found on each page.
        """

        for page_number in range(5, len(self._pdf_file)):
            pdf_page_text: str = self._pdf_file[page_number]
            if section_name in pdf_page_text:
                yield Tp.sort_asset_classes_from_text_lines(pdf_page_text, asset, section_name)

    def _search_item_in_pdf(self, item: str, lower: int, upper: int) -> Optional[str]:
        """
        Search for a specific item within the PDF text in a range of pages.

        :param item: The item to search for in the PDF text.
        :param lower: The lower page number to start the search.
        :param upper: The upper page number to end the search (inclusive).
        :return: The text containing the found item or None if not found.
        """
        for page in range(lower, upper + 1):
            page_text = self._pdf_file[page]
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

        text_lines: List[str] = Tp.sort_miscellaneous_values_from_text_lines(
            transactions_summary, "Cash Transactions Summary", "Ending Cash"
        )

        columns = ["Index", "This Period", "Year to Date"]

        # Skip the first three lines as they are headers
        return Tp.convert_text_lines_to_dataframe(text_lines[3:], columns, [])

    def _provided_asset_composition(self) -> Optional[pd.DataFrame]:
        """
        Extract and return the provided Asset Composition data from the PDF if available.

        :return: A Pandas DataFrame containing the Asset Composition data or None if not found.
        """
        asset_composition = self._search_item_in_pdf("Asset Composition", 3, 6)
        if asset_composition is None:
            return None

        text_lines: List[str] = Tp.sort_miscellaneous_values_from_text_lines(
            asset_composition, "Asset Composition", "Total Assets Long"
        )

        columns = ["Index", "Market Value", "% of Account Assets"]

        # Skip the first three lines as they are headers and delete the last column
        return Tp.convert_text_lines_to_dataframe(text_lines[3:], columns, []).drop(columns[-1], axis=1)

    def _change_in_account_value(self) -> pd.DataFrame:
        change_in_account_value = self._search_item_in_pdf("Change in Account Value", 3, 6)

        text_lines: List[str] = Tp.sort_miscellaneous_values_from_text_lines(
            change_in_account_value, "Change in Account Value", "Accrued Income"
        )

        columns = ["Index", "This Period", "Year to Date"]

        # Skip the first three lines as they are headers and delete the last column
        return Tp.convert_text_lines_to_dataframe(text_lines[3:], columns, []).drop(columns[-1], axis=1)

    def convert_generator_of_transaction_data_to_dataframe(self, transaction: str):
        """
        Convert a generator of transaction data into a DataFrame.

        This method takes a generator of transaction data and converts it into a structured DataFrame with specified
        columns.

        :param transaction: A string containing transaction data.
        :return: A DataFrame containing transaction details.
        """
        # Define the section name to locate in the statement
        section_name = "Transaction Detail - Purchases & Sales"

        # Find the sections in the statement that match the section name
        transaction_sections = self._find_asset_section_in_statement(transaction, section_name)

        # Define the columns and non-numeric columns
        columns = [
            "Settle Date", "Trade Date", "Description", "Name", "Symbol", "Quantity", "Unit Price",
            "Charges and Interest", "Total Amount"
        ]
        non_numeric_columns = ["Settle Date", "Trade Date", "Description", "Name", "Symbol"]

        # Initialize an empty DataFrame to store transaction data
        transactions_dataframe = pd.DataFrame()

        # Iterate through the transaction sections and process the data
        for transaction_details in transaction_sections:
            if transaction_details is None:
                continue

            # Sort and process text lines within the transaction details
            sorted_text_lines = Tp.sort_transactions_from_text_lines(transaction_details)

            # Convert sorted text lines to a DataFrame
            retrieved_dataframe = Tp.convert_text_lines_to_dataframe(sorted_text_lines, columns, non_numeric_columns)

            # Concatenate the retrieved DataFrame to the main DataFrame
            transactions_dataframe = pd.concat([transactions_dataframe, retrieved_dataframe], axis=0)

        # Reset the index of the resulting DataFrame
        transactions_dataframe = transactions_dataframe.reset_index()

        return transactions_dataframe

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
        asset_name_as_shown_per_section = FileManagement.asset_types_as_shown_per_section[asset]
        partial_section_name = f"Investment Detail - {asset_name_as_shown_per_section}"

        asset_sections = self._find_asset_section_in_statement(asset, partial_section_name)
        data_list = []

        # Iterate through the asset sections and extract data
        for text_lines in asset_sections:
            if text_lines is None:
                continue

            data_list += Te.extract_asset_data_from_text_lines(text_lines, asset)

        df = pd.DataFrame(data_list, columns=columns)

        # Clean up specified numeric columns by removing commas and converting to float
        Tp.convert_values_from_columns_to_numeric(df, numeric_columns, [])

        return df

