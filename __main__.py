from PythonScripts.portfolio import portfolio


def print_script_version() -> None:
    current_version = "2.2.0"
    print(f"PDF Scraper and Portfolio Analysis (Version {current_version})\n\n")


def main():
    print_script_version()  # Print Current Version of Script
    portfolio.export_to_excel()  # Export all Data to Excel


if __name__ == "__main__":
    main()
