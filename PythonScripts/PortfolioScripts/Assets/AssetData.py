# _________________________Standard Libraries_________________________
import numpy as np
import pandas as pd
import os

from typing import Dict, List
from dataclasses import dataclass

# _________________________Custom Python Classes_________________________
from PythonScripts.ScrapingScripts.PDFScraper import PDFScraper, pdf_scraper

# _________________________Custom Python Modules_________________________
import PythonScripts.PortfolioScripts.Assets.MarketData as Md


_sectors_csv_path = "4. Sectors"


def get_sector_tickers() -> Dict[str, np.array]:
    """
    Retrieves a mapping of sectors to their corresponding ticker symbols from CSV files.

    :returns Dict[str, np.array]: A dictionary where keys are sector names and values are arrays of ticker symbols.
    """

    # Get a list of CSV files in the specified path
    sector_paths = os.listdir(_sectors_csv_path)

    sector_ticker_map: Dict[str, np.array] = {}

    # Loop through each CSV file in the specified path
    for path in sector_paths:
        # Build the full path to the CSV file
        full_path = f"{_sectors_csv_path}/{path}"

        # Add the sector-ticker mapping to the dictionary
        tickers = pd.read_csv(full_path)["Symbol"].to_numpy()
        sector_name = path.removesuffix(".csv")

        sector_ticker_map[sector_name] = tickers

    return sector_ticker_map


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
    def allocation(self) -> pd.DataFrame:
        return self._calculate_asset_allocation()

    # ____________________Equities____________________
    @property
    def stocks(self) -> pd.DataFrame:
        """
        Get and categorize stocks from the data.

        :return: DataFrame of categorized stocks.
        """
        return self._categorize_asset_types_from_dataframe("Stocks", "Quantity")

    @property
    def exchange_traded_funds(self) -> pd.DataFrame:
        """
        Get and categorize equity-based exchange-traded funds (ETFs) from the data.

        :return: DataFrame of categorized equity-based ETFs.
        """
        return self._categorize_exchange_traded_funds_from_dataframe("Equity")

    @property
    def equity_funds(self) -> pd.DataFrame:
        """
        Get and categorize equity funds from the data.

        :return: DataFrame of categorized equity funds.
        """
        return self._categorize_asset_types_from_dataframe("Equity Funds", "Quantity")

    # ____________________Fixed Income____________________
    @property
    def fixed_income_etfs(self) -> pd.DataFrame:
        """
        Get and categorize fixed income-based exchange-traded funds (ETFs) from the data.

        :return: DataFrame of categorized fixed income-based ETFs.
        """
        return self._categorize_exchange_traded_funds_from_dataframe("Fixed Income")

    @property
    def corporate_bonds(self) -> pd.DataFrame:
        """
        Get and categorize corporate bonds from the data.

        :return: DataFrame of categorized corporate bonds.
        """
        return self._categorize_asset_types_from_dataframe("Corporate Bonds", "Par")

    @property
    def bond_partial_calls(self) -> pd.DataFrame:
        """
        Get and categorize bond partial calls from the data.

        :return: DataFrame of categorized bond partial calls.
        """
        return self._categorize_asset_types_from_dataframe("Bond Partial Calls", "Par")

    @property
    def bond_funds(self) -> pd.DataFrame:
        """
        Get and categorize bond funds from the data.

        :return: DataFrame of categorized bond funds.
        """
        return self._categorize_asset_types_from_dataframe("Bond Funds", "Quantity")

    # ____________________Cash & Cash Equivalents____________________
    @property
    def money_market_funds(self) -> pd.DataFrame:
        """
        Get and categorize money market funds from the data.

        :return: DataFrame of categorized money market funds.
        """
        return self._categorize_asset_types_from_dataframe("Money Market Funds", "Quantity")

    @property
    def treasuries(self) -> pd.DataFrame:
        """
        Get and categorize U.S. Treasuries from the data.

        :return: DataFrame of categorized U.S. Treasuries.
        """
        return self._categorize_asset_types_from_dataframe("U.S. Treasuries", "Par")

    @property
    def cash_holding(self) -> pd.DataFrame:
        """
        Get the market value of cash holdings from the data.

        :return: Market value of cash holdings.
        """
        return self.pdf_scraper.asset_composition.iloc[0]["Market Value"]

    # ____________________Other Asset Classes____________________
    @property
    def options(self):
        return self._categorize_asset_types_from_dataframe("Options", "Quantity")

    # ____________________Misc. Items____________________
    @property
    def holdings(self):
        """
        Calculate and return the allocation of holdings based on weights to the total account value.

        :returns: DataFrame containing the calculated allocation of holdings.
        """
        return self._calculate_allocation_by_weight_to_total_account_value()

    @property
    def sector_allocation(self):
        """
        Calculate and return the sector allocation based on holdings.

        :returns: DataFrame containing the calculated sector allocation.
        """
        return self._calculate_sector_allocation()

    @property
    def assets_sorted_by_sectors(self):
        """
        Calculate and return the sector allocation without grouping, sorted by sector names.

        :returns: DataFrame containing the sorted sector allocation without grouping.
        """
        return self._calculate_sector_allocation(group=False).sort_values(by="Sector").reset_index(drop=True)

    def _calculate_sector_allocation(self, group: bool = True) -> pd.DataFrame:
        """
        Calculate sector allocation for stocks and exchange-traded funds.

        :returns: DataFrame containing Symbol, Name, Market Value, Weight, and Sector columns.
        """

        # Define the columns to keep in the final DataFrame
        columns = ["Symbol", "Name", "Market Value", "Weight", "Sector"]

        # Get the sector-ticker mapping from the Directories class
        sector_ticker_map = get_sector_tickers()

        # Extract stocks DataFrame from the class attribute
        stocks: pd.DataFrame = self.stocks

        # Map tickers to sectors using apply and a lambda function
        stocks["Sector"] = stocks["Symbol"].apply(lambda ticker: next(
                (sector for sector, tickers in sector_ticker_map.items() if ticker in tickers),
                "Not Classified")
        )

        # Fill NaN values in the 'Sector' column with the 'Not Classified' value
        not_classified_value = "Not Classified"
        stocks["Sector"].fillna(not_classified_value, inplace=True)

        # Extract exchange-traded funds DataFrame from the class attribute
        exchange_traded_funds = self.exchange_traded_funds
        exchange_traded_funds["Sector"] = ["Equity ETF"] * len(exchange_traded_funds)

        fixed_income_etfs = self.fixed_income_etfs
        fixed_income_etfs["Sector"] = ["Fixed Income ETF"] * len(fixed_income_etfs)

        # Concatenate stocks and exchange-traded funds DataFrames
        portfolio_sectors = pd.concat([
            stocks[columns], exchange_traded_funds[columns], fixed_income_etfs[columns]
        ], ignore_index=True)

        if not group:
            return portfolio_sectors

        sector_sum_df: pd.DataFrame = portfolio_sectors.groupby("Sector")[["Market Value", "Weight"]].sum()
        sector_sum_df = sector_sum_df.reset_index()

        return sector_sum_df.sort_values(by="Weight", ascending=False).reset_index(drop=True)

    def _calculate_allocation_by_weight_to_total_account_value(self):
        asset_classes: List[str] = [
            "stocks", "exchange_traded_funds", "equity_funds",
            "corporate_bonds", "bond_funds", "fixed_income_etfs",
            "money_market_funds", "treasuries", "options"
        ]

        assets_sorted_by_weight = pd.DataFrame()
        columns_to_extract = ["Name", "Weight", "Market Value"]

        for asset in asset_classes:
            asset_dataframe = getattr(self, asset)[columns_to_extract]
            assets_sorted_by_weight = pd.concat([assets_sorted_by_weight, asset_dataframe], ignore_index=False)

        return assets_sorted_by_weight.sort_values(by="Weight", ascending=False).reset_index(drop=True)

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

    # ____________________Validation____________________
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
