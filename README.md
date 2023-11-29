# Portfolio Class Documentation Summary

The Portfolio class consists of three main components: PDF Scraper, Assets, and Performance.

## Assets Component

The Assets component is responsible for managing and processing individual portfolio holdings. Key properties include 
stocks, ETFs, funds, bonds, and various allocation metrics. Users can scrape data from a Schwab PDF statement and 
calculate asset and sector allocations.

### Properties

1. `stocks`
2. `exchange_traded_funds`
3. `equity_funds`
4. `corporate_bonds`
5. `bond_partial_calls`
6. `bond_funds`
7. `fixed_income_etfs`
8. `treasuries`
9. `money_market_funds`
10. `cash_holding`
11. `options`
12. `allocation`
13. `sector_allocation`
14. `assets_sorted_by_sector`

### Usage Examples

#### 1. Scrape stocks and corporate bonds from the Schwab PDF Statement
```jupyter
stocks = portfolio.assets.stocks
corporate_bonds = portfolio.assets.corporate_bonds
```

#### 2. Calculate Portfolio Asset Allocation
```jupyter
asset_allocation = portfolio.assets.allocation
```

#### 3. Calculate Sector Allocation
```jupyter
sector_allocation = portfolio.assets.sector_allocation
```

## Performance Component

The Performance component calculates returns and risk measures for the portfolio. Properties include time-weighted 
returns, risk measures report, standard deviation, annualized standard deviation, variance, and Sharpe ratio. Users can 
calculate the time-weighted return and various risk measures.

### Properties

1. `time_weighted_returns`
2. `risk_measures_report`
3. `standard_deviation`
4. `annualized_standard_deviation`
5. `variance`
6. `sharpe_ratio`

### Usage Examples

#### 1. Calculate the time weighted return of the portfolio
```jupyter
time_weighted_returns = portfolio.performance.time_weighted_returns
```

#### 2. Calculate all risk measures, including variance and annualized standard deviation.
```jupyter
risk_measures = portfolio.performance.risk_measures
```

## Portfolio Class Instance
The Portfolio class instance integrates both the Assets and Performance components. It offers a method, 
return_contribution, to analyze the contribution of returns to the portfolio.

### Properties

1. `return_contribution`

### Usage Example

```jupyter
return_contribution = portfolio.return_contribution
```

