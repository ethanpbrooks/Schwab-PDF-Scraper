from PythonScripts.ScrapingScripts.PDFScraper import PDFScraper, pdf_scraper

from typing import Dict
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Assets:
    """
    A class representing financial assets and their categorization.

    This class allows you to organize and categorize various financial assets such as stocks, bonds, and ETFs
    from a data source, providing methods and properties for easy access and analysis.

    :param pdf_scraper: An instance of PythonScripts.PDFScraper.PDFScraper for extracting financial data.
    """
    pdf_scraper: PDFScraper

    @property
    def allocation(self):
        return self._calculate_asset_allocation()

    # ____________________Equities____________________
    @property
    def stocks(self):
        """
        Get and categorize stocks from the data.

        :return: DataFrame of categorized stocks.
        """
        return self._categorize_asset_types_from_dataframe("Stocks", "Quantity")

    @property
    def exchange_traded_funds(self):
        """
        Get and categorize equity-based exchange-traded funds (ETFs) from the data.

        :return: DataFrame of categorized equity-based ETFs.
        """
        return self._categorize_exchange_traded_funds_from_dataframe("Equity")

    @property
    def equity_funds(self):
        """
        Get and categorize equity funds from the data.

        :return: DataFrame of categorized equity funds.
        """
        return self._categorize_asset_types_from_dataframe("Equity Funds", "Quantity")

    # ____________________Fixed Income____________________
    @property
    def fixed_income_etfs(self):
        """
        Get and categorize fixed income-based exchange-traded funds (ETFs) from the data.

        :return: DataFrame of categorized fixed income-based ETFs.
        """
        return self._categorize_exchange_traded_funds_from_dataframe("Fixed Income")

    @property
    def corporate_bonds(self):
        """
        Get and categorize corporate bonds from the data.

        :return: DataFrame of categorized corporate bonds.
        """
        return self._categorize_asset_types_from_dataframe("Corporate Bonds", "Par")

    @property
    def bond_partial_calls(self):
        """
        Get and categorize bond partial calls from the data.

        :return: DataFrame of categorized bond partial calls.
        """
        return self._categorize_asset_types_from_dataframe("Bond Partial Calls", "Par")

    @property
    def bond_funds(self):
        """
        Get and categorize bond funds from the data.

        :return: DataFrame of categorized bond funds.
        """
        return self._categorize_asset_types_from_dataframe("Bond Funds", "Quantity")

    # ____________________Cash & Cash Equivalents____________________
    @property
    def money_market_funds(self):
        """
        Get and categorize money market funds from the data.

        :return: DataFrame of categorized money market funds.
        """
        return self._categorize_asset_types_from_dataframe("Money Market Funds", "Quantity")

    @property
    def treasuries(self):
        """
        Get and categorize U.S. Treasuries from the data.

        :return: DataFrame of categorized U.S. Treasuries.
        """
        return self._categorize_asset_types_from_dataframe("U.S. Treasuries", "Par")

    @property
    def cash_holding(self):
        """
        Get the market value of cash holdings from the data.

        :return: Market value of cash holdings.
        """
        return self.pdf_scraper.asset_composition.iloc[0]["Market Value"]

    @property
    def options(self):
        return self._categorize_asset_types_from_dataframe("Options", "Quantity")

    # ____________________Calculations____________________
    def _calculate_asset_allocation(self) -> pd.DataFrame:
        """
        Calculate the assets of assets in the portfolio.

        This method computes the assets of assets in the portfolio, including stocks,
        fixed income, cash equivalents, cash, and options.

        :performance pd.DataFrame: A DataFrame containing the asset assets.
        """

        # Define asset classes and their corresponding sub-assets
        asset_classes: Dict[str, list] = {
            "Equities": ["stocks", "exchange_traded_funds", "equity_funds"],
            "Fixed Income": ["corporate_bonds", "bond_funds", "fixed_income_etfs"],
            "Cash & Equivalents": ["money_market_funds", "treasuries"],
            "Options": ["options"]
        }

        # Initialize a dictionary to store asset assets
        asset_allocation: Dict[str, float] = {}

        # Calculate the assets for each asset class
        for asset, sub_assets in asset_classes.items():
            asset_allocation[asset] = np.sum([getattr(self, x)["Market Value"].sum() for x in sub_assets])

        # Add cash to the "Cash Equivalents" category
        asset_allocation["Cash & Equivalents"] += self.cash_holding

        # Create a Pandas DataFrame to store the asset assets
        asset_allocation: pd.DataFrame = pd.DataFrame(asset_allocation, index=["Market Value"]).transpose()

        # Calculate the weight of each asset class
        asset_allocation["Weight"] = (asset_allocation["Market Value"] / self.pdf_scraper.account_value) * 100

        return asset_allocation.round(2)

    def _validate_calculated_asset_allocation(self, calculated_allocation: pd.DataFrame, file_name: str) -> None:
        """
        Validate the calculated asset assets against the scraped asset assets.

        This method checks if the calculated asset assets matches the total scraped asset assets.
        If there's a mismatch, it raises a ValueError with details.

        :param calculated_allocation (pd.DataFrame): The calculated asset assets DataFrame.
        :param file_name (str): The name of the file being validated.

        :raises ValueError: If the calculated asset assets total does not match the scraped total.
        """
        scraped_portfolio_total = np.round(self.pdf_scraper.account_value, 0)
        calculated_total = np.round(calculated_allocation["Market Value"].sum(), 0)

        if scraped_portfolio_total != calculated_total:
            raise ValueError(
                f"Portfolio total mismatch for file '{file_name}' "
                f"Scraped total: {scraped_portfolio_total}, calculated total: {calculated_total}."
            )

    # ____________________Categorizations____________________
    def _categorize_asset_types_from_dataframe(self, asset: str, quantity: str):
        """
        Categorize and sort assets from a specified DataFrame.

        :param asset: Name of the asset type.
        :param quantity: Name of the quantity column in the DataFrame.
        :return: DataFrame of categorized assets sorted by market value.
        """
        asset_map = {
            "Stocks": "scraped_stocks",
            "Equity Funds": "scraped_equity_funds",
            "U.S. Treasuries": "scraped_treasuries",
            "Money Market Funds": "scraped_money_market_funds",
            "Corporate Bonds": "scraped_corporate_bonds",
            "Bond Partial Calls": "scraped_bond_partial_calls",
            "Bond Funds": "scraped_bond_funds",
            "Options": "scraped_options"
        }

        # Get the specified asset DataFrame
        dataframe: pd.DataFrame = getattr(self.pdf_scraper, asset_map[asset])

        # Calculate the market value if 'Price' and 'Quantity' columns exist
        try:
            dataframe["Market Value"] = dataframe[quantity] * dataframe["Price"]
        except KeyError:
            pass

        account_value = self.pdf_scraper.account_value
        dataframe["Weight"] = (dataframe["Market Value"] / account_value) * 100

        # Sort the DataFrame by 'Market Value'
        dataframe = dataframe.round(2).sort_values(ascending=False, by="Market Value")

        return dataframe.reset_index(drop=True)

    def _categorize_exchange_traded_funds_from_dataframe(self, asset_type: str):
        """
        Categorize and sort exchange-traded funds (ETFs) from specified dataframes.

        :param asset_type: Type of ETFs to categorize (e.g., "Equity" or "Fixed Income").
        :return: DataFrame of categorized ETFs sorted by market value.
        """
        # Get the ETF data from the PDF scraper
        exchange_traded_funds = self.pdf_scraper.scraped_exchange_traded_funds
        other_assets = self.pdf_scraper.scraped_other_assets


        # Combine ETF dataframes
        combined_etfs = pd.concat([exchange_traded_funds, other_assets], ignore_index=True)

        # Filter ETFs based on the asset type (Equity or Fixed Income)
        if asset_type == "Equity":
            combined_etfs = self._filter_out_equity_etfs(combined_etfs)
        elif asset_type == "Fixed Income":
            combined_etfs = self._filter_out_fixed_income_etfs(combined_etfs)

        # Calculate the market value of the ETFs
        combined_etfs["Market Value"] = combined_etfs["Quantity"] * combined_etfs["Price"]
        account_value = self.pdf_scraper.account_value

        # Sort Market Values
        combined_etfs["Weight"] = (combined_etfs["Market Value"] / account_value) * 100

        combined_etfs = combined_etfs.round(2).sort_values(ascending=False, by="Market Value")

        return combined_etfs.reset_index(drop=True)

    # ____________________Filters____________________
    def _filter_out_fixed_income_etfs(self, combined_etfs: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out fixed income ETFs from a DataFrame of ETFs.

        :param combined_etfs: DataFrame of combined ETFs.
        :return: DataFrame of ETFs excluding fixed income ETFs.
        """
        # Get symbols of fixed income ETFs
        fixed_income_etf_symbols = self.pdf_scraper.symbols_of_fixed_income_etfs

        # Filter out fixed income ETFs
        combined_etfs = combined_etfs[combined_etfs["Symbol"].isin(fixed_income_etf_symbols)]

        return combined_etfs

    def _filter_out_equity_etfs(self, combined_etfs: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out equity ETFs from a DataFrame of ETFs.

        :param combined_etfs: DataFrame of combined ETFs.
        :return: DataFrame of ETFs excluding equity ETFs.
        """
        # Get symbols of fixed income ETFs
        fixed_income_etf_symbols = self.pdf_scraper.symbols_of_fixed_income_etfs

        # Filter out equity ETFs
        combined_etfs = combined_etfs[~combined_etfs["Symbol"].isin(fixed_income_etf_symbols)]

        return combined_etfs


assets = Assets(
    pdf_scraper=pdf_scraper
)
