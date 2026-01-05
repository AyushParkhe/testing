import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import os
import os

def ensure_data_dir():
    if not os.path.exists("data1"):
        os.makedirs("data1")
ensure_data_dir()


# -----------------------------
# CONFIGURATION
# -----------------------------
BASE_URL = "https://internshala.com/internships/"
OUTPUT_FILE = "data1/internships.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}


PAGES_TO_SCRAPE = 3        # pages 1 to 3 (≈ 50–60 internships)
REQUEST_DELAY = 5          # seconds between page requests


# -----------------------------
# HELPER FUNCTION
# -----------------------------
def safe_text(element):
    """Extract clean text safely"""
    return element.text.strip() if element else "Not Mentioned"


# -----------------------------
# MAIN SCRAPER FUNCTION
# -----------------------------
def scrape_internshala():
    print("Scraping started at:", datetime.now())

    all_data = []

    for page in range(1, PAGES_TO_SCRAPE + 1):
        try:
            if page == 1:
                url = BASE_URL
            else:
                url = f"{BASE_URL}page-{page}/"

            print(f"Scraping page {page}: {url}")

            response = requests.get(url, headers=HEADERS, timeout=20)
            print("Status code:", response.status_code)
            print("Page length:", len(response.text))

            if response.status_code != 200:
                print("Failed to fetch page:", page)
                continue

            soup = BeautifulSoup(response.text, "lxml")

            internships = soup.find_all(
                "div",
                class_="individual_internship"
            )

            print("Internships found on page:", len(internships))

            for intern in internships:
                try:
                    title = safe_text(
                        intern.find("h3", class_="job-internship-name")
                    )

                    company = safe_text(
                        intern.find("div", class_="company_name")
                    )

                    location = safe_text(
                        intern.find("span", class_="locations")
                    )

                    stipend = safe_text(
                        intern.find("span", class_="stipend")
                    )

                    duration = safe_text(
                        intern.find("span", class_="duration")
                    )

                    link_tag = intern.find("a", class_="job-title-href")
                    apply_link = (
                        "https://internshala.com" + link_tag["href"]
                        if link_tag and link_tag.get("href")
                        else "Not Available"
                    )

                    all_data.append({
                        "title": title,
                        "organization": company,
                        "location": location,
                        "stipend": stipend,
                        "duration": duration,
                        "type": "Internship",
                        "source": "Internshala",
                        "apply_link": apply_link,
                        "last_scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                except Exception as e:
                    print("Error parsing internship:", e)

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print("Error scraping page", page, ":", e)

    return all_data


# -----------------------------
# SAVE DATA (NO DUPLICATES)
# -----------------------------
def save_to_csv(new_data):
    os.makedirs("data1", exist_ok=True)

    new_df = pd.DataFrame(new_data)

    if os.path.exists(OUTPUT_FILE):
        old_df = pd.read_csv(OUTPUT_FILE)

        # Remove duplicates using apply_link
        combined_df = pd.concat([old_df, new_df])
        combined_df.drop_duplicates(
            subset=["apply_link"],
            keep="last",
            inplace=True
        )
    else:
        combined_df = new_df

    combined_df.to_csv(OUTPUT_FILE, index=False)
    print("Saved records:", len(combined_df))


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    data1 = scrape_internshala()
    save_to_csv(data1)
    df.to_csv("data/internships.csv", index=False)
    print("Scraping completed at:", datetime.now())
