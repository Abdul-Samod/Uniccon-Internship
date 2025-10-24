import requests
from bs4 import BeautifulSoup
import re
from openpyxl import Workbook

headers = {"User-Agent": "Mozilla/5.0"}

links = [
    "https://www.bbc.com/yoruba/articles/cq8x27gnkqpo",
    "https://www.bbc.com/yoruba/articles/c07ex973r2jo",
    "https://www.bbc.com/yoruba/articles/cvgeez9d5w0o",
    "https://www.bbc.com/yoruba/55964284",
    "https://www.bbc.com/yoruba/56369880",
    "https://www.bbc.com/yoruba/articles/cdey311d8ypo",
    "https://www.bbc.com/yoruba/articles/c74lm2dl82mo",
    "https://www.bbc.com/yoruba/articles/c1334jrv411o",
    "https://www.bbc.com/yoruba/articles/c0660lx262jo",
    "https://www.bbc.com/yoruba/articles/cn00q1p4z97o",
    "https://www.bbc.com/yoruba/articles/cyx1v2yw56no",
    "https://www.bbc.com/yoruba/articles/c3gm3prv8g4o",
    "https://www.bbc.com/yoruba/afrika-59779448",
    "https://www.bbc.com/yoruba/media-58828628",
    "https://www.bbc.com/yoruba/media-56118334",
    "https://www.bbc.com/yoruba/afrika-54884011",
    "https://www.bbc.com/yoruba/articles/c0klz0rjxydo", 
    "https://www.bbc.com/yoruba/articles/cp3ggd8j7k4o",
    "https://www.bbc.com/yoruba/afrika-60391949",
    "https://www.bbc.com/yoruba/afrika-60112178",
    "https://www.bbc.com/yoruba/56513156",
    "https://www.bbc.com/yoruba/afrika-54030716",
    "https://www.bbc.com/yoruba/afrika-53476830",
    "https://www.bbc.com/yoruba/agbaye-48709679",
    "https://www.bbc.com/yoruba/agbaye-48679504",
    "https://www.bbc.com/yoruba/articles/c0596q9d80vo",
    "https://www.bbc.com/yoruba/afrika-54023123",
    "https://www.bbc.com/yoruba/articles/c0mr91zy7rlo"
]

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Yoruba Health Data"
ws.append(["id", "title", "content", "URL"])  # header row

sentence_id = 1
for i, url in enumerate(links, start=1):
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f" ❌ Error fetching {url}: {e}")
        continue

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Title fallback
        title_tag = soup.find("h1") or soup.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"

        # Get paragraphs
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        full_text = " ".join(paragraphs)

        # Split into sentences
        sentences = re.split(r'(?<=[.?!])\s+', full_text)

        # Filter unwanted patterns
        unwanted_patterns = [
            "©",
            "BBC kò mọ̀ nípa",
            "End of Èyítí A Ń Kà Jùlọ",
            "Oríṣun àwòrán"
        ]

        for sentence in sentences:
            text = sentence.strip()
            if not text:
                continue
            if any(pattern in text for pattern in unwanted_patterns):
                continue
            ws.append([sentence_id, title, text, url])
            sentence_id += 1

        print(f" ✅ Saved article {i}: {title}")
    else:
        print(f" ⚠️ Failed to fetch {url} (status: {response.status_code})")

# Save Excel file
wb.save("yoruba_health.xlsx")
print("💾 Data saved to yoruba_health.xlsx")
