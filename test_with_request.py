
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

# 1. Fetch website HTML
url = "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=20
)
response.raise_for_status()
print(response)

# 2. Parse HTML
soup = BeautifulSoup(response.text, "html.parser")

print(soup)
# 3. Locate the main table
table = soup.find("table", class_="wikitable")

if table is None:
    raise ValueError("Population table not found")

print(table)
# 4. Convert HTML table to DataFrame
df = pd.read_html(StringIO(str(table)))[0]

print(df)
# 5. Inspect available columns
print("Original columns:", df.columns.tolist())

# 6. Standardize column names
df.columns = [
    str(col).strip().lower().replace(" ", "_")
    for col in df.columns
]

print(df.columns)


# Identify the country and population columns
country_col = next(
    col for col in df.columns
    if "location" in col or "country" in col
)

population_col = next(
    col for col in df.columns
    if "population" in col
)

# 7. Select relevant columns
df = df[[country_col, population_col]].copy()
df.columns = ["country", "population"]

# 8. Clean the data
df["country"] = (
    df["country"].astype("string").str.strip()
)

df["population"] = pd.to_numeric(
    df["population"].astype("string")
      .str.replace(",", "", regex=False)
      .str.replace(r"\[.*?\]", "", regex=True)
      .str.strip(),
    errors="coerce"
)

# 9. Handle missing values and duplicates
df = df.dropna(subset=["country", "population"])
df = df[df["country"] != ""]
df = df.drop_duplicates(subset=["country"])

# 10. Transform and sort
df["population"] = df["population"].astype("int64")
df = df.sort_values("population", ascending=False)

# 11. Export
df.to_excel("country_population.xlsx", index=False)

print(df.head(10))
print("Total records:", len(df))
print("File saved successfully!")