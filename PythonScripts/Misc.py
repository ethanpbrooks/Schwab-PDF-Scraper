from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def calculate_statement_periods_to_analyze(start_date):
    """
    Calculate a range of month-year strings given a start date and a number of months.

    :param start_date: A string representing the start date in the format "YYYY-B".
    :return: A list of month-year strings.
    """

    # Convert the input string to a datetime object
    start_date = datetime.strptime(start_date, "%Y-%B")

    # Generate the list of datetime values
    result_dates = [
        (start_date - relativedelta(months=i)).strftime("%Y-%B")
        for i in [0, 3, start_date.month, 12, 12 * 3, 12 * 5]  # Subtracting months in multiples of 12 (years)
    ]

    return result_dates


def calculate_month_range(start_date, num_months):
    """
    Calculate a range of month-year strings given a start date and a number of months.

    :param start_date: A string representing the start date in the format "YYYY-B".
    :param num_months: The number of months to calculate.
    :return: A list of month-year strings.
    """

    # Convert the input string to a datetime object
    start_date = datetime.strptime(start_date, "%Y-%B")

    # Create an empty list to store the result
    result = []

    # Subtract months and add them to the result list
    for _ in range(num_months + 1):
        result.append(start_date.strftime("%Y-%B"))
        # Subtract one month (approximately 30 days)
        start_date = start_date - timedelta(days=30)

    return result
