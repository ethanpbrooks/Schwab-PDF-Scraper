from PythonScripts.PortfolioScripts.AssetData import Assets, assets
from PythonScripts.PortfolioScripts.PerformanceAnalysis import PerformanceAnalysis, performance
from PythonScripts.ScrapingScripts.PDFScraper import PDFScraper, pdf_scraper
from dataclasses import dataclass


@dataclass
class Portfolio:
    """
    Represents a portfolio that combines various financial analysis components.

    :param _pdf_scraper: An instance of PDFScraper for extracting financial data from PDF statements.
    :param _assets: An instance of Assets for managing and categorizing financial assets.
    :param _performance: An instance of PerformanceAnalysis for analyzing the portfolio's performance.
    """

    _pdf_scraper: PDFScraper  # PDFScraper should not be available to the user
    _assets: Assets
    _performance: PerformanceAnalysis

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


portfolio = Portfolio(
    _pdf_scraper=pdf_scraper,
    _assets=assets,
    _performance=performance
)
