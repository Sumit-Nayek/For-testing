
import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = (
    "https://en.wikipedia.org/wiki/"
    "List_of_countries_and_dependencies_by_population"
)

driver = None

try:
    # 1. Configure Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Selenium Manager manages the driver when possible
    driver = webdriver.Chrome(options=options)

    # 2. Open the website
    driver.get(URL)

    # 3. Wait until the table appears
    wait = WebDriverWait(driver, 20)
    table = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "table.wikitable")
        )
    )

    # 4. Extract the table headers
    rows = table.find_elements(By.CSS_SELECTOR, "tr")

    header_row = next(
        row for row in rows
        if row.find_elements(By.TAG_NAME, "th")
    )

    headers = [
        cell.text.strip().lower()
        for cell in header_row.find_elements(By.TAG_NAME, "th")
    ]

    print("Headers:", headers)

    # 5. Identify the required columns
    country_index = next(
        i for i, col in enumerate(headers)
        if "location" in col or "country" in col
    )

    population_index = next(
        i for i, col in enumerate(headers)
        if "population" in col
    )

    # 6. Extract country and population values
    records = []

    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, "th, td")

        if len(cells) <= max(country_index, population_index):
            continue

        country = cells[country_index].text.strip()
        population = cells[population_index].text.strip()

        # Skip the header and empty records
        if country.lower() in ("location", "country") or not country:
            continue

        records.append({
            "country": country,
            "population": population
        })

    # 7. Convert extracted records into a DataFrame
    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError("No records extracted from the table")

    # 8. Clean country names
    df["country"] = df["country"].astype("string").str.strip()

    # 9. Clean population values and convert to numbers
    df["population"] = (
        df["population"]
        .astype("string")
        .str.replace(",", "", regex=False)
        .str.replace(r"\[.*?\]", "", regex=True)
        .str.strip()
    )

    df["population"] = pd.to_numeric(
        df["population"],
        errors="coerce"
    )

    # 10. Remove missing values and duplicates
    df = df.dropna(subset=["country", "population"])
    df = df[df["country"] != ""]
    df = df.drop_duplicates(subset=["country"])

    # 11. Convert to integer and sort
    df["population"] = df["population"].astype("int64")
    df = df.sort_values("population", ascending=False)

    # 12. Export to Excel
    df.to_excel("country_population_selenium.xlsx", index=False)

    print("\nTop 10 countries:")
    print(df.head(10).to_string(index=False))
    print("\nTotal records:", len(df))
    print("Excel file saved successfully!")

except Exception as error:
    print("Scraping failed:", error)

finally:
    if driver is not None:
        driver.quit()

