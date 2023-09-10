import pandas as pd
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ExcelExporter:
    writer: pd.ExcelWriter
    row_offset: int

    def add_dataframe(self, dataframe: pd.DataFrame, sheet_name: str, space_rows: int = 0):
        """
        Add a DataFrame to the Excel file.

        :param dataframe: The DataFrame to be added to the Excel file.
        :type dataframe: pd.DataFrame
        :param sheet_name: The name of the sheet where the DataFrame will be placed.
        :type sheet_name: str
        :param space_rows: Number of empty rows to insert after this DataFrame (default is 0).
        :type space_rows: int
        """
        # Write the DataFrame to the sheet
        dataframe.to_excel(self.writer, sheet_name=sheet_name, index=False, startrow=self.row_offset)

        # Update the row offset for the next DataFrame
        self.row_offset += len(dataframe) + space_rows

    def add_dataframes(self, dataframes: List[pd.DataFrame], space_rows: int = 0):
        """
        Add multiple DataFrames to the same sheet in the Excel file.

        :param dataframes: A list of DataFrames to be added to the Excel file.
        :type dataframes: List[pd.DataFrame]
        :param space_rows: Number of empty rows to insert between DataFrames (default is 0).
        :type space_rows: int
        """
        # Create a Pandas Excel writer object
        for i, dataframe in enumerate(dataframes):
            # Write the DataFrame to the Excel file
            dataframe.to_excel(self.writer, sheet_name='Sheet1', startrow=i * (len(dataframe) + space_rows), index=False)


    def save(self):
        """
        Save the Excel file with added DataFrames.

        This method should be called after adding all desired DataFrames to the ExcelExporter instance.
        """
        self.writer.save()
