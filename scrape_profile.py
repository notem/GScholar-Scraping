import requests
from bs4 import BeautifulSoup
import re

def get_scholar_profile_papers(profile_id):
    headers = {'User-Agent': 'Mozilla/5.0'}
    base_url = f"https://scholar.google.com/citations"
    params = {'user': profile_id, 'hl': 'en', 'sortby': 'pubdate'}

    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    papers = []

    for row in soup.find_all("tr", class_="gsc_a_tr"):
        title_tag = row.find("a", class_="gsc_a_at")
        title = title_tag.text
        url = f"https://scholar.google.com{title_tag['href']}"
        
        author_tag = row.find("div", class_="gs_gray")
        author_list = author_tag.text if author_tag else ""
        
        venue_year_tag = row.find_all("div", class_="gs_gray")[-1]
        venue_year_text = venue_year_tag.text if venue_year_tag else ""
        venue, year = parse_venue_and_year(venue_year_text)

        papers.append({
            "title": title,
            "url": url,
            "authors": author_list,
            "venue": venue,
            "year": year
        })

    return papers

def parse_venue_and_year(venue_year_text):
    match = re.search(r"(.+), (\d{4})", venue_year_text)
    if match:
        venue = match.group(1).strip()
        year = match.group(2).strip()
    else:
        venue = venue_year_text.strip()
        year = ""
    return venue, year

# Example usage
profile_id = "icDo19sAAAAJ"
papers = get_scholar_profile_papers(profile_id)

for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"URL: {paper['url']}")
    print(f"Authors: {paper['authors']}")
    print(f"Venue: {paper['venue']}")
    print(f"Year: {paper['year']}\n")
