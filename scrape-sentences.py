import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import re

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; dataset-bot/1.0)"}

# -----------Clean sentences-----------
def clean_sentence(text):
    """Remove unwanted symbols, URLs, and filter length"""
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"[^A-Za-z0-9.,!?;:'\" ]+", "", text)  # keep letters/punctuation
    text = text.strip()
    if len(text.split()) < 4 or len(text.split()) > 30:  # filter too short/long
        return None
    return text

# ---------- Quotes to Scrape ----------
def scrape_quotes():
    sentences = []
    page_url = "http://quotes.toscrape.com/"
    while page_url:
        r = requests.get(page_url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        for q in soup.find_all("div", class_="quote"):
            text = q.find("span", class_="text")
            if text:
                sent = clean_sentence(text.get_text())
                if sent:
                    sentences.append((sent, "Quotes to Scrape"))

        next_btn = soup.find("li", class_="next")
        if next_btn:
            page_url = urljoin(page_url, next_btn.a["href"])
        else:
            page_url = None
    return sentences

# ---------- Books to Scrape (titles only) ----------
def scrape_books():
    sentences = []
    page_url = "http://books.toscrape.com/catalogue/page-1.html"
    while page_url:
        r = requests.get(page_url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")

        for book in soup.find_all("article", class_="product_pod"):
            title = book.h3.a["title"]
            sent = clean_sentence(title)
            if sent:
                sentences.append((sent, "Books to Scrape"))

        next_btn = soup.find("li", class_="next")
        if next_btn:
            page_url = urljoin(page_url, next_btn.a["href"])
        else:
            page_url = None
    return sentences

# ---------- Project Gutenberg ----------
def scrape_gutenberg():
    url = "https://www.gutenberg.org/files/11/11-0.txt"  # Alice in Wonderland
    r = requests.get(url, headers=HEADERS)
    text = r.text

    raw_sentences = re.split(r'[.!?]', text)
    sentences = []
    for s in raw_sentences:
        sent = clean_sentence(s)
        if sent:
            sentences.append((sent, "Project Gutenberg - Alice in Wonderland"))
    return sentences

# ---------- Main ----------
if __name__ == "__main__":
    data = []

    print("Scraping quotes...")
    data += scrape_quotes()
    print("Quotes collected:", len(data))

    print("Scraping books (titles only)...")
    data += scrape_books()
    print("Quotes + Books collected:", len(data))

    print("Scraping Gutenberg text...")
    data += scrape_gutenberg()
    print("Total sentences collected:", len(data))

    df = pd.DataFrame(data, columns=["sentence", "source"])
    df.to_csv("english_sentences.csv", index=False)
    df.to_excel("english_sentences.xlsx", index=False)

    print("✅ Saved", len(df), "sentences to english_sentences.csv / .xlsx")
