import numpy as np
import pandas as pd

from PythonScripts.PortfolioScripts.AssetData import Assets, assets
from PythonScripts.PortfolioScripts.PerformanceAnalysis import PerformanceAnalysis, performance
from PythonScripts.ScrapingScripts.PDFScraper import PDFScraper, pdf_scraper

import PythonScripts.Misc as Misc

from dataclasses import dataclass


@dataclass
class Portfolio:
    """
    Represents a portfolio that combines various financial analysis components.

    :param _pdf_scraper: An instance of PDFScraper for extracting financial data from PDF statements.
    :param _assets: An instance of Assets for managing and categorizing financial assets.
    :param _performance: An instance of PerformanceAnalysis for analyzing the portfolio's performance.
    """

    _pdf_scraper: PDFScraper
    _assets: Assets
    _performance: PerformanceAnalysis

    @property
    def pdf_scraper(self):
        """
        Provides access to the PDF Scraping component of the portfolio.
        :return: An instance of the PDF Scraper
        """
        return self._pdf_scraper

    @property
    def assets(self):
        """
        Provides access to the assets management component of the portfolio.
        :return: An instance of Assets for managing and categorizing financial assets.
        """
        return self._assets

    @property
    def performance(self):
        """
        Provides access to the performance analysis component of the portfolio.
        :return: An instance of PerformanceAnalysis for analyzing the portfolio's performance.
        """
        return self._performance

    @property
    def return_contribution(self):
        return self._calculate_return_contribution()

    def _calculate_return_contribution(self):
        """
        Calculate the return contribution for different periods based on sector allocations.

        :returns: DataFrame containing return contributions for each sector over various time periods.
        """
        # Initialize an empty DataFrame to store return contributions
        sector_returns = pd.DataFrame()

        # Copy the current sector allocation for reference
        current_sector_allocation = self.assets.sector_allocation.copy()

        # Extract the start date from the currently opened statement
        start_date = self.pdf_scraper.currently_opened_statement.split(".")[0]

        # Get Schwab statement periods to analyze, excluding the current one
        schwab_statement_periods = Misc.calculate_statement_periods_to_analyze(start_date)[1:]

        # Define the time periods to analyze
        month_range = ["3 Month", "Year to Date", "1 Year", "3 Year", "5 Year"]

        # Create a dictionary mapping time periods to statement paths
        periods_and_statement_paths = {k: f"{v}.pdf" for (k, v) in zip(month_range, schwab_statement_periods)}

        # Iterate over time periods and corresponding statement paths
        for period, statement_path in periods_and_statement_paths.items():
            # Swap the statement to the one for the current time period
            self.pdf_scraper.swap_statement(statement_path)

            # Retrieve sector allocation for the current time period
            period_sector_allocation = self.assets.sector_allocation

            # Merge current and period sector allocations based on the 'Sector' column
            merged_df = pd.merge(
                current_sector_allocation,
                period_sector_allocation,
                on="Sector",
                suffixes=("_df1", "_df2")
            )

            # Calculate percentage return for each sector
            percentage_return = ((merged_df["Market Value_df1"] - merged_df["Market Value_df2"])
                                 / merged_df["Market Value_df2"])

            # Calculate weighted percentage returns based on sector weights
            weighted_percentage_returns = percentage_return * (merged_df["Weight_df1"] / 100)

            # Add the calculated return contributions to the DataFrame for the current time period
            sector_returns[period] = np.round(weighted_percentage_returns * 100, 2)

        # Revert to the original PDF file after calculations
        self.pdf_scraper.revert_to_original_pdf_file()

        # Set the index of the resulting DataFrame to sector names
        return sector_returns.set_index(current_sector_allocation["Sector"])


portfolio = Portfolio(
    _pdf_scraper=pdf_scraper,
    _assets=assets,
    _performance=performance
)
