import pandas as pd
import numpy as np
from scipy.stats import gmean
import MainScripts.PDFScraper
import MainScripts.FileManagement as FileManagement

from datetime import datetime
from dateutil.relativedelta import relativedelta

from typing import Dict, List
from dataclasses import dataclass


# File paths
EQUITY_SUMMARY_FILE_PATH = "../Excel Outputs/Equity Summary.xlsx"
fixed_income_etfs: List[str] = FileManagement.extract_fixed_income_etf_tickers()


def _convert_path_to_datetime(file_path: str) -> datetime.strftime:
    date = datetime.strptime(file_path.split(".")[0], "%Y-%B")
    return date


def _asset_is_fixed_income_as_stated_per_schwab(asset: str):
    return asset in ["U.S. Treasuries", "Partial Calls", "Corporate Bonds"]


def _sum_of_collection(asset_collection: Dict[str, pd.DataFrame]):
    return sum([asset["Market Value"].sum() for asset in asset_collection.values()])


def _generate_year_over_year_statement_paths(base_date: datetime, num_years: int) -> List[str]:
    """
    Generate a list of file paths for statements, year over year, based on a given base date.

    :param base_date (datetime) The base date for which statements are required.
    :param num_years (int) The number of years to go back from the base date.

    :returns A list of file paths in the format "YYYY-Month.pdf" for each year over the specified range.
    :rtype List[str]
    """
    statement_paths: List[str] = []

    for year_offset in range(1, num_years + 2):
        # Calculate the date for the statement by subtracting 'year_offset' years from the base date
        statement_date = base_date - relativedelta(years=year_offset)

        # Format the date as "YYYY-Month" and create the file path
        statement_path = statement_date.strftime("%Y-%B.pdf")

        # Append the file path to the list
        statement_paths.append(statement_path)

    return statement_paths


@dataclass
class Portfolio:
    """
    Represents a portfolio of financial assets and provides methods to analyze its composition and returns over time.

    This class uses a PDFScraper instance to extract financial data from PDF statements and offers properties and
    methods to access and analyze the portfolio's asset composition and returns.

    :param pdf_scraper: An instance of PDFScraper used for extracting financial data from PDF statements.
    :type pdf_scraper: Scripts.PDFScraper.PDFScraper
    """

    pdf_scraper: MainScripts.PDFScraper.PDFScraper

    @property
    def __version__(self) -> str:
        """
        Get the version of the Portfolio class.
        :returns A string representing the version of the Portfolio class.
        """
        return "1.0.4"

    @property
    def asset_allocation(self) -> pd.DataFrame:
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
    def fixed_income_etfs(self) -> pd.DataFrame:
        """
        Get a DataFrame containing the allocation of fixed income ETFs in the portfolio.

        This property retrieves the combined DataFrame of equities and exchange-traded funds (ETFs),
        and filters out rows corresponding to symbols in the fixed_income_etfs list.

        :return: A pandas DataFrame representing the allocation of fixed income ETFs in the portfolio.
        """
        return self._categorize_asset_types_from_dataframes("Fixed Income ETFs")

    @property
    def equities(self) -> pd.DataFrame:
        """
        Get a DataFrame containing the allocation of equities in the portfolio.

        This property retrieves the combined DataFrame of equities and exchange-traded funds (ETFs),
        and filters out rows corresponding to symbols in the fixed_income_etfs list.

        :return: A pandas DataFrame representing the allocation of equities in the portfolio.
        """
        return self._categorize_asset_types_from_dataframes("Equities")

    @property
    def options(self) -> pd.DataFrame:
        """
        Retrieve the DataFrame containing options data from the PDF scraper.

        This property returns a DataFrame that contains information about options
        extracted from the PDF statements.

        :return: A DataFrame containing options data.
        """
        return self._categorize_asset_types_from_dataframes("Options")

    @property
    def exchange_traded_funds(self) -> pd.DataFrame:
        """
        Get a DataFrame containing the allocation of exchange-traded funds (ETFs) in the portfolio.

        This property retrieves the combined DataFrame of equities and ETFs,
        and filters out rows corresponding to symbols in the fixed_income_etfs list.

        :return: A pandas DataFrame representing the allocation of ETFs in the portfolio.
        """
        return self._categorize_asset_types_from_dataframes("Exchange Traded Funds")

    @property
    def corporate_bonds(self) -> pd.DataFrame:
        """
        Get a DataFrame containing investment details for Corporate Bonds.

        :return: A pandas DataFrame containing investment details for Corporate Bonds.
        """
        return self._categorize_asset_types_from_dataframes("Corporate Bonds")

    @property
    def bond_partial_calls(self) -> pd.DataFrame:
        """
        Get a DataFrame containing investment details for Partial Calls Bonds.

        :return: A pandas DataFrame containing investment details for Partial Calls Bonds.
        """
        return self._categorize_asset_types_from_dataframes("Partial Calls")

    @property
    def bond_funds(self) -> pd.DataFrame:
        """
        Get a DataFrame containing investment details for Bond Funds.

        :return: A pandas DataFrame containing investment details for Bond Funds.
        """
        return self._categorize_asset_types_from_dataframes("Bond Funds")

    @property
    def equity_funds(self) -> pd.DataFrame:
        """
        Get a DataFrame containing investment details for Equity Funds.

        :return: A pandas DataFrame containing investment details for Equity Funds.
        """
        return self._categorize_asset_types_from_dataframes("Equity Funds")

    @property
    def money_market_funds(self) -> pd.DataFrame:
        """
        Get a DataFrame containing investment details for Money Market Funds.

        :return: A pandas DataFrame containing investment details for Money Market Funds with
        added "Market Value" column.
        """
        return self._categorize_asset_types_from_dataframes("Money Market Funds")

    @property
    def treasuries(self) -> pd.DataFrame:
        """
        Get a DataFrame containing investment details for U.S. Treasuries (cash equivalents).

        :return: A pandas DataFrame containing investment details for U.S. Treasuries.
        """
        return self._categorize_asset_types_from_dataframes("U.S. Treasuries")

    @property
    def equity_collection(self) -> Dict[str, pd.DataFrame]:
        """
        Get a collection of DataFrames containing equity-related asset allocations.

        This property returns a dictionary containing DataFrames for "Equities," "Exchange Traded Funds," and
        "Equity Funds."

        :return: A dictionary with asset type names as keys and corresponding DataFrames as values.
        """
        return {
            "Equities": self.equities,
            "Exchange Traded Funds": self.exchange_traded_funds,
            "Equity Funds": self.equity_funds
        }

    @property
    def cash_equivalent_collection(self) -> Dict[str, pd.DataFrame]:
        """
        Retrieve a collection of dataframes for cash equivalent investments.

        This property returns a dictionary containing dataframes for different types of cash equivalent investments.
        The collection includes U.S. Treasuries and Money Market Funds dataframes.

        :return: A dictionary with keys representing cash equivalent investment types and values as dataframes
                 containing investment details.
        :rtype: Dict[str, pd.DataFrame]
        """
        return {
            "U.S. Treasuries": self.treasuries,
            "Money Market Funds": self.money_market_funds
        }

    @property
    def fixed_income_collection(self) -> Dict[str, pd.DataFrame]:
        """
        Get a collection of DataFrames containing fixed income-related asset allocations.

        This property returns a dictionary containing DataFrames for "Corporate Bonds," "Partial Calls," "Bond Funds,"
        and "Fixed Income ETFs."

        :return: A dictionary with asset type names as keys and corresponding DataFrames as values.
        """
        return {
            "Corporate Bonds": self._categorize_asset_types_from_dataframes("Corporate Bonds"),
            "Partial Calls": self._categorize_asset_types_from_dataframes("Partial Calls"),
            "Bond Funds": self._categorize_asset_types_from_dataframes("Bond Funds"),
            "Fixed Income ETFs": self._categorize_asset_types_from_dataframes("Fixed Income ETFs")
        }

    def _categorize_asset_types_from_dataframes(self, asset: str) -> pd.DataFrame:
        """
        Categorize and process asset dataframes based on the asset type.

        This method takes an asset type as input and categorizes the dataframes
        accordingly. It applies specific conditions and computations based on
        the asset type.

        :param asset: The asset type to categorize.
        :type asset: str
        :return: A pandas DataFrame containing the categorized asset data.
        :rtype: pd.DataFrame
        """

        # Define a dictionary mapping asset types to their respective dataframes
        asset_methods: Dict[str, str] = {
            "Money Market Funds": "money_market_fund_dataframe",
            "Equities": "equity_dataframe",
            "Exchange Traded Funds": "exchange_traded_funds_dataframe",
            "Fixed Income ETFs": "exchange_traded_funds_dataframe",
            "U.S. Treasuries": "treasuries_dataframe",
            "Corporate Bonds": "corporate_bonds_dataframe",
            "Partial Calls": "bond_partial_calls",
            "Bond Funds": "bond_funds_dataframe",
            "Equity Funds": "equity_funds_dataframe",
            "Options": "options_dataframe"
        }

        if asset not in asset_methods:
            raise KeyError(f"The current version of the script does not contain '{asset}.'")

        # Retrieve the dataframe corresponding to the provided asset type
        dataframe = getattr(self.pdf_scraper, asset_methods[asset])

        # Apply conditions and computations based on asset type
        if asset in ["Fixed Income ETFs", "Exchange Traded Funds"]:
            # Older versions report ETFs as "Other Assets"
            dataframe = pd.concat([dataframe, self.pdf_scraper.other_assets_dataframe], ignore_index=True)

            is_fixed_income_eft = asset == "Fixed Income ETFs"
            fixed_income_etf_symbols: List[str] = self.pdf_scraper.symbols_of_fixed_income_etfs

            user_selected_type_of_fixed_income = dataframe["Symbol"].isin(
                fixed_income_etf_symbols) if is_fixed_income_eft else ~dataframe["Symbol"].isin(
                fixed_income_etf_symbols)

            # Filter the dataframe based on the condition and create a copy
            dataframe = dataframe.loc[user_selected_type_of_fixed_income].copy()

        # Apply additional calculations if the asset is not fixed income
        if not _asset_is_fixed_income_as_stated_per_schwab(asset) and asset != "Options":
            dataframe["Market Value"] = dataframe["Quantity"] * dataframe["Price"]

        return dataframe

    def _categorize_equities_and_exchange_traded_funds(self) -> pd.DataFrame:
        """
        Combine and calculate market value for equities and exchange-traded funds (ETFs).

        This method combines the equity and ETF dataframes from the PDFScraper instance,
        calculates the market value for each equity, and returns the resulting combined DataFrame.

        :return: A pandas DataFrame representing the combined allocation of equities and ETFs in the portfolio.
        """
        # Extract quantity and price column names for equities
        quantity, price = MainScripts.PDFScraper.equity_numeric

        # Combine both equity and ETF dataframes from the PDFScraper instance
        equities_dataframe = self.pdf_scraper.equity_dataframe
        etfs_dataframe = self.pdf_scraper.exchange_traded_funds_dataframe
        other_assets_dataframe = self.pdf_scraper.other_assets_dataframe

        combined_dataframe = pd.concat([equities_dataframe, etfs_dataframe, other_assets_dataframe], ignore_index=True)

        # Calculate the market value for each equity by multiplying quantity with price
        combined_dataframe["Market Value"] = combined_dataframe[quantity] * combined_dataframe[price]

        return combined_dataframe

    def _revert_to_original_pdf_file(self) -> None:
        """
        Revert the PDF file back to the original file.

        This method swaps the currently loaded PDF file with the original PDF file.
        It is used to ensure that the PDF file is reverted to its original state after performing operations.

        :return: None
        """
        self.pdf_scraper.swap_statement(self.pdf_scraper.selected_schwab_statements["Most Recent"])


    def _validate_calculated_asset_allocation(self, calculated_allocation: pd.DataFrame, file_name: str) -> None:
        """
        Validate the calculated asset allocation against the scraped asset allocation.

        This method checks if the calculated asset allocation matches the total scraped asset allocation.
        If there's a mismatch, it raises a ValueError with details.

        :param calculated_allocation (pd.DataFrame): The calculated asset allocation DataFrame.
        :param file_name (str): The name of the file being validated.

        :raises ValueError: If the calculated asset allocation total does not match the scraped total.
        """
        scraped_asset_allocation = np.round(self.pdf_scraper.asset_composition["Market Value"].sum(), 0)
        calculated_total = np.round(calculated_allocation["Market Value"].sum(), 0)

        if scraped_asset_allocation != calculated_total:
            raise ValueError(
                f"Portfolio total mismatch for file '{file_name}' "
                f"Scraped total: {scraped_asset_allocation}, calculated total: {calculated_total}."
            )

    def _calculate_asset_allocation(self) -> pd.DataFrame:
        """
        Calculate the allocation of assets in the portfolio.

        This method computes the allocation of assets in the portfolio, including equities,
        fixed income, cash equivalents, cash, and options.

        :returns pd.DataFrame: A DataFrame containing the asset allocation.
        """
        # Calculate the total value of individual asset categories
        asset_totals: Dict[str, float] = {
            "Equities": _sum_of_collection(self.equity_collection),
            "Fixed Income": _sum_of_collection(self.fixed_income_collection),
            "Cash Equivalents": _sum_of_collection(self.cash_equivalent_collection),
            "Cash": self.pdf_scraper.asset_composition.iloc[0]["Market Value"],
            "Options": self.options["Market Value"].sum(),
        }

        # Create a DataFrame from the asset totals, transpose, and rename the column
        asset_allocation_df = pd.DataFrame(asset_totals, index=[0]).transpose().rename(
            columns={0: "Market Value"}
        )

        # Validate the calculated asset allocation against the currently opened statement
        self._validate_calculated_asset_allocation(asset_allocation_df, self.pdf_scraper.currently_opened_statement)

        return asset_allocation_df

    def calculate_returns_over_time(self):
        """
        Calculate portfolio returns over selected time periods.

        This method calculates the percentage change in portfolio value over selected time periods.
        It uses the asset allocation at the beginning of each time period and the asset allocation
        at the end of that period to compute the returns.

        :returns pd.DataFrame: A DataFrame containing returns over the selected time periods, expressed as percentages.
        """

        # Copy the selected Schwab statements and remove the "Most Recent" entry
        time_periods_and_file_paths = self.pdf_scraper.selected_schwab_statements.copy()
        del time_periods_and_file_paths["Most Recent"]

        # Define the columns for the resulting DataFrame
        columns = time_periods_and_file_paths.keys()
        returns_over_selected_periods = pd.DataFrame([], columns=columns)

        # Get the current asset allocation at the beginning of the analysis
        current_asset_allocation = self.asset_allocation

        # Iterate through each selected time period and calculate returns
        for time_period, file_path in time_periods_and_file_paths.items():
            # Swap to the statement for the current time period
            self.pdf_scraper.swap_statement(file_path)

            # Get the asset allocation at the end of the current time period
            period_asset_allocation = self.asset_allocation

            # Calculate & store the percentage change in asset allocation
            pct_change = (current_asset_allocation - period_asset_allocation) / current_asset_allocation
            returns_over_selected_periods[time_period] = pct_change.fillna(0, inplace=False)

            # Update the current asset allocation for the next iteration
            current_asset_allocation = period_asset_allocation

        self._revert_to_original_pdf_file()

        return returns_over_selected_periods * 100

    def _calculate_returns_over_selected_periods(self, file_paths: List[str], revert_to_original_file: bool = True
                                                 ) -> pd.DataFrame:
        """
        Calculate portfolio returns over selected time periods.

        This method calculates the percentage change in portfolio value over selected time periods.
        It uses the asset allocation at the beginning and end of each time period to compute the returns.

        :param file_paths (List[str]): List of file paths to statements for each time period.
        :param revert_to_original_file (bool, optional): Whether to revert to the original PDF file after calculation.
                Defaults to True.

        :returns pd.DataFrame: A DataFrame containing returns over the selected time periods, expressed as percentages.

        """
        dataframes: List[pd.DataFrame] = []

        # Iterate through the provided file paths
        for file_path in file_paths:
            # Swap to the statement for the current time period
            self.pdf_scraper.swap_statement(file_path)
            # Append the asset allocation for the current time period
            dataframes.append(self.asset_allocation)

        # Calculate the returns by subtracting the end-of-period allocation from the start-of-period allocation
        period_returns: pd.DataFrame = (dataframes[0] - dataframes[-1]) / dataframes[0]

        # Optionally revert to the original PDF file
        if revert_to_original_file:
            self._revert_to_original_pdf_file()

        # Fill NaN values with 0 and return the calculated returns
        return period_returns.fillna(0, inplace=False)

    def calculate_yearly_returns(self):
        # Get the date of the currently opened statement
        current_statement_date = _convert_path_to_datetime(self.pdf_scraper.currently_opened_statement)

        # Generate file paths for year-over-year statements for the past 5 years
        year_over_year_file_paths = _generate_year_over_year_statement_paths(current_statement_date, 5)

        # Iterate through the list of file paths to calculate yearly returns
        yearly_returns = []
        for index in range(len(year_over_year_file_paths) - 1):
            # Select two consecutive file paths for the calculation
            selected_file_paths = year_over_year_file_paths[index: index + 2]

            # Calculate the returns between the selected statements
            yearly_return = self._calculate_returns_over_selected_periods(
                file_paths=selected_file_paths,
                revert_to_original_file=False
            )

            # Append the yearly return as a list to the results
            yearly_returns.append(yearly_return["Market Value"].to_list())

        self._revert_to_original_pdf_file()

        # Convert the list of yearly returns to a NumPy array
        yearly_returns: np.array = np.array([sum(returns) for returns in yearly_returns])

        return yearly_returns


portfolio = Portfolio(MainScripts.PDFScraper.pdf_scraper)
