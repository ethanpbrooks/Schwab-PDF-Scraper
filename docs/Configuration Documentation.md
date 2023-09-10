# Configuration File Documentation

This configuration file is used in conjunction with the PDF Statement Data Extractor and Analyzer script. It contains settings and information necessary for the script to extract and process financial data from PDF statements.

## Schwab Portfolio Statements

The **Schwab Portfolio Statements** section specifies the names of Schwab portfolio statements to be used for data extraction. Each statement is associated with a predefined key, making it easier to select statements based on different criteria or time periods.

- `"Most Recent"`: The most recent Schwab portfolio statement.
- `"One Month"`: A statement for the previous month.
- `"Year-to-Date"`: A statement for the year-to-date period.
- `"One Year"`: A statement for the past year.
- `"Three Year"`: A statement for the past three years.
- `"Five Year"`: A statement for the past five years.

## Fixed Income ETFs

The **Fixed Income ETFs** section lists the ticker symbols of fixed income Exchange-Traded Funds (ETFs) that the script may encounter in the PDF statements. This information helps the script identify and process fixed income ETF data.

## Line Items to Remove

The **Line Items to Remove** section specifies a list of text elements that should be removed from the extracted PDF content. These elements are typically headers, footers, or other non-data text that should not be included in the analysis.

## Asset Types as Shown per Section

The **Asset Types as Shown per Section** section provides mappings between asset types and the labels as they appear in the sections of the PDF statements. This mapping is essential for identifying and processing data specific to each asset type.

- `"Equities"`: Label for equity investments.
- `"Exchange Traded Funds"`: Label for ETF investments.
- `"Other Assets"`: Label for other types of assets.
- `"Money Market Funds"`: Label for money market funds.
- `"Options"`: Label for options investments.
- `"Bond Funds"`: Label for bond funds.
- `"Equity Funds"`: Label for equity funds.
- `"U.S. Treasuries"`: Label for U.S. Treasuries.
- `"Corporate Bonds"`: Label for corporate bonds.
- `"Partial Call"`: Label for partial call investments.

## Symbols Corresponding to Each Asset Type

The **Symbols Corresponding to Each Asset Type** section defines the keywords or symbols used in the PDF statements to identify different asset types. This information is crucial for extracting and categorizing data correctly.

- `"Equities"`: Symbol for identifying equity investments.
- `"Exchange Traded Funds"`: Symbol for identifying ETF investments.
- `"Fixed Income"`: Symbol for identifying fixed income investments.
- `"Mutual Funds"`: Symbol for identifying mutual fund investments.
- `"Partial Call"`: Symbol for identifying partial call investments.
- `"Money Market Funds"`: Symbol for identifying money market fund investments.
- `"Options"`: Symbol for identifying options investments.

Please ensure that the information in this configuration file is accurate and corresponds to the format of the PDF statements you intend to analyze.
