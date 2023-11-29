from dataclasses import dataclass
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Callable, Any

import pandas as pd

from PythonScripts.ScrapingScripts.PDFScraper import PDFScraper, pdf_scraper


# ____________________ Time Periods ____________________
_THREE_MONTH = 3
_ONE_YEAR = 12
_THREE_YEAR = 12 * 3
_FIVE_YEAR = 12 * 5

_STANDARD_PERIODS_LIST = ["3 Month", "Year to Date", "1 Year", "3 Year", "5 Year"]


# ____________________ Functions ____________________

def _most_recent_period(statement_path: str) -> datetime:
    """
    Get the most recent period from the statement path.

    :param statement_path: Path of the statement in the format "YYYY-B.pdf".
    :return: datetime object representing the most recent period.
    """
    date = datetime.strptime(
        statement_path.split(".")[0],
        "%Y-%B"
    )
    return date


def _months_to_subtract(statement_path: str) -> List[int]:
    """
    Calculate the number of months to subtract for standard periods.

    :param statement_path: Path of the statement in the format "YYYY-B.pdf".
    :return: List of months to subtract for standard periods.
    """
    year_to_date = _most_recent_period(statement_path).month
    return [_THREE_MONTH, year_to_date, _ONE_YEAR, _THREE_YEAR, _FIVE_YEAR]


def _schwab_statements_to_iterate(statement_path: str) -> Dict[str, str]:
    """
    Generate a dictionary of Schwab statement paths and corresponding dates for standard periods.

    :param statement_path: Path of the statement in the format "YYYY-B.pdf".
    :return: Dictionary with Schwab statement paths and dates.
    """
    statement_data = {}
    for months, periods in zip(_months_to_subtract(statement_path), _STANDARD_PERIODS_LIST):
        date = (_most_recent_period(statement_path) - relativedelta(months=months)).strftime("%Y-%B")
        pdf_path = f"{date}.pdf"
        statement_data[pdf_path] = periods

    return statement_data


def _months_to_iterate(statement_path: str, add_additional_month: bool):
    """
    Generate a dictionary of Schwab statement paths and corresponding dates for custom periods.

    :param statement_path: Path of the statement in the format "YYYY-B.pdf".
    :param add_additional_month: Boolean flag to add another month.
    :return: Dictionary with Schwab statement paths and dates.
    """
    additional_months = 2 if add_additional_month else 1
    statement_data = {}

    for month_range in range(_FIVE_YEAR + additional_months):
        date = (_most_recent_period(statement_path) - relativedelta(months=month_range)).strftime("%Y-%B")
        pdf_path = f"{date}.pdf"
        statement_data[pdf_path] = date

    return statement_data


# ____________________ Dataclass ____________________
@dataclass
class FinancialAnalyst:
    """
    A dataclass representing a Financial Analyst that extends the PDFScraper class.

    This class provides decorators for iterating through Schwab statements and performing calculations.
    """

    pdf_scraper: PDFScraper

    # _______________ Decorators _______________
    def decorator_standard_iteration(self, calculation: Callable[..., Any]):
        """
        A decorator for standard iteration through Schwab statements.

        This decorator swaps Schwab statements for standard periods, performs calculations, and returns a DataFrame.

        :param calculation: The calculation function to be applied to each statement.
        :return: Wrapper function for standard iteration.
        """
        def wrapper():
            dataframe = pd.DataFrame()
            iterator = _schwab_statements_to_iterate(
                self.pdf_scraper.currently_opened_statement
            ).copy().items()

            for pdf_path, statement_date in iterator:
                self.pdf_scraper.swap_statement(pdf_path)
                dataframe[statement_date] = calculation()

            return dataframe

        return wrapper()

    def decorator_monthly_iteration(self, calculation: Callable[..., Any], add_additional_month: bool):
        """
        A decorator for monthly iteration through Schwab statements.

        This decorator swaps Schwab statements for custom periods, performs calculations, and returns a DataFrame.

        :param calculation: The calculation function to be applied to each statement.
        :param add_additional_month: Boolean flag to add another month.
        :return: Wrapper function for monthly iteration.
        """
        def wrapper():
            dataframe = pd.DataFrame()
            iterator = _months_to_iterate(
                self.pdf_scraper.currently_opened_statement, add_additional_month
            ).copy().items()

            for path, month in iterator:
                self.pdf_scraper.swap_statement(path)
                dataframe[month] = calculation()

            return dataframe

        return wrapper()

    def decorator_custom_iteration(self, calculation: Callable[..., Any], add_additional_month: bool, columns: list):
        """
        A decorator for custom iteration through Schwab statements with specified columns.

        This decorator swaps Schwab statements for custom periods, performs calculations, and returns a DataFrame with
        specified columns.

        :param calculation: The calculation function to be applied to each statement.
        :param add_additional_month: Boolean flag to add another month.
        :param columns: List of columns for the resulting DataFrame.
        :return: Wrapper function for custom iteration with specified columns.
        """
        def wrapper():
            retrieved_data = []
            iterator = _months_to_iterate(self.pdf_scraper.currently_opened_statement, add_additional_month).copy()

            for path, month in iterator.items():
                self.pdf_scraper.swap_statement(path)
                retrieved_data.append(calculation())

            dataframe = pd.DataFrame(retrieved_data, columns=columns, index=iterator.values())
            return dataframe

        return wrapper()


financial_analyst = FinancialAnalyst(pdf_scraper=pdf_scraper)
