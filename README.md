# PDF Statement Data Extractor and Analyzer

This Python script is designed to extract and analyze financial data from PDF statements, specifically tailored for Schwab statements. It provides functionality to read PDF files, extract text content, clean and process data, and convert it into Pandas DataFrames for further analysis.

## Features

- Extracts text content from PDF files.
- Processes financial data from Schwab statements, including asset composition, equities, fixed income, options, and more.
- Converts extracted data into Pandas DataFrames.
- Handles specific financial data cleaning, such as removing commas and converting values to numeric types.
- Supports swapping PDF content with a new file for analysis.

## Requirements

- Python 3.x
- Libraries: `fitz`, `os`, `pandas`, `logging`, and custom module `FileManagement` (provided separately).

## Usage

1. Clone the repository to your local machine.
2. Install the required Python libraries if you haven't already:

   ```bash
   pip install PyMuPDF pandas
3. Replace ./config.json with your configuration file if needed.
4. Place your Schwab PDF statements in the ./Statements directory.
5. Run the script:

   ```bash
   python your_script.py
6. The script will extract and process data from the most recent Schwab statement by default. You can swap the PDF content with a new file using the swap_statement method.

### Configuration
The script relies on a config.json file for configuration settings.
You can customize the list of statements to analyze and define line items to remove in the configuration file.

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgements
- This script was created for educational and personal use.
- The custom FileManagement module may include additional functions and configurations not covered in this README.

### Disclaimer
- This script is not intended for use in critical financial or investment decisions.
- Always verify the accuracy and reliability of the extracted data.

