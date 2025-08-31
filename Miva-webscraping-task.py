#import libraries and tools
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

#set base url and header
BASE_URL = "http://quotes.toscrape.com/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; learning-bot/1.0; +https://example.com)"}

#create fetch function to handle HTTP GET request
def fetch(url):
    return requests.get(url, headers=HEADERS, timeout=10)

#create function to scrape quotes and author names
def scrape_all():
    all_quotes = []
    all_authors = []
    page_url = BASE_URL
    while page_url:
        print("Fetching", page_url)
        r = fetch(page_url)
        if r.status_code != 200:
            print("Failed:", r.status_code)
            break
        soup = BeautifulSoup(r.text, "html.parser")
        for q in soup.find_all("div", class_="quote"):
            text = q.find("span", class_="text").get_text(strip=True)
            author = q.find("small", class_="author").get_text(strip=True)
            all_quotes.append(text); all_authors.append(author)

        next_btn = soup.find("li", class_="next")
        if next_btn and next_btn.find("a"):
            page_url = urljoin(BASE_URL, next_btn.find("a")["href"])
            time.sleep(1)
        else:
            page_url = None

#create excel file to store quotes and authors
    df = pd.DataFrame({"quote": all_quotes, "author": all_authors})
    df.to_csv("quotes_all_pages.csv", index=False)
    print("Saved", len(df), "quotes.")

if __name__ == "__main__":
    scrape_all()
