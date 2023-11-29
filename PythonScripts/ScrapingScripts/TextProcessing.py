from typing import List, Optional
import pandas as pd

import PythonScripts.ScrapingScripts.FileManagement as FileManagement


# _________________________Text Line Sorting_________________________
def sort_transactions_from_text_lines(transaction_text_lines: List[str]) -> List[str]:
    sorted_text_lines = []
    start_of_section = transaction_text_lines.index("Total Amount") + 1

    symbols = [line.split(": ")[-1] for line in transaction_text_lines if line.find(": ") != -1]
    print(symbols)

    for text_line in transaction_text_lines[start_of_section:]:

        if "Reinvested Shares" in text_line:
            asset_data = text_line.replace("Reinvested Shares ", "")
            asset_name = asset_data.split(": ")[0]

            sorted_text_lines += ["Reinvested Shares", asset_name]
            continue

        sorted_text_lines.append(text_line)

    return sorted_text_lines


def sort_asset_classes_from_text_lines(page_text: str, asset: str, partial_section_name: str) -> Optional[List[str]]:
    """
    Extract and process the text lines related to a specific asset from a PDF page.

    :param page_text: Text content of a PDF page.
    :param asset: The asset type to extract.
    :param partial_section_name: The partial name of the asset section.
    :return: A list of cleaned and processed text lines related to the asset, or None if the asset is not found.
    """

    asset_page_data = page_text

    # Check if the asset is present on the page
    if asset not in asset_page_data:
        return None

    # Remove text after the end of the asset section
    end_of_section = f"Total {asset}"
    if end_of_section in asset_page_data:
        page_text = asset_page_data[:asset_page_data.index(end_of_section)]

    # Find the start of the asset section
    first_start_of_section_index = asset_page_data.index(partial_section_name) + len(partial_section_name) + 1
    asset_page_data = page_text[first_start_of_section_index:]

    if asset not in asset_page_data:
        return None

    second_start_of_section_index = asset_page_data.index(asset) + len(asset) + 1
    asset_page_data = asset_page_data[second_start_of_section_index:]

    # Get line items to remove from the config
    line_items_to_remove = FileManagement.config["Line Items to Remove"] + ["(continued)", "[Non-Sweep]"]

    # Process and clean the text lines
    reduced_text_lines = [line.strip() for line in asset_page_data.split("\n") if not line.startswith(
        tuple(line_items_to_remove)) and line]

    return reduced_text_lines


def sort_miscellaneous_values_from_text_lines(page_text: str, start: str, end: str) -> List[str]:
    """
    Extract and clean text lines related to cash transactions summary from a PDF page.
    """

    # Extract the relevant section based on the start and end points
    section_text = page_text[page_text.index(start):page_text.index(end)]

    # Split the section into lines and remove empty or whitespace-only lines
    text_lines = [line.strip() for line in section_text.split("\n") if line.strip()]

    return text_lines


# _________________________Value Conversions_________________________
def convert_values_from_columns_to_numeric(df: pd.DataFrame, columns: List[str], exceptions: List[str]) -> None:
    """
    Clean and convert specified columns in a Pandas DataFrame to numeric format.

    This function processes the values in the specified columns, removing trailing ' S', commas, and '$ ' from the
    values. Additionally, it handles negative values enclosed in parentheses, converting them to their negative
    numeric counterparts.
    """
    # Define a custom function to clean and convert values
    def clean_and_convert(value):
        value = str(value)
        value = value.rstrip(' S').replace(",", "").replace("$ ", "")
        value = value.replace("<", "").replace("%", "")
        if value.startswith('(') and value.endswith(')'):
            return -float(value[1:-1])

        return float(value)

    # Apply the custom function to the specified columns
    adjusted_columns = [x for x in columns if x not in exceptions]
    df[adjusted_columns] = df[adjusted_columns].applymap(clean_and_convert)


def convert_text_lines_to_dataframe(text_lines: List[str], columns: List[str], exceptions: List[str]):
    """
    Clean and convert specified columns in a Pandas DataFrame to numeric format.

    This function processes the values in the specified columns, removing trailing ' S', commas, and '$ ' from the
    values. Additionally, it handles negative values enclosed in parentheses, converting them to their negative
    numeric counterparts.
    """

    n_columns = len(columns)
    data = {col: [] for col in columns}

    for index, line in enumerate(text_lines):
        column_index = columns[index % n_columns]
        data[column_index].append(line)

    dataframe = pd.DataFrame(data).set_index(columns[0])
    convert_values_from_columns_to_numeric(dataframe, columns[1:], exceptions)

    return dataframe
