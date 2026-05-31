import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

CSV_FILE = "bets_data.csv"

url = "https://www.footballsuper.tips/football-accumulators-tips/football-tips-prediction-of-the-day/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(url, headers=headers, timeout=15)

soup = BeautifulSoup(r.text, "html.parser")
text = soup.get_text("\n", strip=True)

lines = [x.strip() for x in text.split("\n") if x.strip()]

odd_index = None

for i, line in enumerate(lines):
    if "Total Odd" in line:
        odd_index = i
        break

if odd_index is None:
    raise Exception("FS TIP NOT FOUND")

odds_match = re.search(
    r"Total Odd[:\s]+([0-9]+(?:\.[0-9]+)?)",
    lines[odd_index]
)

odds = float(odds_match.group(1))

tip_line = lines[odd_index - 4]
match_line = lines[odd_index - 2]
league_line = lines[odd_index - 1]

selection = f"{match_line} - {tip_line}"

new_row = {
    "Data": datetime.now().strftime("%d.%m.%Y"),
    "Liga": "FS TIPS",
    "Selekcja": selection,
    "Kurs": odds,
    "Stawka": 100,
    "Wynik": "WAIT",
    "Profit": 0,
    "Profit skumulowany": 0,
    "Bankroll": 0,
    "Notatka": f"Auto FS Tips | {league_line}"
}

try:
    df = pd.read_csv(CSV_FILE)
except:
    df = pd.DataFrame()

df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

df.to_csv(CSV_FILE, index=False)

print("FS TIP ADDED")
