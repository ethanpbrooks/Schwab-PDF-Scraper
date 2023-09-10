# Portfolio Analysis Script Documentation

## Overview

This script is designed for analyzing a financial portfolio. It uses a PDF scraper to extract financial data from PDF statements and provides methods to analyze the portfolio's asset composition, returns over time, and more.

## Table of Contents

1. [Imports and File Paths](#imports-and-file-paths)
2. [Class: `Portfolio`](#class-portfolio)
   1. [Asset Composition](#asset-composition)
   2. [Portfolio Returns](#portfolio-returns)
   3. [Fixed Income ETF Allocation](#fixed-income-etf-allocation)
   4. [Equity Allocation](#equity-allocation)
   5. [Options Data](#options-data)
   6. [Corporate Bonds Allocation](#corporate-bonds-allocation)
   7. [Mutual Funds Allocation](#mutual-funds-allocation)
   8. [Money Market Funds Allocation](#money-market-funds-allocation)
   9. [Treasuries Allocation](#treasuries-allocation)
   10. [Private Methods](#private-methods)
   11. [Monthly Returns Calculation](#monthly-returns-calculation)

## 1. Imports and File Paths <a name="imports-and-file-paths"></a>

- Imports necessary libraries such as pandas, numpy, datetime, and more.
- Defines file paths for output files and obtains fixed income ETF tickers.

## 2. Class: `Portfolio` <a name="class-portfolio"></a>

Represents a portfolio of financial assets and provides methods to analyze its composition and returns over time.

### 2.1. Asset Composition <a name="asset-composition"></a>

- **Description**: Retrieves the calculated asset composition of the portfolio.
- **Properties**:
  - `asset_composition`: A pandas DataFrame containing the asset composition of the portfolio.
- **Methods**:
  - `_calculate_asset_allocation()`: Private method to calculate asset allocation.

### 2.2. Portfolio Returns <a name="portfolio-returns"></a>

- **Description**: Calculates and returns the portfolio returns over time.
- **Properties**:
  - `portfolio_returns`: A pandas DataFrame containing portfolio returns over time.
- **Methods**:
  - `_calculate_portfolio_returns_over_time()`: Private method to calculate returns over time.

### 2.3. Fixed Income ETF Allocation <a name="fixed-income-etf-allocation"></a>

- **Description**: Retrieves a DataFrame containing the allocation of fixed income ETFs in the portfolio.
- **Properties**:
  - `fixed_income_etf`: A pandas DataFrame representing the allocation of fixed income ETFs.

### 2.4. Equity Allocation <a name="equity-allocation"></a>

- **Description**: Retrieves a DataFrame containing the allocation of equities in the portfolio.
- **Properties**:
  - `equities`: A pandas DataFrame representing the allocation of equities.

### 2.5. Options Data <a name="options-data"></a>

- **Description**: Retrieves a DataFrame containing options data from the PDF scraper.
- **Properties**:
  - `options`: A DataFrame containing options data.

### 2.6. Corporate Bonds Allocation <a name="corporate-bonds-allocation"></a>

- **Description**: Retrieves a DataFrame containing investment details for Corporate Bonds.
- **Properties**:
  - `corporate_bonds`: A pandas DataFrame containing investment details for Corporate Bonds.

### 2.7. Mutual Funds Allocation <a name="mutual-funds-allocation"></a>

- **Description**: Retrieves a combined DataFrame of bond funds and equity funds from the PDFScraper instance.
- **Properties**:
  - `mutual_funds`: A DataFrame containing combined bond fund and equity fund data.

### 2.8. Money Market Funds Allocation <a name="money-market-funds-allocation"></a>

- **Description**: Retrieves a DataFrame containing investment details for Money Market Funds.
- **Properties**:
  - `money_market_funds`: A pandas DataFrame containing investment details for Money Market Funds.

### 2.9. Treasuries Allocation <a name="treasuries-allocation"></a>

- **Description**: Retrieves a DataFrame containing investment details for cash equivalents (U.S. Treasuries).
- **Properties**:
  - `treasuries`: A pandas DataFrame containing investment details for cash equivalents.

### 2.10. Private Methods <a name="private-methods"></a>

- `_categorize_equities_and_exchange_traded_funds()`: Private method to combine and calculate market value for equities and ETFs.
- `_calculate_asset_allocation()`: Private method to calculate asset allocation.
- `_revert_to_original_pdf_file()`: Private method to revert the PDF file back to its original state.
- `_calculate_portfolio_returns_over_time()`: Private method to calculate returns over time.
- `calculate_monthly_returns()`: Method to calculate monthly returns.

### 2.11. Monthly Returns Calculation <a name="monthly-returns-calculation"></a>

- **Description**: Calculates monthly returns for the portfolio based on statement data.

## 3. Usage Example <a name="usage-example"></a>

- Instantiates the `Portfolio` class and demonstrates how to use it for portfolio analysis.

```python
portfolio = Portfolio(Scripts.PDFScraper.pdf_scraper)

This documentation provides an overview of the script's structure, properties, and methods. It serves as a reference for understanding and using the script for portfolio analysis.

Please note that the script is still in development, and further updates and improvements may be made.

Feel free to modify or expand the documentation as needed to provide additional details or context specific to your project.
