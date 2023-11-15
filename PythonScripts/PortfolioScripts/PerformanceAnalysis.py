from PythonScripts.ScrapingScripts.PDFScraper import PDFScraper, pdf_scraper

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np
import pandas as pd


@dataclass
class PerformanceAnalysis:
    """
    A class for calculating and managing performance on investments.

    This class provides methods to calculate time-weighted performance based on the provided financial data.

    :param pdf_scraper: An instance of PythonScripts.PDFScraper for extracting financial data.
    """

    pdf_scraper: PDFScraper

    @property
    def time_weighted_returns(self) -> pd.DataFrame:
        """
        Calculate time-weighted performance for various time periods.

        :return: DataFrame with time-weighted performance for different time periods.
        """

        return self._calculate_time_weighted_returns()

    @property
    def standard_deviation(self):
        return self._calculate_variance_and_standard_deviation()

    @property
    def risk_measures(self):
        return self._calculate_risk_measures()

    # ____________________Calculations____________________
    @staticmethod
    def calculate_month_range(start_date, num_months):
        """
        Calculate a range of month-year strings given a start date and a number of months.

        :param start_date: A string representing the start date in the format "YYYY-B".
        :param num_months: The number of months to calculate.
        :return: A list of month-year strings.
        """

        # Convert the input string to a datetime object
        start_date = datetime.strptime(start_date, "%Y-%B")

        # Create an empty list to store the result
        result = []

        # Subtract months and add them to the result list
        for _ in range(num_months + 1):
            result.append(start_date.strftime("%Y-%B"))
            # Subtract one month (approximately 30 days)
            start_date = start_date - timedelta(days=30)

        return result

    def _calculate_schwab_statement_paths(self, num_months: int) -> List[str]:
        """
        Calculate Schwab statement file dates for a specified number of months.

        :param num_months: The number of months for which statement paths are calculated.
        :return: A list of file date strings.
        """

        # Get the start date from the currently opened statement's file name.
        start_date: str = self.pdf_scraper.currently_opened_statement.split(".")[0]

        # Calculate a list of file dates by subtracting the specified number of months.
        statement_paths: List[str] = self.calculate_month_range(start_date, num_months)

        return statement_paths

    def _calculate_gross_returns(self):
        """
        Calculate gross performance for various time periods.

        :return: A DataFrame with gross performance.
        """

        # Define the items to be included in the account summary
        account_items = ["Period", "Ending Value", "Starting Value", "Cash Flow"]
        account_summary: Dict[str, List] = {k: [] for k in account_items}

        # Get Schwab statement dates for the specified number of months
        num_months = 12 * 5
        schwab_statement_dates = self._calculate_schwab_statement_paths(num_months)

        def insert_data_to_dict(date: str, account_values: pd.DataFrame, deposits: pd.DataFrame):
            # Calculate account value and cash flow
            ending_account_value = account_values.iloc[-1]
            starting_account_value = account_values.loc["Starting Value"]

            data_list = [date, ending_account_value, starting_account_value, deposits]

            for item, data in zip(account_items, data_list):
                account_summary[item].append(data)

        for statement_date in schwab_statement_dates:
            # Swap statement, calculate changes, and insert data into the summary
            self.pdf_scraper.swap_statement(f"{statement_date}.pdf")

            account_value_changes = self.pdf_scraper.change_in_account_value["This Period"]

            cash_deposit_column = "Deposits and other Cash Credits"
            cash_deposits = self.pdf_scraper.cash_transaction_summary["This Period"].loc[cash_deposit_column]

            insert_data_to_dict(statement_date, account_value_changes, cash_deposits)

        # Revert to the original PDF file
        self.pdf_scraper.revert_to_original_pdf_file()

        account_summary["Cash Flow"][-1] = 0

        # Create a DataFrame from the account summary
        account_summary: pd.DataFrame = pd.DataFrame(account_summary)

        # Calculate the "Adjusted Starting Value"
        account_summary["Starting Value after Cash Flow"] = (account_summary["Starting Value"]
                                                             + account_summary["Cash Flow"])

        adjusted_beginning_value = account_summary["Starting Value after Cash Flow"]
        ending_value = account_summary["Ending Value"]

        # Calculate the internal rate of return
        account_summary["Gross Returns"] = ending_value / adjusted_beginning_value

        return account_summary["Gross Returns"]

    def _calculate_time_weighted_returns(self) -> pd.DataFrame:
        """
        Calculate time-weighted performance for various time periods.

        :return: DataFrame with time-weighted performance for different time periods.
        """

        # Calculate internal rates of tw_returns
        gross_returns = self._calculate_gross_returns()

        # Define the time periods and corresponding column names
        quarter, one_year, three_year, five_year = 3, 12, 12 * 3, 12 * 5
        year_to_date = datetime.strptime(self.pdf_scraper.currently_opened_statement, "%Y-%B.pdf").month
        periods = [quarter, year_to_date, one_year, three_year, five_year]
        columns = ["Three Month", "Year to Date", "One Year", "Three Year", "Five Year"]

        # Calculate time-weighted tw_returns for each time period
        tw_returns = [gross_returns.head(n).prod() - 1 for n in periods]

        # Create a DataFrame with the time-weighted tw_returns
        time_weighted_returns = pd.DataFrame(
            {c: [twr] for (c, twr) in zip(columns, tw_returns)}, index=["Time Weighted Returns"]
        ).transpose()

        # Convert the results to percentages rounded to two decimal places
        return np.round(time_weighted_returns * 100, 2)

    def _calculate_historical_account_values(self, num_months: int) -> pd.DataFrame:
        """
        Retrieve historical account values for a specified number of months.

        This method gathers historical account values by swapping Schwab statements to the corresponding dates and
        extracting the account value for each date.

        :param num_months: The number of months for which historical account values should be collected.
        :return: A DataFrame containing historical account values, indexed by file dates.
        """
        schwab_statement_paths = self._calculate_schwab_statement_paths(num_months)

        # Iterate through the file dates to gather historical data.
        historical_values: Dict[str, list] = {}
        for date in schwab_statement_paths:
            # Swap the statement to the corresponding date.
            self.pdf_scraper.swap_statement(f"{date}.pdf")
            historical_values[date] = [self.pdf_scraper.account_value]

        historical_values: pd.DataFrame = pd.DataFrame(historical_values).transpose().rename(
            columns={0: "Account Value"})[::-1]

        return historical_values

    def _calculate_variance_and_standard_deviation(self):
        """
        Calculate risk measurements, including variance, standard deviation, and annualized standard deviation.

        This method calculates risk measurements based on historical percentage performance over various time periods.

        :return: A DataFrame containing risk measurements.
        """
        # Calculate historical percentage performance over the specified time period
        quarter, one_year, three_year, five_year = 3, 12, 12 * 3, 12 * 5

        historical_percentage_returns = self._calculate_historical_account_values(five_year).pct_change()
        year_to_date = datetime.strptime(historical_percentage_returns.index[-1], "%Y-%B").month

        # Define the time periods and corresponding column names
        periods = [quarter, year_to_date, one_year, three_year, five_year]
        columns = ["Three Month", "Year to Date", "One Year", "Three Year", "Five Year"]

        # Calculate variances for each time period
        variances = [historical_percentage_returns.tail(n).var()["Account Value"] for n in periods]

        # Create a DataFrame to store risk measurements
        risk_measurements = pd.DataFrame({c: [v] for (c, v) in zip(columns, variances)}, index=["Variance"]).transpose()
        risk_measurements["Standard Deviation"] = np.sqrt(risk_measurements["Variance"])
        risk_measurements["Annualized Standard Deviation"] = risk_measurements["Standard Deviation"] * np.sqrt(12)

        # Round the values to two decimal places and express as percentages
        risk_measurements: pd.DataFrame = np.round(risk_measurements * 100, 2)

        self.pdf_scraper.revert_to_original_pdf_file()

        return risk_measurements

    def _calculate_risk_measures(self) -> pd.DataFrame:
        """
        Generate a portfolio report.

        This method generates a portfolio report by combining risk measures and time-weighted performance.
        It also calculates and adds the Sharpe Ratio to the report.

        :return: A DataFrame containing the portfolio report.
        """
        print("Generating report... Please wait.")

        # Get risk measurements and time-weighted performance
        variance_and_standard_deviation = self.standard_deviation
        time_weighted_returns = self.time_weighted_returns

        # Concatenate risk measures and time-weighted performance horizontally
        portfolio_report = pd.concat([variance_and_standard_deviation, time_weighted_returns], axis=1)

        # Calculate Sharpe Ratio
        twr = portfolio_report["Time Weighted Returns"]
        standard_deviation = portfolio_report["Standard Deviation"]
        sharpe_ratio: pd.DataFrame = twr / standard_deviation

        # Add Sharpe Ratio to the report and round it to two decimal places
        portfolio_report["Sharpe Ratio"] = sharpe_ratio.round(2)

        return portfolio_report


performance = PerformanceAnalysis(pdf_scraper)
