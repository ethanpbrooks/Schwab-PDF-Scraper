# PDFScraper and AbstractPDFScraper Class Documentation

The `PDFScraper` class, along with its abstract counterpart `AbstractPDFScraper`, is designed for extracting and processing investment data from PDF documents. These classes are specifically tailored for financial data extraction from Schwab statements and provide a structured way to access and work with different types of financial assets.

## Table of Contents

- [Constructor](#constructor)
- [Properties](#properties)
- [Methods](#methods)
- [Private Methods](#private-methods)
- [Example Usage](#example-usage)
- [Note](#note)

## AbstractPDFScraper Class

### Overview

The `AbstractPDFScraper` class serves as an abstract base class, defining the structure and interface for extracting investment data from PDF documents. It provides a set of abstract properties and methods that must be implemented by concrete subclasses. This abstraction allows for extensibility and customization when dealing with different types of financial data.

### Properties

- `asset_composition` (Abstract Property): Get the DataFrame containing asset composition information.

- `options_dataframe` (Abstract Property): Retrieve and convert options data from the PDF statement into a DataFrame.

- `equity_dataframe` (Abstract Property): Get the DataFrame containing equity investment information.

- `bond_funds_dataframe` (Abstract Property): Get the DataFrame containing bond fund investment information.

- `equity_funds_dataframe` (Abstract Property): Get the DataFrame containing equity fund investment information.

- `exchange_traded_funds_dataframe` (Abstract Property): Get the DataFrame containing Exchange Traded Fund (ETF) investment information.

- `other_assets_dataframe` (Abstract Property): Get a DataFrame containing information about other assets (e.g., ETFs) from the statements.

- `money_market_fund_dataframe` (Abstract Property): Property to retrieve a DataFrame containing investment details for Money Market Funds.

- `corporate_bonds_dataframe` (Abstract Property): Property to retrieve a DataFrame containing investment details for Corporate Bonds.

- `bond_partial_calls` (Abstract Property): Retrieve a DataFrame containing information about bond partial calls.

- `treasuries_dataframe` (Abstract Property): Property to retrieve a DataFrame containing investment details for U.S. Treasuries.

- `swap_statement(new_file_name: str)` (Abstract Method): Swap the PDF content with a new PDF file.

## PDFScraper Class

### Constructor

#### `PDFScraper(_pdf: Dict[int, list], _selected_statements_to_analyze: Dict[str, str], _list_of_fixed_income_etf: List[str])`

- Creates a new `PDFScraper` instance.
- **Parameters:**
  - `_pdf` (Dict[int, list]): A dictionary containing extracted text content from each page of a PDF document.
  - `_selected_statements_to_analyze` (Dict[str, str]): A dictionary of selected Schwab statement file names for analysis.
  - `_list_of_fixed_income_etf` (List[str]): A list of fixed income ETF tickers.

### Properties

- `selected_schwab_statements` (Property): Retrieves the list of selected Schwab statements for analysis.

- `symbols_of_fixed_income_etfs` (Property): Retrieves the list of fixed income ETF tickers.

- `currently_opened_statement` (Property): Retrieves the file name of the currently opened Schwab statement.

### Methods

The `PDFScraper` class provides various methods to extract and process data related to different asset types, including stocks, fixed income, options, and more. These methods return Pandas DataFrames containing the extracted data.

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

```pycon
# Create a PDFScraper instance
pdf_scraper = PDFScraper(_pdf_data, _selected_statements, _fixed_income_etfs)

# Retrieve equity investment data as a DataFrame
equity_data = pdf_scraper.equity_dataframe()

# Retrieve asset composition data as a DataFrame
asset_composition_data = pdf_scraper.asset_composition()
```

Please note that the AbstractPDFScraper class defines the structure and interface, while the PDFScraper class implements these methods and properties for specific data extraction from Schwab statements.

## Private Methods

### `_asset_composition(self) -> pd.DataFrame`

Extracts the asset composition information from the PDF and returns it as a DataFrame.

This method extracts the relevant section of asset composition information from the PDF,
processes the data, and creates a DataFrame with columns for "Type" and "Market Value".

**Returns:**
- A pandas DataFrame containing asset composition data with columns "Type" and "Market Value".

### `_asset_composition_text_lines(self) -> Optional[List[str]]`

Extract the text lines containing asset composition information from the Schwab statement.

This method searches through the first 5 pages of the Schwab statement to find the section
that contains asset composition information. If found, it returns the list of text lines
containing this information.

**Returns:**
- A list of text lines containing asset composition information if found, else None.

### `_find_asset_section_in_statement(self, asset: str)`

Find the start of the asset section in the PDF pages.

This function searches for the start of the asset section within the PDF
pages starting from a specified page number.

**Parameters:**
- `asset` (str): The asset type for which to find the section.

**Returns:**
- Generator that yields text lines of the section found on each page.

### `_convert_generator_of_asset_data_to_dataframe(self, asset: str, columns: List[str], numeric_columns: List[str]) -> pd.DataFrame`

Convert a generator of asset data into a Pandas DataFrame.

This function takes a generator of asset data sections, extracts the data,
and converts it into a Pandas DataFrame.

**Parameters:**
- `asset` (str): The asset string to identify data sections.
- `columns` (List[str]): List of column names for the DataFrame.
- `numeric_columns` (List[str]): List of column names to clean and convert to numeric type.

**Returns:**
- A Pandas DataFrame containing the extracted asset data.

### `__post_init__(self)`

Initialize the `PDFScraper` instance after object creation.

This method sets the currently opened statement to the most recent Schwab statement
selected for analysis.

## Note

These private methods are used internally by the `PDFScraper` class to extract, process, and convert
different types of financial data from Schwab statements. They play a crucial role in the data
extraction process and help maintain data integrity and accuracy.

