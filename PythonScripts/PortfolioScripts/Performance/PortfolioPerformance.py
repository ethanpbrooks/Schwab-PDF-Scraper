from dataclasses import dataclass

import pandas as pd

from PythonScripts.PortfolioScripts.Performance.PortfolioReturns import PortfolioReturns, portfolio_returns
from PythonScripts.PortfolioScripts.Performance.PortfolioRisk import PortfolioRisk, portfolio_risk


@dataclass
class PortfolioPerformance:
    portfolio_returns: PortfolioReturns
    portfolio_risk: PortfolioRisk

    @property
    def variance(self) -> pd.DataFrame:
        return self.portfolio_risk.calculate_variance()

    @property
    def standard_deviation(self) -> pd.DataFrame:
        return self.portfolio_risk.calculate_standard_deviation()

    @property
    def time_weighted_returns(self) -> pd.DataFrame:
        return self.portfolio_returns.calculate_time_weighted_returns()

    @property
    def absolute_returns(self) -> pd.DataFrame:
        return self.portfolio_returns.calculate_portfolio_returns()

    @property
    def asset_class_returns(self):
        return self.portfolio_returns.calculate_asset_class_returns()

    @property
    def asset_class_compounded_annual_growth_rate(self):
        return self.portfolio_returns.calculate_asset_class_compounded_annual_growth_rate()

    @property
    def compounded_annual_growth_rate(self):
        return self.portfolio_returns.calculate_compounded_annual_growth_rate()

    @property
    def asset_return_contribution(self) -> pd.DataFrame:
        return self.portfolio_returns.calculate_asset_return_contribution()

    @property
    def sector_return_contribution(self) -> pd.DataFrame:
        return self.portfolio_returns.calculate_return_contribution()

    @property
    def cash_time_weighted_returns(self) -> pd.DataFrame:
        return self.portfolio_returns.calculate_cash_time_weighted_returns()


portfolio_performance = PortfolioPerformance(
    portfolio_returns=portfolio_returns,
    portfolio_risk=portfolio_risk
)
