from MainScripts.PorfolioAnalysis import portfolio
import numpy as np


def main():
    foo = portfolio.calculate_time_weighted_rate_of_return(3)
    print(foo)


if __name__ == "__main__":
    main()
