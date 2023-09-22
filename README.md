# PDF Financial Data Scraper

The PDF Financial Data Scraper is a Python tool designed to extract and process investment data from PDF documents, particularly tailored for Schwab statements. It allows you to extract data related to various asset types, such as equities, fixed income, options, and more, and convert it into structured Pandas DataFrames for further analysis.

## Table of Contents

- [PDF Financial Data Scraper](#pdf-financial-data-scraper)
- [Features](#features)
- [Installation](#installation)
   - [Clone the Repository](#clone-the-repository)
   - [Change Directory](#change-directory)
   - [Install Required Packages](#install-required-packages)
- [Configuration File](#configuration)
- [Usage](#usage)
   - [Extracting Investment Data](#extracting-investment-data)
      - [Equity Investment Data](#equity-investment-data)
      - [Asset Composition](#asset-composition)
   - [Portfolio Analysis Tool](#portfolio-analysis-tool)
      - [Portfolio Class](#portfolio-class)
      - [Custom Analysis Class](#custom-analysis-class)
   - [PDF Scraper Options](#pdf-scraper-options)
- [Documentation](#documentation)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [About the Author](#about-the-author)
   - [Background](#background)
   - [Project Goals](#project-goals)
   - [Contact Information](#contact-information)

## Features

- Extract investment data from PDF documents.
- Process data related to different asset types, including equities, fixed income, options, and more.
- Convert extracted data into Pandas DataFrames for easy analysis.
- Retrieve asset composition information.
- Handle various financial instruments present in Schwab statements.

## Installation

1. Clone the repository to your local machine:

   ```pycon
   git clone https://github.com/yourusername/pdf-financial-scraper.git
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

Please note that you will need to fill out the data in this config.json file based on your specific Schwab portfolio statements and asset configurations. Replace the empty strings with the actual file names, settings, line items to remove, asset type mappings, and symbols corresponding to each asset type as needed for your use case.
Before you can use the PDFScraper for processing Schwab portfolio statements, you need to create a `config.json` file in the MainScripts directory of your project with the following structure:


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
The asset_composition property provides an overview of your portfolio's asset composition. It extracts data related to different asset types, such as equities, fixed income, ETFs, and more:

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
- **Experience:** I manage over $1 million as part of my responsibilities at Barry University's SMIF. My expertise in computer science and data analysis has allowed me to leverage technology to enhance our investment strategies and decision-making processes.

### Project Goals

The PDF Financial Data Scraper project was born out of my desire to streamline the process of extracting and analyzing investment data from PDF documents, particularly tailored for Schwab statements. I believe that technology can play a crucial role in making data-driven financial decisions, and this project is a testament to that vision.

### Contact Information

If you have any questions, suggestions, or would like to collaborate on this project, please feel free to reach out to me:

- Email: [ethan.brooks@example.com](mailto:ethan.brooks@mymail.barry.edu)
- LinkedIn: [Ethan Brooks](https://www.linkedin.com/in/ethan-brooks-11706a14a/)

Thank you for using the PDF Financial Data Scraper, and I hope it proves to be a valuable tool for your investment analysis needs.
