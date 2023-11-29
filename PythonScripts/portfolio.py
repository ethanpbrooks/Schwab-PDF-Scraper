import pandas as pd

import progressbar
from dataclasses import dataclass
from typing import Dict

from PythonScripts.PortfolioScripts.Performance.PortfolioPerformance import PortfolioPerformance, portfolio_performance
from PythonScripts.PortfolioScripts.Assets.AssetData import Assets, assets
from PythonScripts.ScrapingScripts.PDFScraper import PDFScraper, pdf_scraper



@dataclass
class Portfolio:
    """
    A class representing a financial portfolio.

    This class includes properties for accessing the PDF scraper, portfolio performance, and asset data.

    :param _pdf_scraper: An instance of the PDFScraper class for handling PDF scraping operations.
    :param _performance: An instance of the PortfolioPerformance class for managing portfolio performance.
    :param _assets: An instance of the Assets class containing portfolio asset data.
    """

    _pdf_scraper: PDFScraper
    _performance: PortfolioPerformance
    _assets: Assets

    @property
    def pdf_scraper(self) -> PDFScraper:
        """
        Property to access the PDF scraper.

        :return: An instance of the PDFScraper class.
        """
        return self._pdf_scraper

    @property
    def performance(self) -> PortfolioPerformance:
        """
        Property to access portfolio performance.

        :return: An instance of the PortfolioPerformance class.
        """
        return self._performance

    @property
    def assets(self) -> Assets:
        """
        Property to access portfolio asset data.

        :return: An instance of the Assets class.
        """
        return self._assets

    def export_to_excel(self):
        """
        Export portfolio data to an Excel workbook.

        This method exports multiple DataFrames, including asset and performance data, to an Excel workbook.
        The data is organized into different sheets based on the specified property maps.

        """
        # Property maps for assets and performance components
        assets_property_map: Dict[str, str] = {
            "Stocks": "stocks",
            "Exchange Traded Funds": "exchange_traded_funds",
            "Equity Funds": "equity_funds",
            "Fixed Income ETFs": "fixed_income_etfs",
            "Corporate Bonds": "corporate_bonds",
            "Bond Funds": "bond_funds",
            "Money Market Funds": "money_market_funds",
            "US Treasuries": "treasuries",
            "Options": "options",
            "Asset Allocation": "allocation",
        }

        performance_property_map: Dict[str, str] = {
            "Time Weighted Returns": "time_weighted_returns",
            "Compounded Annual Growth Rate": "compounded_annual_growth_rate",
            "Variance": "variance",
            "Standard Deviation": "standard_deviation",
            "Sector Return Contribution": "sector_return_contribution",
            "Asset Class Returns": "asset_class_returns",
            "Asset Class (CAGR) Returns": "asset_class_compounded_annual_growth_rate",
            "Asset (CAGR) Contribution": "asset_return_contribution"
        }

        # Combine property maps
        property_map: Dict[str, str] = {**assets_property_map, **performance_property_map}

        # Path for the Excel workbook
        excel_path = "3. Excel Files/Portfolio Data.xlsx"

        # Create the Excel writer outside the loop
        with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
            for item, reference in property_map.items():
                # Determine the component (assets or performance)
                component = self.assets if item in assets_property_map else self.performance

                # Write each DataFrame to the same Excel file using the same writer
                getattr(component, reference).to_excel(writer, sheet_name=item)


# Create an instance of the Portfolio class
portfolio = Portfolio(
    _pdf_scraper=pdf_scraper,
    _performance=portfolio_performance,
    _assets=assets
)
