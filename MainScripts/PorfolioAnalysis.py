import pandas as pd
import numpy as np
import MainScripts.PDFScraper
import MainScripts.FileManagement as FileManagement

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from typing import Dict, List
from dataclasses import dataclass

import calendar


# File paths
EQUITY_SUMMARY_FILE_PATH = "../Excel Outputs/Equity Summary.xlsx"
fixed_income_etfs: List[str] = FileManagement.extract_fixed_income_etf_tickers()
_primary_asset_classes = ["Equities", "Fixed Income", "Cash & Cash Equivalents"]


def _asset_is_fixed_income_as_stated_per_schwab(asset: str):
    return asset in ["U.S. Treasuries", "Partial Calls", "Corporate Bonds"]


def _sum_of_collection(asset_collection: Dict[str, pd.DataFrame]):
    return sum([asset["Market Value"].sum() for asset in asset_collection.values()])


def _asset_class_map() -> Dict[str, str]:
    asset_methods: Dict[str, str] = {
        "Money Market Funds": "money_market_funds",
        "Stocks": "stocks",
        "Exchange Traded Funds": "exchange_traded_funds",
        "Fixed Income ETFs": "fixed_income_etfs",
        "U.S. Treasuries": "treasuries",
        "Corporate Bonds": "corporate_bonds",
        "Bond Funds": "bond_funds",
        "Equity Funds": "equity_funds",
        "Options": "options"
    }

    return asset_methods


def _subtract_months(start_date, num_months):
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


def _last_day_of_month_from_string(date_string: str):
    """
    Convert a date string in the format "year-month" with the month written out to the last day of the month in
    "year-month-day" format.

    :param date_string:
    :return: The last day of the specified month in the format "year-month-day".
    """
    # Split the date string into year and month
    year, month_name = date_string.split('-')

    # Map the month name to its numeric representation
    month = list(calendar.month_name).index(month_name)

    # Find the last day of the month
    last_day = calendar.monthrange(int(year), month)[1]

    return f"{year}-{month:02d}-{last_day:02d}"


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


def _pdf_scraper_asset_property_map() -> Dict[str, str]:
    """

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

    return asset_methods


def _portfolio_asset_property_map() -> Dict[str, str]:
    asset_methods: Dict[str, str] = {
        "Money Market Funds": "money_market_funds",
        "Equities": "stocks",
        "Exchange Traded Funds": "exchange_traded_funds",
        "Fixed Income ETFs": "fixed_income_etfs",
        "U.S. Treasuries": "treasuries",
        "Corporate Bonds": "corporate_bonds",
        "Bond Funds": "bond_funds",
        "Equity Funds": "equity_funds",
        "Options": "options"
    }

    return asset_methods


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
        return "0.9.7"

    @property
    def time_periods_and_file_paths(self) -> Dict[str, str]:
        # Copy the selected Schwab statements and remove the "Most Recent" entry
        time_periods_and_file_paths: Dict[str, str] = self.pdf_scraper.selected_schwab_statements.copy()
        del time_periods_and_file_paths["Most Recent"]

        return time_periods_and_file_paths

    @property
    def account_value(self) -> float:
        return self.pdf_scraper.change_in_account_value()["This Period"][-1]

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

        This property retrieves the combined DataFrame of stocks and exchange-traded funds (ETFs),
        and filters out rows corresponding to symbols in the fixed_income_etfs list.

        :return: A pandas DataFrame representing the allocation of fixed income ETFs in the portfolio.
        """
        return self._categorize_asset_types_from_dataframes("Fixed Income ETFs")

    @property
    def stocks(self) -> pd.DataFrame:
        """
        Get a DataFrame containing the allocation of stocks in the portfolio.

        This property retrieves the combined DataFrame of stocks and exchange-traded funds (ETFs),
        and filters out rows corresponding to symbols in the fixed_income_etfs list.

        :return: A pandas DataFrame representing the allocation of stocks in the portfolio.
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

        This property retrieves the combined DataFrame of stocks and ETFs,
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
            "Equities": self.stocks,
            "Exchange Traded Funds": self.exchange_traded_funds,
            "Equity Funds": self.equity_funds
        }

    @property
    def cash_holding(self) -> float:
        """
        Get the cash holding value from the current PDF statement.

        This property retrieves the cash holding value, represented by the "Market Value" of the first entry
        in the asset composition section of the current PDF statement.

        :return: The cash holding value as a float.
        """
        return self.pdf_scraper.asset_composition.iloc[0]["Market Value"]

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

    @property
    def risk_measurements(self) -> pd.DataFrame:
        """
        Get risk measurements based on historical percentage returns.

        This property calculates risk measurements, including variance, standard deviation,
        and annualized standard deviation, based on historical percentage returns over various time periods.

        :return: A DataFrame containing risk measurements.
        """
        return self._calculate_risk_measurements()

    @property
    def time_weighted_returns(self):
        """
        Calculate and return time-weighted returns for the portfolio.

        This property calculates and returns time-weighted returns for the portfolio, which provide a measure of the
        portfolio's performance that is not affected by the timing or size of cash flows into or out of the portfolio.

        :return: Time-weighted returns as a percentage.
        """
        return self._calculate_time_weighted_returns()

    @property
    def risk_adjusted_performance_measures(self):
        """
        Calculate and return risk-adjusted performance measures for the portfolio.

        This property calculates and returns various risk-adjusted performance measures for the portfolio, which can help
        assess how well the portfolio has performed considering its risk.

        :return: A DataFrame containing risk-adjusted performance measures.
        """
        return self._calculate_risked_adjusted_performance_measures()

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

        asset_methods = _pdf_scraper_asset_property_map()
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
        Combine and calculate market value for stocks and exchange-traded funds (ETFs).

        This method combines the equity and ETF dataframes from the PDFScraper instance,
        calculates the market value for each equity, and returns the resulting combined DataFrame.

        :return: A pandas DataFrame representing the combined allocation of stocks and ETFs in the portfolio.
        """
        # Extract quantity and price column names for stocks
        quantity, price = MainScripts.PDFScraper.equity_numeric

        # Combine both equity and ETF dataframes from the PDFScraper instance
        equities_dataframe = self.pdf_scraper.equity_dataframe
        etfs_dataframe = self.pdf_scraper.exchange_traded_funds_dataframe
        other_assets_dataframe = self.pdf_scraper.other_assets_dataframe

        combined_dataframe = pd.concat([equities_dataframe, etfs_dataframe, other_assets_dataframe], ignore_index=True)

        # Calculate the market value for each equity by multiplying quantity with price
        combined_dataframe["Market Value"] = combined_dataframe[quantity] * combined_dataframe[price]

        return combined_dataframe

    def _validate_calculated_asset_allocation(self, calculated_allocation: pd.DataFrame, file_name: str) -> None:
        """
        Validate the calculated asset allocation against the scraped asset allocation.

        This method checks if the calculated asset allocation matches the total scraped asset allocation.
        If there's a mismatch, it raises a ValueError with details.

        :param calculated_allocation (pd.DataFrame): The calculated asset allocation DataFrame.
        :param file_name (str): The name of the file being validated.

        :raises ValueError: If the calculated asset allocation total does not match the scraped total.
        """
        scraped_portfolio_total = np.round(self.account_value, 0)
        calculated_total = np.round(calculated_allocation["Market Value"].sum(), 0)

        if scraped_portfolio_total != calculated_total:
            raise ValueError(
                f"Portfolio total mismatch for file '{file_name}' "
                f"Scraped total: {scraped_portfolio_total}, calculated total: {calculated_total}."
            )

    def _calculate_asset_allocation(self) -> pd.DataFrame:
        """
        Calculate the allocation of assets in the portfolio.

        This method computes the allocation of assets in the portfolio, including stocks,
        fixed income, cash equivalents, cash, and options.

        :returns pd.DataFrame: A DataFrame containing the asset allocation.
        """

        # Define asset classes and their corresponding sub-assets
        asset_classes: Dict[str, list] = {
            "Equities": ["stocks", "exchange_traded_funds", "equity_funds"],
            "Fixed Income": ["corporate_bonds", "bond_funds", "fixed_income_etfs"],
            "Cash & Equivalents": ["money_market_funds", "treasuries"],
            "Options": ["options"]
        }

        # Initialize a dictionary to store asset allocation
        asset_allocation: Dict[str, float] = {}

        # Calculate the allocation for each asset class
        for asset, sub_assets in asset_classes.items():
            asset_allocation[asset] = np.sum([getattr(self, x)["Market Value"].sum() for x in sub_assets])

        # Add cash to the "Cash Equivalents" category
        asset_allocation["Cash & Equivalents"] += self.cash_holding

        # Create a Pandas DataFrame to store the asset allocation
        asset_allocation: pd.DataFrame = pd.DataFrame(asset_allocation, index=["Market Value"]).transpose()

        # Calculate the weight of each asset class
        asset_allocation["Weight"] = (asset_allocation["Market Value"] / self.account_value) * 100

        return asset_allocation.round(2)

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
        current_asset_allocation = self.asset_allocation["Market Value"].copy()

        # Iterate through each selected time period and calculate returns
        for time_period, file_path in time_periods_and_file_paths.items():
            # Swap to the statement for the current time period
            self.pdf_scraper.swap_statement(file_path)

            # Get the asset allocation at the end of the current time period
            period_asset_allocation = self.asset_allocation["Market Value"]

            # Calculate & store the percentage change in asset allocation
            dollar_change = current_asset_allocation - period_asset_allocation
            returns_over_selected_periods[time_period] = dollar_change

        self.pdf_scraper.revert_to_original_pdf_file()

        return returns_over_selected_periods

    def _schwab_statement_dates(self, num_months: int) -> List[str]:
        """
        Calculate a list of Schwab statement paths for a specified number of months.

        This method computes a list of file paths for Schwab statements by subtracting the specified number of months from
        the currently opened statement's file name.

        :param num_months: The number of months for which statement paths should be calculated.
        :return: A list of statement paths for the specified months.
        """
        # Get the start date from the currently opened statement's file name.
        start_date: str = self.pdf_scraper.currently_opened_statement.split(".")[0]

        # Calculate a list of file dates by subtracting the specified number of months.
        statement_paths: List[str] = _subtract_months(start_date, num_months)

        return statement_paths

    def _historical_account_values(self, num_months: int) -> pd.DataFrame:
        """
        Retrieve historical account values for a specified number of months.

        This method gathers historical account values by swapping Schwab statements to the corresponding dates and
        extracting the account value for each date.

        :param num_months: The number of months for which historical account values should be collected.
        :return: A DataFrame containing historical account values, indexed by file dates.
        """
        schwab_statement_paths = self._schwab_statement_dates(num_months)

        # Iterate through the file dates to gather historical data.
        historical_values: Dict[str, list] = {}
        for date in schwab_statement_paths:
            # Swap the statement to the corresponding date.
            self.pdf_scraper.swap_statement(f"{date}.pdf")
            historical_values[date] = [self.account_value]

        historical_values: pd.DataFrame = pd.DataFrame(historical_values).transpose().rename(
            columns={0: "Account Value"})[::-1]

        return historical_values

    def _calculate_risk_measurements(self):
        """
        Calculate risk measurements, including variance, standard deviation, and annualized standard deviation.

        This method calculates risk measurements based on historical percentage returns over various time periods.

        :return: A DataFrame containing risk measurements.
        """
        # Calculate historical percentage returns over the specified time period
        quarter, one_year, three_year, five_year = 3, 12, 12 * 3, 12 * 5

        historical_percentage_returns = self._historical_account_values(five_year).pct_change()
        year_to_date = datetime.strptime(historical_percentage_returns.index[-1], "%Y-%B").month

        # Define the time periods and corresponding column names
        periods = [quarter, year_to_date, one_year, three_year, five_year]
        columns = ["Quarter", "Year to Date", "One Year", "Three Year", "Five Year"]

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

    def _calculate_internal_rates_of_returns(self) -> pd.DataFrame:
        """
        Calculate internal rates of return for the portfolio.

        This method calculates internal rates of returns by analyzing changes in the account's value and cash flows
        over a specified number of months.

        :return: Internal Rates of Returns.
        """
        # Define the items to be included in the account summary
        account_items = ["Period", "Ending Value", "Starting Value", "Cash Flow"]
        account_summary: Dict[str, List] = {k: [] for k in account_items}
        cash_flow_items = ["Credits", "Debits", "Transfer of Securities (In/Out)"]

        # Get Schwab statement dates for the specified number of months
        num_months = 12 * 5
        schwab_statement_dates = self._schwab_statement_dates(num_months)

        def insert_data_to_dict(date: str, dataframe: pd.DataFrame):
            # Calculate account value and cash flow
            ending_account_value = dataframe.iloc[-1]
            starting_account_value = dataframe.loc["Starting Value"]
            cash_flow = dataframe.loc[cash_flow_items].sum()

            data_list = [date, ending_account_value, starting_account_value, cash_flow]

            for item, data in zip(account_items, data_list):
                account_summary[item].append(data)

        for statement_date in schwab_statement_dates:
            # Swap statement, calculate changes, and insert data into the summary
            self.pdf_scraper.swap_statement(f"{statement_date}.pdf")
            account_value_changes = self.pdf_scraper.change_in_account_value()["This Period"]
            insert_data_to_dict(statement_date, account_value_changes)

        # Revert to the original PDF file
        self.pdf_scraper.revert_to_original_pdf_file()

        account_summary["Cash Flow"][-1] = 0

        # Create a DataFrame from the account summary
        account_summary: pd.DataFrame = pd.DataFrame(account_summary)

        # Calculate the "Adjusted Starting Value"
        account_summary["Adjusted Starting Value"] = account_summary["Starting Value"] + account_summary["Cash Flow"]

        adjusted_beginning_value = account_summary["Adjusted Starting Value"]
        ending_value = account_summary["Ending Value"]

        # Calculate the internal rate of return
        account_summary["Internal Rate of Return"] = ending_value / adjusted_beginning_value

        return account_summary["Internal Rate of Return"]

    def _calculate_time_weighted_returns(self) -> pd.DataFrame:
        """
        Calculate time-weighted returns for different time periods.

        This method calculates time-weighted returns for various time periods, including the quarter, year to date,
        one year, three years, and five years, based on previously calculated internal rates of return.

        :return: Time-weighted returns for each time period as a DataFrame.
        """
        # Calculate internal rates of returns
        internal_rates_of_returns = self._calculate_internal_rates_of_returns()

        # Define the time periods and corresponding column names
        quarter, one_year, three_year, five_year = 3, 12, 12 * 3, 12 * 5
        year_to_date = datetime.strptime(self.pdf_scraper.currently_opened_statement, "%Y-%B.pdf").month + 1
        periods = [quarter, year_to_date, one_year, three_year, five_year]
        columns = ["Quarter", "Year to Date", "One Year", "Three Year", "Five Year"]

        # Calculate time-weighted returns for each time period
        returns = [internal_rates_of_returns.head(n).prod() - 1 for n in periods]

        # Create a DataFrame with the time-weighted returns
        time_weighted_returns = pd.DataFrame(
            {c: [twr] for (c, twr) in zip(columns, returns)}, index=["Time Weighted Returns"]
        ).transpose()

        # Convert the results to percentages rounded to two decimal places
        return np.round(time_weighted_returns * 100, 2)

    def _calculate_risked_adjusted_performance_measures(self) -> pd.DataFrame:
        """
        Generate a portfolio report.

        This method generates a portfolio report by combining risk measures and time-weighted returns.
        It also calculates and adds the Sharpe Ratio to the report.

        :return: A DataFrame containing the portfolio report.
        """
        print("Generating report... Please wait.")

        # Get risk measurements and time-weighted returns
        risk_measures = self.risk_measurements
        time_weighted_returns = self.time_weighted_returns

        # Concatenate risk measures and time-weighted returns horizontally
        portfolio_report = pd.concat([risk_measures, time_weighted_returns], axis=1)

        # Calculate Sharpe Ratio
        twr = portfolio_report["Time Weighted Returns"]
        standard_deviation = portfolio_report["Standard Deviation"]
        sharpe_ratio: pd.DataFrame = twr / standard_deviation

        # Add Sharpe Ratio to the report and round it to two decimal places
        portfolio_report["Sharpe Ratio"] = sharpe_ratio.round(2)

        return portfolio_report

    def export_to_excel(self) -> None:
        asset_methods: Dict[str, str] = {
            "Money Market Funds": "money_market_funds",
            "Equities": "stocks",
            "Exchange Traded Funds": "exchange_traded_funds",
            "Fixed Income ETFs": "fixed_income_etfs",
            "U.S. Treasuries": "treasuries",
            "Corporate Bonds": "corporate_bonds",
            "Bond Funds": "bond_funds",
            "Equity Funds": "equity_funds",
            "Options": "options"
        }

        with pd.ExcelWriter("Portfolio Report.xlsx", engine="xlsxwriter") as writer:
            for sheet_name in asset_methods:
                dataframe: pd.DataFrame = getattr(self, asset_methods[sheet_name])
                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

            portfolio.calculate_returns_over_time().to_excel(writer, sheet_name="Returns", index=True)

        self.pdf_scraper.revert_to_original_pdf_file()


portfolio = Portfolio(MainScripts.PDFScraper.pdf_scraper)
