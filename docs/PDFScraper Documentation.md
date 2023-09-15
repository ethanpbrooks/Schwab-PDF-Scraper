# PDFScraper Class Documentation

The `PDFScraper` class is responsible for extracting and processing investment data from PDF documents. It supports various asset types such as equities, fixed income, options, and more. This class is specifically designed for use in financial data extraction from Schwab statements.

## Constructor

### `PDFScraper(_pdf: Dict[int, list], _selected_statements_to_analyze: Dict[str, str], _list_of_fixed_income_etf: List[str])`

- Creates a new `PDFScraper` instance.
- **Parameters:**
  - `_pdf` (Dict[int, list]): A dictionary containing extracted text content from each page of a PDF document.
  - `_selected_statements_to_analyze` (Dict[str, str]): A dictionary of selected Schwab statement file names for analysis.
  - `_list_of_fixed_income_etf` (List[str]): A list of fixed income ETF tickers.

## Properties

### `selected_schwab_statements`

- Retrieves the list of selected Schwab statements for analysis.
- **Returns:** A dictionary where keys represent selected statements and values represent their file names.

### `symbols_of_fixed_income_etfs`

- Retrieves the list of fixed income ETF tickers.
- **Returns:** A list of fixed income ETF tickers.

### `currently_opened_statement`

- Retrieves the file name of the currently opened Schwab statement.
- **Returns:** The file name of the currently opened Schwab statement.

## Methods

The `PDFScraper` class provides various methods to extract and process data related to different asset types, including equities, fixed income, options, and more. These methods return Pandas DataFrames containing the extracted data.

- `asset_composition()` - Extracts asset composition information from the PDF and returns it as a DataFrame.

- `options_dataframe()` - Retrieves and converts options data from the PDF statement into a DataFrame.

- `equity_dataframe()` - Retrieves equity investment data from the PDF statement and returns it as a DataFrame.

- `bond_funds_dataframe()` - Retrieves bond fund investment data from the PDF statement and returns it as a DataFrame.

- `equity_funds_dataframe()` - Retrieves equity fund investment data from the PDF statement and returns it as a DataFrame.

- `exchange_traded_funds_dataframe()` - Retrieves Exchange Traded Fund (ETF) investment data from the PDF statement and returns it as a DataFrame.

- `other_assets_dataframe()` - Retrieves information about other assets (e.g., ETFs) from the PDF statement and returns it as a DataFrame.

- `money_market_fund_dataframe()` - Retrieves investment details for Money Market Funds from the PDF statement and returns them as a DataFrame.

- `corporate_bonds_dataframe()` - Retrieves investment details for Corporate Bonds from the PDF statement and returns them as a DataFrame.

- `bond_partial_calls()` - Retrieves information about bond partial calls from the PDF statement and returns it as a DataFrame.

- `treasuries_dataframe()` - Retrieves investment details for U.S. Treasuries from the PDF statement and returns them as a DataFrame.

- `swap_statement(new_file_name: str)` - Swaps the PDF content with a new PDF file, updating the internal PDF dictionary.

**Note:** The above methods return Pandas DataFrames containing the extracted data, making it easy to analyze and work with the financial data.

## Example Usage

```python
# Create a PDFScraper instance
pdf_scraper = PDFScraper(_pdf_data, _selected_statements, _fixed_income_etfs)

# Retrieve equity investment data as a DataFrame
equity_data = pdf_scraper.equity_dataframe()

# Retrieve asset composition data as a DataFrame
asset_composition_data = pdf_scraper.asset_composition()
