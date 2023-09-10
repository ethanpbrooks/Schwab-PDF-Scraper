import pandas as pd
import numpy as np
import Scripts.PDFScraper
import Scripts.FileManagement as FileManagement

from datetime import datetime
from dateutil.relativedelta import relativedelta

from typing import Dict, List
from dataclasses import dataclass

config_file_path: str = Scripts.PDFScraper.config_file_path


# File paths
EQUITY_SUMMARY_FILE_PATH = "../Excel Outputs/Equity Summary.xlsx"
fixed_income_etfs: List[str] = FileManagement.extract_fixed_income_etf_tickers()


def _convert_path_to_datetime(file_path: str) -> datetime.strftime:
    date = datetime.strptime(file_path.split(".")[0], "%Y-%B")
    return date


@dataclass
class Portfolio:
    """
    Represents a portfolio of financial assets and provides methods to analyze its composition and returns over time.

    This class uses a PDFScraper instance to extract financial data from PDF statements and offers properties and
    methods to access and analyze the portfolio's asset composition and returns.

    :param pdf_scraper: An instance of PDFScraper used for extracting financial data from PDF statements.
    :type pdf_scraper: Scripts.PDFScraper.PDFScraper
    """

    pdf_scraper: Scripts.PDFScraper.PDFScraper

    @property
    def asset_composition(self) -> pd.DataFrame:
        """
        Retrieve the calculated asset composition of the portfolio.

        This property returns the previously calculated asset composition of the portfolio.
        The asset composition is based on the extracted data from the PDF and includes
        columns for the asset type, total market value, and the weight of each asset type
        in the portfolio.

        :return: A pandas DataFrame containing the asset composition of the portfolio.
        """
        return self._calculate_asset_allocation()

    @property
    def portfolio_returns(self) -> pd.DataFrame:
        """
        Calculate and return the portfolio returns as a pandas DataFrame.

        This property calculates the returns of the portfolio based on the changes in asset values over time.
        It uses the method `calculate_asset_changes_over_time` to calculate the changes in asset values.

        :return: A pandas DataFrame containing the portfolio returns over time.
        """
        return self._calculate_portfolio_returns_over_time()

    @property
    def fixed_income_etf(self) -> pd.DataFrame:
        """
        Get a DataFrame containing the allocation of fixed income ETFs in the portfolio.

        This method retrieves the combined DataFrame of equities and exchange-traded funds (ETFs),
        and filters out rows corresponding to symbols in the fixed_income_etfs list.

        :return: A pandas DataFrame representing the allocation of fixed income ETFs in the portfolio.
        """
        combined_dataframe = self._categorize_equities_and_exchange_traded_funds()
        fixed_income_etfs_dataframe = combined_dataframe[combined_dataframe['Symbol'].isin(fixed_income_etfs)]

        return fixed_income_etfs_dataframe

    @property
    def equities(self) -> pd.DataFrame:
        """
        Get a DataFrame containing the allocation of equities in the portfolio.

        This method retrieves the combined DataFrame of equities and exchange-traded funds (ETFs),
        and filters out rows corresponding to symbols in the fixed_income_etfs list.

        :return: A pandas DataFrame representing the allocation of equities in the portfolio.
        """
        combined_dataframe = self._categorize_equities_and_exchange_traded_funds()
        equities_dataframe = combined_dataframe[~combined_dataframe['Symbol'].isin(fixed_income_etfs)]

        return equities_dataframe

    @property
    def options(self) -> pd.DataFrame:
        """
        Retrieve the DataFrame containing options data from the PDF scraper.

        This property returns a DataFrame that contains information about options
        extracted from the PDF statements.

        :return: A DataFrame containing options data.
        """
        return self.pdf_scraper.options_dataframe

    @property
    def corporate_bonds(self) -> pd.DataFrame:
        """
        Get a DataFrame containing investment details for Corporate Bonds.

        :return: A pandas DataFrame containing investment details for Corporate Bonds.
        """
        # Combine both bond fund and equity fund dataframes from the PDFScraper instance
        bonds_dataframe = self.pdf_scraper.corporate_bonds_dataframe
        partial_calls = self.pdf_scraper.other_corporate_bonds_dataframe

        combined_bonds_dataframe = pd.concat([bonds_dataframe, partial_calls], ignore_index=True)

        return combined_bonds_dataframe

    @property
    def mutual_funds(self) -> pd.DataFrame:
        """
        Get a combined DataFrame of bond funds and equity funds from the PDFScraper instance.

        This property combines bond fund and equity fund DataFrames extracted from the PDFScraper instance.
        It calculates the market value for each mutual fund by multiplying the quantity with the price.

        :return: A DataFrame containing combined bond fund and equity fund data.
        :rtype: pd.DataFrame
        """

        # Extract quantity and price column names for mutual funds
        quantity, price = Scripts.PDFScraper.equity_numeric

        # Combine both bond fund and equity fund dataframes from the PDFScraper instance
        bond_funds_dataframe = self.pdf_scraper.bond_funds_dataframe
        equity_funds_dataframe = self.pdf_scraper.equity_fund_dataframe

        combined_dataframe = pd.concat([bond_funds_dataframe, equity_funds_dataframe], ignore_index=True)

        # Calculate the market value for each mutual fund by multiplying quantity with price
        combined_dataframe["Market Value"] = combined_dataframe[quantity] * combined_dataframe[price]

        return combined_dataframe

    @property
    def money_market_funds(self) -> pd.DataFrame:
        """
        Get a DataFrame containing investment details for Money Market Funds.

        This property retrieves investment details for money market funds from the associated PDFScraper instance.
        It calculates the market value for each money market fund by multiplying the quantity with the price.

        :return: A pandas DataFrame containing investment details for Money Market Funds with
        added "Market Value" column.
        """
        # Extract quantity and price column names for equities
        quantity, price = Scripts.PDFScraper.equity_numeric

        # Get the money market funds DataFrame from the PDFScraper instance
        money_market_fund = self.pdf_scraper.money_market_fund_dataframe

        # Calculate the market value for each money market fund by multiplying quantity with price
        money_market_fund["Market Value"] = money_market_fund[quantity] * money_market_fund[price]

        return money_market_fund

    @property
    def treasuries(self):
        """
        Get the DataFrame containing investment details for cash equivalents (U.S. Treasuries).

        :return: A pandas DataFrame containing investment details for cash equivalents (U.S. Treasuries).
        """

        return self.pdf_scraper.treasuries_dataframe

    def _categorize_equities_and_exchange_traded_funds(self) -> pd.DataFrame:
        """
        Combine and calculate market value for equities and exchange-traded funds (ETFs).

        This method combines the equity and ETF dataframes from the PDFScraper instance,
        calculates the market value for each equity, and returns the resulting combined DataFrame.

        :return: A pandas DataFrame representing the combined allocation of equities and ETFs in the portfolio.
        """
        # Extract quantity and price column names for equities
        quantity, price = Scripts.PDFScraper.equity_numeric

        # Combine both equity and ETF dataframes from the PDFScraper instance
        equities_dataframe = self.pdf_scraper.equity_dataframe
        etfs_dataframe = self.pdf_scraper.exchange_traded_funds_dataframe
        other_assets_dataframe = self.pdf_scraper.other_assets_dataframe

        combined_dataframe = pd.concat([equities_dataframe, etfs_dataframe, other_assets_dataframe], ignore_index=True)

        # Calculate the market value for each equity by multiplying quantity with price
        combined_dataframe["Market Value"] = combined_dataframe[quantity] * combined_dataframe[price]

        return combined_dataframe

    def _calculate_asset_allocation(self) -> pd.DataFrame:
        """
        Calculate the composition of different asset types in the portfolio.

        This method calculates the composition of cash holdings, cash equivalents, equities, and fixed income
        in the portfolio. It extracts relevant values from different DataFrames and calculates their totals and weights.
        The calculated weights and weighted returns are added as new columns to the resulting DataFrame.

        :return: A DataFrame representing the composition of different asset types, including their total values,
                 weights, and weighted returns.
        """
        original_asset_composition_dataframe = self.pdf_scraper.asset_composition
        current_statement = self.pdf_scraper.currently_opened_statement

        # Get the total market value of Cash Holding
        cash = original_asset_composition_dataframe.iloc[0]["Market Value"]

        # Calculate the total market value for Cash Equivalents and Money Market Funds
        treasuries = self.treasuries["Market Value"].sum()
        money_market_fund = self.money_market_funds["Market Value"].sum()

        # Calculate the total market value for Mutual Funds, Corporate Bonds, and Fixed Income ETFs
        mutual_funds = self.mutual_funds["Market Value"].sum()
        corporate_bonds = self.corporate_bonds["Market Value"].sum()
        fi_etf = self.fixed_income_etf["Market Value"].sum()

        # Calculate the total market value for Fixed Income asset_returns
        sum_of_fixed_income = mutual_funds + corporate_bonds + fi_etf
        sum_of_cash_equivalents = treasuries + money_market_fund

        # Calculate the total market value for Equities
        sum_of_equities = self.equities["Market Value"].sum()

        # Calculate the total market value for Options
        sum_of_options = self.options["Market Value"].sum()

        # Create a DataFrame to store asset composition summary
        columns = ["Asset Type", "Total"]
        asset_returns = {
            "Asset Type": ["Cash Holding", "Cash Equivalents", "Equities", "Fixed Income", "Options"],
            "Total": [cash, sum_of_cash_equivalents, sum_of_equities, sum_of_fixed_income, sum_of_options]
        }

        asset_composition = pd.DataFrame(asset_returns, columns=columns)
        asset_composition["Weight"] = asset_composition["Total"] / asset_composition["Total"].sum()

        # Calculate the weighted return for each asset type
        asset_composition["Weighted Return"] = asset_composition["Total"] * asset_composition["Weight"]

        # Check if the totals match
        scraped_portfolio_total = round(original_asset_composition_dataframe["Market Value"].sum())
        calculated_total = round(asset_composition["Total"].sum())

        if scraped_portfolio_total != calculated_total:
            raise ValueError(
                f"Portfolio total mismatch for file '{current_statement}' "
                f"Scraped total: {scraped_portfolio_total}, calculated total: {calculated_total}."
            )

        asset_composition.fillna(0, inplace=True)
        return asset_composition

    def _revert_to_original_pdf_file(self) -> None:
        """
        Revert the PDF file back to the original file.

        This method swaps the currently loaded PDF file with the original PDF file.
        It is used to ensure that the PDF file is reverted to its original state after performing operations.

        :return: None
        """
        self.pdf_scraper.swap_statement(self.pdf_scraper.selected_schwab_statements["Most Recent"])

    def _calculate_portfolio_returns_over_time(self):
        """
        Calculate portfolio returns over a specified time period.

        This method calculates the returns of the portfolio for each specified time period by subtracting the
        asset composition totals of each period from the current asset composition totals. The results are
        stored in a DataFrame where each column represents a period, and each row represents an asset type.

        :return: A DataFrame containing portfolio returns over the specified time periods.
        """
        # Get the current asset allocation
        current_asset_allocation = self.asset_composition
        current_asset_totals = current_asset_allocation["Total"].to_numpy()

        # Get the periods and file paths for portfolio statements
        portfolio_periods_and_paths = self.pdf_scraper.selected_schwab_statements.copy()
        portfolio_periods_and_paths.pop("Most Recent")  # Remove the most recent period

        # Initialize a dictionary to store returns for each period
        portfolio_returns_over_time = {}

        # Iterate through each period and statement file
        for period, file_path in portfolio_periods_and_paths.items():
            # Swap to the statement file for the current period
            self.pdf_scraper.swap_statement(file_path)

            # Get the asset allocation for the current period
            period_asset_allocation = self.asset_composition
            period_asset_totals = period_asset_allocation["Total"].to_numpy()

            # Calculate the returns for each asset type and store in a NumPy array
            period_returns = current_asset_totals - period_asset_totals
            # period_returns = np.diff(np.stack([period_asset_totals, current_asset_totals]), axis=0)

            # Store the period returns to the dictionary
            portfolio_returns_over_time[period] = period_returns

        # Create a DataFrame from the portfolio returns dictionary with asset types as index
        returns_over_time_dataframe = pd.DataFrame(
            portfolio_returns_over_time, index=current_asset_allocation["Asset Type"]
        )

        self._revert_to_original_pdf_file()
        return returns_over_time_dataframe

    def calculate_monthly_returns(self):
        statement_paths = self.pdf_scraper.selected_schwab_statements.values()
        datetime_dates: List[datetime.strptime] = [
            _convert_path_to_datetime(file_path) for file_path in statement_paths
        ]

        most_recent_date = datetime_dates[0]
        last_available_date = datetime_dates[-1]

        monthly_statement_paths: List[str] = []
        time_periods: List[str] = []

        date, i = most_recent_date, 1
        while date != last_available_date:
            time_periods.append(date)

            date_datetime_as_string = date.strftime("%Y-%B")
            validated_path_name = FileManagement.validated_file_path(date_datetime_as_string)
            monthly_statement_paths.append(validated_path_name)

            date = most_recent_date - relativedelta(months=i)
            i += 1

        portfolio_monthly_returns = []
        length_of_monthly_statement_paths = len(monthly_statement_paths)
        for index in range(0, length_of_monthly_statement_paths, 2):
            two_month_range = monthly_statement_paths[slice(index, index+2)]

            monthly_totals = []
            for month_path in two_month_range[::-1]:
                self.pdf_scraper.swap_statement(month_path)
                total = self.asset_composition["Total"].to_numpy()
                monthly_totals.append(total)

            monthly_totals = np.stack(monthly_totals)
            portfolio_monthly_returns.append(np.diff(monthly_totals, axis=0))

        for i in portfolio_monthly_returns:
            print(i)


portfolio = Portfolio(Scripts.PDFScraper.pdf_scraper)
