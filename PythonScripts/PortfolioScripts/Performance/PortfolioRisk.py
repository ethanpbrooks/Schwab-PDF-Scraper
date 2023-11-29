from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

from PythonScripts.PortfolioScripts.Assets.AssetData import Assets, assets
from PythonScripts.FinancialAnalyst import FinancialAnalyst, financial_analyst
from PythonScripts.PortfolioScripts.Performance.PortfolioPerformance import PortfolioReturns, portfolio_returns


@dataclass
class PortfolioRisk:
    """
    A class for calculating risk measures for a financial portfolio.

    This class provides methods to calculate portfolio variance, standard deviation, and overall risk measures.
    It also incorporates time-weighted performance and calculates the Sharpe Ratio.

    :param assets: An instance of the Assets class containing portfolio asset data.
    :param financial_analyst: An instance of the FinancialAnalyst class for financial data analysis.
    :param portfolio_returns: An instance of the PortfolioReturns class for calculating portfolio returns.
    """

    assets: Assets
    financial_analyst: FinancialAnalyst
    portfolio_returns: PortfolioReturns

    def calculate_variance(self) -> pd.DataFrame:
        """
        Calculate the variance of the portfolio for different time periods.

        :return: DataFrame with portfolio variance for various time periods.
        """
        def account_values() -> List[float]:
            return [self.financial_analyst.pdf_scraper.account_value]

        historical_account_values: pd.DataFrame = self.financial_analyst.decorator_monthly_iteration(
            calculation=account_values,
            add_additional_month=False
        ).rename(index={0: "Account Value"}).T

        historical_percentage_returns: pd.DataFrame = historical_account_values[::-1].pct_change()

        time_periods = {
            "3 Month": 3,
            "Year to Date": self.financial_analyst.pdf_scraper.year_to_date_numerical_value,
            "1 Year": 12,
            "3 Year": 12 * 3,
            "5 Year": 12 * 5
        }

        portfolio_variance = pd.DataFrame()
        for period_str, period_int in time_periods.items():
            selected_time_period = historical_percentage_returns.tail(period_int)
            portfolio_variance[period_str] = selected_time_period.var()

        portfolio_variance = portfolio_variance.rename(index={"Account Value": "Variance"}).T

        self.financial_analyst.pdf_scraper.revert_to_original_pdf_file()
        return portfolio_variance

    def calculate_standard_deviation(self) -> pd.DataFrame:
        """
        Calculate the standard deviation and annualized standard deviation of the portfolio.

        :return: DataFrame with portfolio standard deviation and annualized standard deviation.
        """
        variance = self.calculate_variance()
        standard_deviation: pd.DataFrame = np.sqrt(
            variance.rename(columns={"Variance": "Standard Deviation"})
        ) * 100

        annualized_standard_deviation = standard_deviation * np.sqrt(12)
        standard_deviation["Annualized Standard Deviation"] = annualized_standard_deviation

        # self.financial_analyst.pdf_scraper.revert_to_original_pdf_file()
        return standard_deviation.round(2)

    def _calculate_risk_measures(self) -> pd.DataFrame:
        """
        Generate a portfolio report.

        This method generates a portfolio report by combining risk measures and time-weighted performance.
        It also calculates and adds the Sharpe Ratio to the report.

        :return: A DataFrame containing the portfolio report.
        """
        print("Generating report... Please wait.")

        # Get risk measurements and time-weighted performance
        variance_and_standard_deviation = self.calculate_standard_deviation()
        time_weighted_returns = self.portfolio_returns.calculate_time_weighted_returns()

        # Concatenate risk measures and time-weighted performance horizontally
        portfolio_report = pd.concat([variance_and_standard_deviation, time_weighted_returns], axis=1)

        # Calculate Sharpe Ratio
        twr = portfolio_report["Time Weighted Returns"]
        standard_deviation = portfolio_report["Standard Deviation"]
        sharpe_ratio: pd.DataFrame = twr / standard_deviation

        # Add Sharpe Ratio to the report and round it to two decimal places
        portfolio_report["Sharpe Ratio"] = sharpe_ratio.round(2)

        return portfolio_report


# Create instances of required classes
portfolio_risk = PortfolioRisk(
    assets=assets,
    financial_analyst=financial_analyst,
    portfolio_returns=portfolio_returns
)
