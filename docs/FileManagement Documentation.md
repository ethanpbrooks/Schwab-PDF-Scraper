# Financial Data Processing Script Documentation

## Overview

This script is designed for processing financial data, specifically related to portfolio statements. It handles various tasks such as extracting information from configuration files, cleaning text data from PDF statements, and validating statement files.

## Table of Contents

1. [File Paths](#file-paths)
2. [Logging Configuration](#logging-configuration)
3. [Asset Types](#asset-types)
4. [Function: `symbol_corresponding_to_asset`](#function-symbol_corresponding_to_asset)
5. [Function: `clean_text_lines_from_page`](#function-clean_text_lines_from_page)
6. [Function: `extract_schwab_statements`](#function-extract_schwab_statements)
7. [Function: `extract_fixed_income_etf_tickers`](#function-extract_fixed_income_etf_tickers)
8. [Function: `validate_statement_files`](#function-validate_statement_files)
9. [Function: `validated_file_path`](#function-validated_file_path)

## 1. File Paths <a name="file-paths"></a>

- `_config_file_path`: Path to the configuration file.
- `_statements_directory_path`: Path to the directory containing statement files.
- `_statement_folder_path`: Path to the folder containing statement files.

## 2. Logging Configuration <a name="logging-configuration"></a>

- `logging.basicConfig()`: Configures logging settings.
- `logger`: Creates a logger instance for the current module.

## 3. Asset Types <a name="asset-types"></a>

- Defines various asset types used in the script, such as equities, treasuries, corporate bonds, etc.
- `all_asset_types`: A list of all defined asset types.
- `asset_types_as_shown_per_section`: A dictionary mapping asset types to their representation in configuration.

## 4. Function: `symbol_corresponding_to_asset` <a name="function-symbol_corresponding_to_asset"></a>

- **Description**: Retrieves the symbol corresponding to a given asset type.
- **Parameters**:
  - `asset` (str): The asset type for which to retrieve the symbol.
- **Returns**: The symbol corresponding to the input asset type (str).
- **Raises**:
  - `KeyError`: If the input asset type is not found in the configuration.

## 5. Function: `clean_text_lines_from_page` <a name="function-clean_text_lines_from_page"></a>

- **Description**: Cleans text lines from a page by removing specified line items.
- **Parameters**:
  - `text_lines` (List[str]): List of text lines from a page.
  - `asset` (str): The asset string to identify lines to retain.
- **Returns**: Cleaned list of text lines (Optional[List[str]]).
- **Notes**: It retains lines that start with the 'asset' string and stops processing when it encounters a line indicating the end of sections.

## 6. Function: `extract_schwab_statements` <a name="function-extract_schwab_statements"></a>

- **Description**: Extracts the "Schwab Portfolio Statements" dictionary from the configuration file.
- **Returns**: The "Schwab Portfolio Statements" dictionary from the configuration.

## 7. Function: `extract_fixed_income_etf_tickers` <a name="function-extract_fixed_income_etf_tickers"></a>

- **Description**: Extracts a list of fixed income ETF tickers from the configuration file.
- **Returns**: A list of fixed income ETF tickers.

## 8. Function: `validate_statement_files` <a name="function-validate_statement_files"></a>

- **Description**: Validates the PDF statement files in the specified folder.
- **Returns**: True if all filenames are valid, False otherwise.
- **Raises**:
  - `ValueError`: If a filename does not match the expected format.

## 9. Function: `validated_file_path` <a name="function-validated_file_path"></a>

- **Description**: Validates and retrieves the full file path for a PDF statement.
- **Parameters**:
  - `base_file_name` (str): The base name of the PDF statement file.
- **Returns**: The full file path for the PDF statement.
- **Raises**:
  - `ValueError`: If the specified PDF file does not exist in the statement folder.
