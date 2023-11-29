from typing import List
import PythonScripts.ScrapingScripts.FileManagement as FileManagement


def extract_symbols_corresponding_to_assets(asset: str) -> str:
    """
    Get the symbol corresponding to a given asset type.

    This function takes an asset type as input and checks if it exists in
    the 'asset_types_as_shown_per_section' dictionary. If it does, it
    translates the asset name to the corresponding section name and
    retrieves the symbol for that asset type from the 'config' dictionary.

    :param asset: The asset type for which to retrieve the symbol.
    :type asset: str
    :return: The symbol corresponding to the input asset type.
    :rtype: str
    :raises KeyError: If the input asset type is not found in the 'asset_types_as_shown_per_section' dictionary.
    """
    if asset not in FileManagement.asset_types_as_shown_per_section:
        raise KeyError(f"'{asset}' not found in configuration file!")

    if asset == "Other Fixed Income":
        return FileManagement.config["Symbols Corresponding to Each Asset Type"]["Partial Call"]

    translated_asset_name = FileManagement.asset_types_as_shown_per_section[asset]
    return FileManagement.config["Symbols Corresponding to Each Asset Type"][translated_asset_name]


def extract_asset_data_from_text_lines(text_lines: List[str], asset: str) -> List[tuple]:
    """
    Extract asset data from a list of text lines.

    This function takes a list of text lines and extracts relevant data for a
    specific asset type. It identifies the asset symbol keyword, extracts the
    corresponding symbols, and processes the data lines accordingly.

    Note: Assumes that the input data has been previously validated for accuracy
    and consistency.

    :param text_lines: List of text lines to extract data from.
    :type text_lines: List[str]
    :param asset: The asset type for which to extract data.
    :type asset: str
    :return: List of tuples containing extracted asset data.
    :rtype: List[tuple]
    """
    # Get the asset symbol keyword
    asset_symbol_keyword = extract_symbols_corresponding_to_assets(asset)

    # Extract symbols and their indices
    symbols = [line.split(asset_symbol_keyword)[-1] for line in text_lines if asset_symbol_keyword in line]
    symbol_indices = [0] + [text_lines.index(line) - 1 for line in text_lines if asset_symbol_keyword in line]

    data_list = []

    # Iterate through symbol indices to extract data
    for idx in symbol_indices[:-1]:
        starting_index = idx + 2 if idx > 0 else idx
        data_range = slice(starting_index, starting_index + 6)
        selected_asset_data: List[str] = [x for x in text_lines[data_range]]

        # Check if the first element is numeric and exclude it if necessary
        if selected_asset_data[0].replace(",", "").replace(".", "").isdigit():
            selected_asset_data = selected_asset_data[1:]

        data_list.append(selected_asset_data)

    # Determine the number of columns based on asset type
    n_of_columns = 4 if FileManagement.asset_types_as_shown_per_section[asset] in [
        "Fixed Income", "Options", "Other Fixed Income"] else 3

    # Create tuples with symbols and extracted data
    data_list = [tuple([symbol] + data[:n_of_columns]) for symbol, data in zip(symbols, data_list.copy())]

    return data_list
