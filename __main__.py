from MainScripts.PorfolioAnalysis import portfolio


def main():
    risk_measurements = portfolio.calculate_risk_measurements()
    print(risk_measurements, "\n\n")

    asset_allocation = portfolio.asset_allocation
    print(asset_allocation)


if __name__ == "__main__":
    main()
