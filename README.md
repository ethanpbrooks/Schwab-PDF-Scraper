# PDF Financial Data Scraper

The PDF Financial Data Scraper is a Python tool designed to extract and process investment data from PDF documents, particularly tailored for Schwab statements. It allows you to extract data related to various asset types, such as stocks, fixed income, options, and more, and convert it into structured Pandas DataFrames for further analysis.

## Table of Contents

- [PDF Financial Data Scraper](#pdf-financial-data-scraper)
- [Features](#features)
- [Installation](#installation)
- [Configuration File](#configuration)
- [Usage](#usage)
   - [Extracting Investment Data](#extracting-investment-data)
      - [Equity Investment Data](#equity-investment-data)
      - [Asset Composition](#asset-composition)
   - [Portfolio Analysis Tool](#portfolio-analysis-tool)
      - [Portfolio Class](#portfolio-class)
      - [Custom Analysis Class](#custom-analysis-class)
   - [PDF Scraper Options](#pdf-scraper-options)
- [About the Author](#about-the-author)
   - [Background](#background)
   - [Contact Information](#contact-information)

## Features

- Extract investment data from PDF documents.
- Process data related to different asset types, including stocks, fixed income, options, and more.
- Convert extracted data into Pandas DataFrames for easy analysis.
- Retrieve asset composition information.
- Handle various financial instruments present in Schwab statements.

## Installation

1. Clone the repository to your local machine:

   ```pycon
   git clone https://github.com/ethanpbrooks/pdf-financial-scraper.git
   ```

2. Change the directory to the project folder

   ```pycon
   cd pdf-financial-scraper
   ```
   
3. Install the required Python packages

   ```pycon
   pip install -r requirements.txt
   ```

## Configuration

To use the PDF Financial Data Scraper, you'll need to configure the `config.json` file with your specific data. Please note that while we provide a template for these sections, we cannot display the actual content due to confidentiality or privacy reasons.

```json
{
  "Schwab Portfolio Statements": {
    "Most Recent": "",
    "One Month": "",
    "Year-to-Date": "",
    "One Year": "",
    "Three Year": "",
    "Five Year": ""
  },

  "Fixed Income ETFs": [
    ""
  ],

  "Line Items to Remove": [
    ""
  ],

  "Asset Types as Shown per Section": {
    "": ""
  },

  "Symbols Corresponding to Each Asset Type": {
    "": ""
  }
}
```

#### Asset Types as Shown per Section

The "Asset Types as Shown per Section" section defines how different asset types are labeled in your statements. It should follow this format:

```json
{
  "Asset Types as Shown per Section": {
    "Equities": "Equities",
    "Exchange Traded Funds": "Exchange Traded Funds",
    "...": "..."
  }
}
```

#### Symbols Corresponding to Each Asset Type

The "Symbols Corresponding to Each Asset Type" section specifies the symbols or identifiers associated with each asset type in your statements. It should follow this format:

```json
{
  "Symbols Corresponding to Each Asset Type": {
    "Equities": "SYMBOL: ",
    "Exchange Traded Funds": "SYMBOL: ",
    "...": "..."
  }
}
```

Please ensure that your actual configuration follows these formats while replacing the values with your specific data.

## Usage

### Extracting Investment Data

To access and analyze your investment data, you can utilize the instance of the **PDFScraper** class named `pdf_scraper`. This instance provides various properties that allow you to extract different types of investment data.

First, make sure you have imported the `pdf_scraper` instance into your script as shown below:

```pycon
from MainScripts.PDFScraper import pdf_scraper
```
Now, you can easily retrieve specific investment data as follows:

#### Equity Investment Data
To obtain equity investment data, including information about stocks and shares, you can use the equity_dataframe property:

```pycon
# Retrieve Equity investment data as a DataFrame
equity_data = pdf_scraper.equity_dataframe
```

The equity_dataframe property returns a pandas DataFrame containing details about your equity investments, such as symbol, name, quantity, and price.

#### Asset Composition
The asset_composition property provides an overview of your portfolio's asset composition. It extracts data related to different asset types, such as stocks, fixed income, ETFs, and more:

```pycon
# Retrieve asset composition data as a DataFrame
asset_composition = pdf_scraper.asset_composition
```

The resulting DataFrame includes information about the type of assets in your portfolio and their respective market values.

With these properties, you can effortlessly access and work with your investment data to perform various analyses and make informed financial decisions.

## Portfolio Analysis Tool

This project includes a complimentary module called **PortfolioAnalysis**, which provides a powerful toolset for analyzing and managing your investment portfolio. The core of this module is the **Portfolio** class, designed to help you perform various calculations and analysis on your investment data.

### Portfolio Class

The **Portfolio** class offers a wide range of functionalities for portfolio analysis, including:

- Calculation of portfolio performance metrics such as returns, volatility, and risk measures.
- Diversification analysis to assess asset allocation.
- Optimization techniques to find the optimal asset mix for your investment goals.
- Visualization tools for generating informative charts and reports.

### Custom Analysis Class

While the **Portfolio** class in **PortfolioAnalysis** covers a broad spectrum of portfolio analysis needs, we understand that you may have specific requirements or custom analysis methods. That's why we offer you the flexibility to create your own analysis class and integrate it seamlessly with the project. You can extend and customize the analysis functionality to suit your unique investment strategies and objectives.

### PDF Scraper Options

In addition to the portfolio analysis capabilities, this project provides options for PDF scraping to extract investment data from your financial statements. The **PDFScraper** class is responsible for extracting and processing data from PDF documents. While the default implementation is included, you also have the freedom to change the PDF scraper to suit your needs.

Whether you choose to use the built-in PDF scraper or develop your custom one, this project is designed to give you the flexibility to tailor your investment analysis and data extraction processes to your preferences.

## About the Author

I'm Ethan Brooks, and I currently serve as the Co-Managing Director of Barry University's Student Managed Investment Fund (SMIF). As a computer science major with a specialization in data analysis, I've combined my passion for technology with my interest in finance to develop and maintain the PDF Financial Data Scraper project.

### Background

- **Location:** Miami, Florida
- **Role:** Co-Managing Director at Barry University's SMIF

### Disclaimer

Please note that I am a student, and while I have designed and implemented this tool to the best of my abilities, it is essential to exercise caution and verify the extracted data for accuracy. Investment decisions should be made based on thorough analysis and consultation with financial professionals.

### Contact Information

If you have any questions, or suggestions, please feel free to reach out to me:

- Email: [ethan.brooks@mymail.barry.edu](mailto:ethan.brooks@mymail.barry.edu)
- LinkedIn: [Ethan Brooks](https://www.linkedin.com/in/ethan-brooks-11706a14a/)

Thank you for using the PDF Financial Data Scraper, and I hope it proves to be a valuable tool for your investment analysis needs.
