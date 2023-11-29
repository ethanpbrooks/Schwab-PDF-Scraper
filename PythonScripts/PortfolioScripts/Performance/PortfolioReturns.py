import pandas as pd
import numpy as np

from datetime import datetime
from dataclasses import dataclass
from PythonScripts.PortfolioScripts.Assets.AssetData import Assets, assets
from PythonScripts.FinancialAnalyst import FinancialAnalyst, financial_analyst


@dataclass
class PortfolioReturns:
    assets: Assets
    financial_analyst: FinancialAnalyst

    def calculate_portfolio_returns(self):
        current_account_value = self.financial_analyst.pdf_scraper.account_value.copy()

        def calculate_returns():
            period_account_value = self.financial_analyst.pdf_scraper.account_value

            difference = current_account_value / period_account_value
            percentage_change = [(difference - 1) * 100]

            return np.round(percentage_change, 2)

        p_returns = self.financial_analyst.decorator_standard_iteration(calculate_returns).rename(
            index={0: "% Returns"}
        ).T

        self.financial_analyst.pdf_scraper.revert_to_original_pdf_file()
        return p_returns

    def calculate_compounded_annual_growth_rate(self) -> pd.DataFrame:
        """
        Calculate compounded annual growth rate.

        This method calculates the compounded annual growth rate (CAGR) based on the current and period account values.

        :return: DataFrame with the compounded annual growth rate.
        """
        # Copy the current account value to avoid modification during calculations
        current_account_value = self.financial_analyst.pdf_scraper.account_value.copy()

        # Extract the current period's datetime from the statement file name
        current_period_datetime = datetime.strptime(
            self.financial_analyst.pdf_scraper.currently_opened_statement.split(".")[0],
            "%Y-%B"
        )
        current_year = current_period_datetime.year
        current_month = current_period_datetime.month

        def compounded_annual_growth_rates():
            """
            Calculate compounded annual growth rate for a specific period.

            :return: A NumPy array containing the compounded annual growth rate.
            """

            # Extract the account value for the period being analyzed
            period_account_value: float = self.financial_analyst.pdf_scraper.account_value
            period_year = int(self.financial_analyst.pdf_scraper.currently_opened_statement.split("-")[0])

            # Calculate the number of years (n) for the growth rate formula
            if current_month < 12 and (current_year - period_year) == 0:
                n = 1
            else:
                n = current_year - period_year

            # Calculate the compounded annual growth rate
            percentage_return: float = (current_account_value / period_account_value) ** (1 / n)
            return np.round([
                (percentage_return - 1) * 100
            ], 2)


        # Apply the inner function to calculate the compounded annual growth rate
        growth_rate = self.financial_analyst.decorator_standard_iteration(compounded_annual_growth_rates)
        growth_rate: pd.DataFrame = growth_rate.rename(index={0: "Compounded Annual Growth Rate"}).T

        self.financial_analyst.pdf_scraper.revert_to_original_pdf_file()
        return growth_rate.fillna(0)

    def calculate_return_contribution(self) -> pd.DataFrame:
        """
        Calculate the return contribution for different periods based on sector allocations.

        :returns: DataFrame containing return contributions for each sector over various time periods.
        """
        # Copy the current sector allocation for reference
        current_sector_allocation = self.assets.sector_allocation.copy()

        def calculate_sector_returns():
            """
            Calculate sector returns based on the changes in sector allocations.

            :return: A NumPy array containing the sector returns.
            """
            period_sector_allocation = self.assets.sector_allocation

            # Merge current and period sector allocations based on the 'Sector' column
            merged_df = pd.merge(
                current_sector_allocation,
                period_sector_allocation,
                on="Sector",
                suffixes=("_df1", "_df2")
            )

            # Calculate returns for each sector
            percentage_return = (
                    (merged_df["Market Value_df1"] - merged_df["Market Value_df2"])
                    / merged_df["Market Value_df2"]
            )

            # Calculate weighted percentage returns
            weighted_percentage_returns = percentage_return * (merged_df["Weight_df1"] / 100)
            return np.round(weighted_percentage_returns * 100, 2)

        # Apply the inner function to calculate sector returns
        sector_returns = self.financial_analyst.decorator_standard_iteration(calculate_sector_returns).set_index(
            current_sector_allocation["Sector"]
        )

        # Revert to the original PDF file after calculations
        self.financial_analyst.pdf_scraper.revert_to_original_pdf_file()

        return sector_returns

    def calculate_time_weighted_returns(self) -> pd.DataFrame:
        """
        Calculate time-weighted returns for various time periods.

        This method calculates time-weighted returns based on changes in account values and cash flow over different
        time periods.

        :return: DataFrame with time-weighted returns for different time periods.
        """
        # Define the columns to extract from the PDF data
        columns = ["Ending Value", "Beginning Value", "Cash Flow"]

        def extract_changes_in_account_values() -> tuple:
            """
            Extract changes in account values and cash flow.

            :return: A tuple containing ending value, beginning value, and cash flow.
            """
            change_in_account_value = self.financial_analyst.pdf_scraper.change_in_account_value
            ending_value = change_in_account_value["This Period"].iloc[-1]
            beginning_value = change_in_account_value["This Period"].iloc[0]

            # Extract cash deposits from the PDF data
            cash_deposit_column = "Deposits and other Cash Credits"
            cash_deposits = self.financial_analyst.pdf_scraper.scraped_cash_transaction_summary["This Period"].loc[
                cash_deposit_column]

            return ending_value, beginning_value, cash_deposits

        # Extract the data using the provided function and columns
        dataframe = self.financial_analyst.decorator_custom_iteration(
            calculation=extract_changes_in_account_values,
            add_additional_month=False,
            columns=columns
        )

        # Extract ending values and cash flow from the dataframe
        ending_values = dataframe["Ending Value"]
        cash_flow = dataframe["Cash Flow"]

        # Adjust the beginning values by adding cash flow
        adjusted_beginning_values = dataframe["Beginning Value"] + cash_flow

        # Calculate gross returns
        dataframe["Gross Returns"] = ending_values / adjusted_beginning_values

        # Define time periods for calculations
        time_periods = {
            "3 Month": 3,
            "Year to Date": self.financial_analyst.pdf_scraper.year_to_date_numerical_value,
            "1 Year": 12,
            "3 Year": 12 * 3,
            "5 Year": 12 * 5
        }

        # Calculate time-weighted returns for each time period
        time_weighted_returns = pd.DataFrame()
        for period_str, period_int in time_periods.items():
            df = dataframe["Gross Returns"]
            time_weighted_returns[period_str] = [df.head(period_int).prod() - 1]

        # Rename the index for clarity and multiply by 100 for percentage representation
        time_weighted_returns = time_weighted_returns.rename(index={0: "Time Weighted Return"}).T * 100

        # Round the values to two decimal places
        self.financial_analyst.pdf_scraper.revert_to_original_pdf_file()
        return time_weighted_returns.round(2)

    def calculate_asset_class_returns(self) -> pd.DataFrame:
        """
        Calculate asset class returns.

        This method calculates percentage returns for each asset class based on changes in asset allocation.

        :return: DataFrame with asset class returns.
        """
        # Copy the current asset allocation for reference
        current_asset_allocation: pd.DataFrame = self.assets.allocation.copy()

        def calculate_asset_class_returns() -> np.array:
            """
            Calculate percentage returns for each asset class.

            :return: A NumPy array containing percentage returns for each asset class.
            """
            period_asset_allocation = self.assets.allocation

            # Calculate percentage returns based on changes in market value
            percentage_returns = (
                     (current_asset_allocation["Market Value"] - period_asset_allocation["Market Value"])
                     / period_asset_allocation["Market Value"]
             ) * 100

            return percentage_returns.round(2)

        # Apply the inner function to calculate asset class returns
        asset_class_returns = self.financial_analyst.pdf_scraper.standard_iterator(calculate_asset_class_returns)

        # Revert to the original PDF file after calculations
        self.financial_analyst.pdf_scraper.revert_to_original_pdf_file()

        # Fill NaN values with 0 and return the results
        return asset_class_returns.fillna(0)

    def calculate_asset_class_compounded_annual_growth_rate(self):
        # Copy the current asset allocation for reference
        current_asset_allocation: pd.DataFrame = self.assets.allocation["Market Value"].copy()

        current_period_datetime = datetime.strptime(
            self.financial_analyst.pdf_scraper.currently_opened_statement.split(".")[0],
            "%Y-%B"
        )

        current_year = current_period_datetime.year
        current_month = current_period_datetime.month

        def compounded_annual_growth_rates():
            """
            Calculate compounded annual growth rate for a specific period.

            :return: A NumPy array containing the compounded annual growth rate.
            """
            # Extract the account value for the period being analyzed
            period_asset_allocation = self.assets.allocation["Market Value"]
            period_year = int(self.financial_analyst.pdf_scraper.currently_opened_statement.split("-")[0])

            # Calculate the number of years (n) for the growth rate formula
            if current_month < 12 and (current_year - period_year) == 0:
                n = 1
            else:
                n = current_year - period_year

            # Calculate the compounded annual growth rate
            percentage_return = (current_asset_allocation / period_asset_allocation) ** (1 / n)
            percentage_return = (percentage_return - 1) * 100

            return percentage_return.round(2)

        # Apply the inner function to calculate the compounded annual growth rate
        growth_rate = self.financial_analyst.decorator_standard_iteration(compounded_annual_growth_rates)

        # Revert to the original PDF file after calculations
        self.financial_analyst.pdf_scraper.revert_to_original_pdf_file()

        return growth_rate.fillna(0)

    def calculate_asset_return_contribution(self):
        weights = self.assets.allocation["Weight"]
        asset_class_returns = self.calculate_asset_class_compounded_annual_growth_rate()

        for column in asset_class_returns.columns:
            asset_class_returns[column] = asset_class_returns[column] * (weights / 100)

        return asset_class_returns.round(2).fillna(0)

    def calculate_cash_time_weighted_returns(self):

        def cash_transaction_history():
            investments_sold = self.financial_analyst.pdf_scraper.scraped_cash_transaction_summary[
                "This Period"].loc["Investments Sold"]

            cash_equivalents_allocation = self.assets.allocation["Market Value"].loc["Cash & Equivalents"]

            return cash_equivalents_allocation, investments_sold

        columns = ["Ending Cash", "Transactions"]
        cash_historical_data = self.financial_analyst.decorator_custom_iteration(
            calculation=cash_transaction_history,
            add_additional_month=True,
            columns=columns
        )

        # Unpack Values
        ending_cash = cash_historical_data["Ending Cash"].to_numpy()[:-1]
        beginning_cash = cash_historical_data["Ending Cash"].to_numpy()[1:]
        cash_transactions = np.array(cash_historical_data["Transactions"].to_list()[:-2] + [0])

        cash_dataframe = pd.DataFrame({
            "Ending Cash": ending_cash,
            "Beginning Cash": beginning_cash,
            "Beginning Cash after Transactions": beginning_cash + cash_transactions
        })


        gross_returns = cash_dataframe["Ending Cash"] / cash_dataframe[
            "Beginning Cash after Transactions"
        ]

        cash_dataframe["Gross Returns"] = gross_returns - 1

        time_periods = {
            "3 Month": 3,
            "Year to Date": self.financial_analyst.pdf_scraper.year_to_date_numerical_value,
            "1 Year": 12,
            "3 Year": 12 * 3,
            "5 Year": 12 * 5
        }

        # Calculate time-weighted returns for each time period
        cash_twr = pd.DataFrame()
        for period_str, period_int in time_periods.items():
            df = cash_dataframe["Gross Returns"]

            cash_twr[period_str] = [df.head(period_int).prod()]

        # Rename the index for clarity and multiply by 100 for percentage representation
        cash_twr = cash_twr.rename(index={0: "Cash Time Weighted Return"}).T * 100

        self.financial_analyst.pdf_scraper.revert_to_original_pdf_file()
        return cash_twr.round(2)


portfolio_returns = PortfolioReturns(assets, financial_analyst)
