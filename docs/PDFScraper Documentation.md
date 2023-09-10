# PDF Scraper

The `PDFScraper` script is designed to extract and process investment data from PDF documents, particularly Schwab statements. It provides methods and properties to extract data for different asset types, such as equities, fixed income, options, and more, and convert them into Pandas DataFrames for further analysis.

## Table of Contents
1. [Requirements](#requirements)
2. [File Paths](#file-paths)
3. [Data Structures](#data-structures)
4. [Functions](#functions)
   - [_read_pdf(pdf_name)](#read-pdf)
   - [_symbol_corresponding_to_asset(asset)](#symbol-corresponding-to-asset)
   - [_clean_text_lines_from_page(text_lines, asset)](#clean-text-lines-from-page)
   - [_extract_asset_data_from_text_lines(text_lines, asset)](#extract-asset-data-from-text-lines)
5. [PDFScraper Class](#pdfscraper-class)
   - [Properties](#properties)
     - [selected_schwab_statements](#selected-schwab-statements)
     - [currently_opened_statement](#currently-opened-statement)
     - [pdf](#pdf)
     - [asset_composition](#asset-composition)
     - [options_dataframe](#options-dataframe)
     - [equity_dataframe](#equity-dataframe)
     - [bond_funds_dataframe](#bond-funds-dataframe)
     - [equity_fund_dataframe](#equity-fund-dataframe)
     - [exchange_traded_funds_dataframe](#exchange-traded-funds-dataframe)
     - [other_assets_dataframe](#other-assets-dataframe)
     - [money_market_fund_dataframe](#money-market-fund-dataframe)
     - [corporate_bonds_dataframe](#corporate-bonds-dataframe)
     - [other_corporate_bonds_dataframe](#other-corporate-bonds-dataframe)
     - [treasuries_dataframe](#treasuries-dataframe)
   - [Methods](#methods)
     - [swap_statement(new_file_name)](#swap-statement)
6. [Initialization](#initialization)

## Requirements<a name="requirements"></a>

- Python 3.7+
- PyMuPDF (fitz)
- Pandas
- dataclasses module

## File Paths<a name="file-paths"></a>

- `config_file_path`: Path to the configuration file.
- `statements_directory_path`: Path to the directory containing PDF statements.
- `_schwab_statement_paths`: A dictionary mapping statement types to their file paths.
- `_months`: A list of month names.

## Data Structures<a name="data-structures"></a>

- `equity_columns`: List of column names for equity data.
- `equity_numeric`: List of numeric columns in the equity data.
- `option_columns`: List of column names for option data.
- `option_numeric`: List of numeric columns in the option data.
- `fixed_income_columns`: List of column names for fixed income data.
- `fi_numeric`: List of numeric columns in the fixed income data.

## Functions<a name="functions"></a>

### _read_pdf(pdf_name)<a name="read-pdf"></a>

Extracts and splits text content from each page of a PDF document.

- `pdf_name`: The name of the PDF file.
- Returns a dictionary where keys represent page numbers, and values represent extracted and split text content from each page.
- Raises `FileNotFoundError` if the specified PDF file is not found.

### _symbol_corresponding_to_asset(asset)<a name="symbol-corresponding-to-asset"></a>

Get the symbol corresponding to a given asset type.

- `asset`: The asset type for which to retrieve the symbol.
- Returns the symbol corresponding to the input asset type.
- Raises `KeyError` if the input asset type is not found in the configuration.

### _clean_text_lines_from_page(text_lines, asset)<a name="clean-text-lines-from-page"></a>

Clean text lines from a page by removing specified line items.

- `text_lines`: List of text lines from a page.
- `asset`: The asset string to identify lines to retain.
- Returns a cleaned list of text lines.

### _extract_asset_data_from_text_lines(text_lines, asset)<a name="extract-asset-data-from-text-lines"></a>

Extract asset data from a list of text lines.

- `text_lines`: List of text lines to extract data from.
- `asset`: The asset type for which to extract data.
- Returns a list of tuples containing extracted asset data.

## PDFScraper Class<a name="pdfscraper-class"></a>

A class for extracting and processing investment data from PDF documents.

### Properties<a name="properties"></a>

#### selected_schwab_statements<a name="selected-schwab-statements"></a>

Get the list of selected Schwab statements for analysis.

#### currently_opened_statement<a name="currently-opened-statement"></a>

Get the currently opened Schwab statement file.

#### pdf<a name="pdf"></a>

Get the dictionary of extracted PDF content.

#### asset_composition<a name="asset-composition"></a>

Get the DataFrame containing asset composition information.

#### options_dataframe<a name="options-dataframe"></a>

Retrieve and convert options data from the PDF statement into a DataFrame.

#### equity_dataframe<a name="equity-dataframe"></a>

Get the DataFrame containing equity investment information.

#### bond_funds_dataframe<a name="bond-funds-dataframe"></a>

Get the DataFrame containing bond fund investment information.

#### equity_fund_dataframe<a name="equity-fund-dataframe"></a>

Get the DataFrame containing equity fund investment information.

#### exchange_traded_funds_dataframe<a name="exchange-traded-funds-dataframe"></a>

Get the DataFrame containing Exchange Traded Fund (ETF) investment information.

#### other_assets_dataframe<a name="other-assets-dataframe"></a>

Get a DataFrame containing information about other assets (e.g., ETFs) from the statements.

#### money_market_fund_dataframe<a name="money-market-fund-dataframe"></a>

Property to retrieve a DataFrame containing investment details for Money Market Funds.

#### corporate_bonds_dataframe<a name="corporate-bonds-dataframe"></a>

Property to retrieve a DataFrame containing investment details for Corporate Bonds.

#### other_corporate_bonds_dataframe<a name="other-corporate-bonds-dataframe"></a>

Property to retrieve a DataFrame containing investment details for other Corporate Bonds.

#### treasuries_dataframe<a name="treasuries-dataframe"></a>

Property to retrieve a DataFrame containing investment details for U.S. Treasuries.

### Methods<a name="methods"></a>

#### swap_statement(new_file_name)<a name="swap-statement"></a>

Swap the PDF content with a new PDF file.

- `new_file_name`: The name of the new PDF file.

## Initialization<a name="initialization"></a>

The script is initialized by reading the most recent Schwab statement and creating an instance of the `PDFScraper` class, allowing you to work with the extracted data.

---

This script provides a powerful tool for extracting and analyzing investment data from Schwab statements. It offers flexibility in processing data for various asset types and can be a valuable asset for financial analysis and reporting.

For more information on how to use the script and its methods, refer to the code comments and documentation provided for each function and class.
