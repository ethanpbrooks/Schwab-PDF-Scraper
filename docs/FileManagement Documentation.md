# Schwab Portfolio Statements Processor

## Overview

This Python script is designed to process Schwab Portfolio Statements in PDF format. It performs various tasks including extracting data from the statements, validating statement filenames, and more. This documentation provides an overview of the script's structure, functions, and usage.

## Table of Contents

- [File Structure](#file-structure)
- [Configuration](#configuration)
- [Functions](#functions)
  - [extract_schwab_statements](#extract_schwab_statements)
  - [extract_fixed_income_etf_tickers](#extract_fixed_income_etf_tickers)
  - [validate_statement_files](#validate_statement_files)
  - [validated_file_path](#validated_file_path)

## File Structure

The script consists of the following components:

- **Main Script**: The main script is responsible for processing Schwab Portfolio Statements. It includes functions to read configuration files, validate statement filenames, and perform various data extraction tasks.

- **Configuration File (`config.json`)**: This JSON file stores configuration data used by the script, such as Schwab Portfolio Statements information and fixed income ETF tickers.

- **Statements Directory (`Statements`)**: This folder contains the PDF statement files that need to be processed. The script validates and extracts data from these files.

## Configuration

Before running the script, you should configure the `config.json` file to specify Schwab Portfolio Statements and fixed income ETF information. Here's how to configure it:

- `Schwab Portfolio Statements`: Define the structure of Schwab Portfolio Statements as a dictionary in the configuration file. This structure is used for data extraction.

- `Fixed Income ETFs`: Specify a list of fixed income ETF tickers that the script will use.

## Functions

### `extract_schwab_statements`

This function extracts the "Schwab Portfolio Statements" dictionary from the `config.json` file. The extracted information is used to structure and extract data from the statements.

### `extract_fixed_income_etf_tickers`

This function extracts a list of fixed income ETF tickers from the `config.json` file. These tickers are used in data processing.

### `validate_statement_files`

This function validates the PDF statement filenames in the `Statements` folder. It checks if the filenames follow the expected format, including the year and month. Invalid filenames result in a `ValueError` with an informative message.

### `validated_file_path`

This function validates and retrieves the full file path for a PDF statement. It takes a base file name, appends it to the statement folder path, and checks if the corresponding PDF file exists. If the file is found, it returns the full file path; otherwise, it raises a `ValueError`.

## Usage

To use this script:

1. Configure the `config.json` file with the appropriate information for Schwab Portfolio Statements and fixed income ETFs.

2. Ensure that the PDF statement files are placed in the `Statements` folder with filenames in the format 'YYYY-Month.pdf'.

3. Run the script to process the statements and extract data.

## Conclusion

This Python script provides a structured way to process Schwab Portfolio Statements and extract relevant data. By following the configuration guidelines and using the provided functions, you can efficiently work with financial data from these statements.
