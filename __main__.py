from Scripts.PorfolioAnalysis import portfolio
import pandas as pd


def mainfff():
    dataframes = {
        "Returns over Time": portfolio.portfolio_returns,
        "Asset Allocation": portfolio.asset_composition,
        "Equities": portfolio.equities,
        "Fixed Income ETFs": portfolio.fixed_income_etf,
        "Corporate Bonds": portfolio.corporate_bonds,
        "U.S. Treasuries": portfolio.treasuries,
        "Money Market Funds": portfolio.money_market_funds,
        "Mutual Funds": portfolio.mutual_funds,
        "Options": portfolio.options
    }

    # Create an ExcelWriter object
    with pd.ExcelWriter('Excel Outputs/output.xlsx', engine='xlsxwriter') as writer:
        # Iterate through the dictionary and write each DataFrame with empty rows in between
        start_row = 0  # Start row counter

        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name='Sheet1', startrow=start_row, index=False, header=True)

            # Add empty rows (adjust as needed)
            empty_rows = pd.DataFrame({'': [''] * 2})
            empty_rows.to_excel(writer, sheet_name='Sheet1', startrow=start_row + len(df) + 2, header=False,
                                index=False)

            start_row += len(df) + 3  # Update the start row for the next DataFrame


def main():
    # x = portfolio.calculate_monthly_returns()
    # y = portfolio.asset_composition
    x = portfolio.portfolio_returns
    print(x)


if __name__ == "__main__":
    main()
