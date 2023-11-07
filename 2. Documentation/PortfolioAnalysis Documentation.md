# Portfolio Class Documentation

The `Portfolio` class represents a financial portfolio and provides methods and properties for analyzing its asset composition and returns over time. This class relies on the `PDFScraper` instance to extract financial data from PDF statements.

## Constructor

### `Portfolio(pdf_scraper: Scripts.PDFScraper.PDFScraper)`

- Creates a new `Portfolio` instance.
- Parameters:
  - `pdf_scraper` (Scripts.PDFScraper.PDFScraper): An instance of `PDFScraper` used for extracting financial data from PDF statements.

## Properties

### `asset_allocation`

- Retrieves the calculated asset composition of the portfolio.
- PerformanceAnalysis: A pandas DataFrame containing the asset composition of the portfolio, including asset type, total market value, and asset weight.

### `fixed_income_etfs`

- Retrieves a DataFrame containing the allocation of fixed income ETFs in the portfolio.
- PerformanceAnalysis: A pandas DataFrame representing the allocation of fixed income ETFs.

### `stocks`

- Retrieves a DataFrame containing the allocation of stocks in the portfolio.
- PerformanceAnalysis: A pandas DataFrame representing the allocation of stocks.

### `options`

- Retrieves a DataFrame containing options data from the PDF scraper.
- PerformanceAnalysis: A pandas DataFrame containing options data.

### `exchange_traded_funds`

- Retrieves a DataFrame containing the allocation of exchange-traded funds (ETFs) in the portfolio.
- PerformanceAnalysis: A pandas DataFrame representing the allocation of ETFs.

### `corporate_bonds`

- Retrieves a DataFrame containing investment details for Corporate Bonds.
- PerformanceAnalysis: A pandas DataFrame containing investment details for Corporate Bonds.

### `bond_partial_calls`

- Retrieves a DataFrame containing investment details for Partial Calls Bonds.
- PerformanceAnalysis: A pandas DataFrame containing investment details for Partial Calls Bonds.

### `bond_funds`

- Retrieves a DataFrame containing investment details for Bond Funds.
- PerformanceAnalysis: A pandas DataFrame containing investment details for Bond Funds.

### `equity_funds`

- Retrieves a DataFrame containing investment details for Equity Funds.
- PerformanceAnalysis: A pandas DataFrame containing investment details for Equity Funds.

### `money_market_funds`

- Retrieves a DataFrame containing investment details for Money Market Funds.
- PerformanceAnalysis: A pandas DataFrame containing investment details for Money Market Funds, including an added "Market Value" column.

### `treasuries`

- Retrieves a DataFrame containing investment details for U.S. Treasuries (cash equivalents).
- PerformanceAnalysis: A pandas DataFrame containing investment details for U.S. Treasuries.

### `equity_collection`

- Retrieves a collection of DataFrames containing equity-related asset allocations.
- PerformanceAnalysis: A dictionary with asset type names as keys and corresponding DataFrames as values.

### `cash_equivalent_collection`

- Retrieves a collection of dataframes for cash equivalent investments.
- PerformanceAnalysis: A dictionary with keys representing cash equivalent investment types and values as dataframes containing investment details.

### `fixed_income_collection`

- Retrieves a collection of DataFrames containing fixed income-related asset allocations.
- PerformanceAnalysis: A dictionary with asset type names as keys and corresponding DataFrames as values.

## Methods

### `_categorize_asset_types_from_dataframes(asset: str)`

- Categorizes and processes asset dataframes based on the asset type.
- Parameters:
  - `asset` (str): The asset type to categorize.
- PerformanceAnalysis: A pandas DataFrame containing the categorized asset data.

### `_categorize_equities_and_exchange_traded_funds()`

- Combines and calculates market value for stocks and exchange-traded funds (ETFs).
- PerformanceAnalysis: A pandas DataFrame representing the combined allocation of stocks and ETFs in the portfolio.

### `_revert_to_original_pdf_file()`

- Reverts the PDF file back to the original file.
- This method swaps the currently loaded PDF file with the original PDF file to ensure that the PDF file is in its original state.
- PerformanceAnalysis: None

### `_validate_calculated_asset_allocation(calculated_allocation: pd.DataFrame, file_name: str)`

- Validates the calculated asset allocation against the scraped asset allocation.
- Parameters:
  - `calculated_allocation` (pd.DataFrame): The calculated asset allocation DataFrame.
  - `file_name` (str): The name of the file being validated.
- Raises:
  - `ValueError` if the calculated asset allocation total does not match the scraped total.

### `_calculate_asset_allocation()`

- Calculates the allocation of assets in the portfolio.
- PerformanceAnalysis: A pandas DataFrame containing the asset allocation.

### `calculate_returns_over_time()`

- Calculates portfolio returns over selected time periods.
- PerformanceAnalysis: A DataFrame containing returns over the selected time periods, expressed as percentages.

### `_calculate_returns_over_selected_periods(file_paths: List[str], revert_to_original_file: bool = True)`

- Calculates portfolio returns over selected time periods.
- Parameters:
  - `file_paths` (List[str]): List of file paths to statements for each time period.
  - `revert_to_original_file` (bool, optional): Whether to revert to the original PDF file after calculation. Defaults to True.
- PerformanceAnalysis: A DataFrame containing returns over the selected time periods, expressed as percentages.

### `calculate_yearly_returns()`

- Calculates yearly returns for the portfolio.
- PerformanceAnalysis: A NumPy array containing yearly returns.

## Example Usage

```python
# Create a Portfolio instance
portfolio = Portfolio(Scripts.PDFScraper.pdf_scraper)

# Access properties and methods
asset_allocation = portfolio.asset_allocation
stocks = portfolio.stocks
returns_over_time = portfolio.calculate_returns_over_time()
yearly_returns = portfolio.calculate_yearly_returns()
