from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

def get_full_profile_page(profile_id):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Chrome(options=options)
    
    base_url = f"https://scholar.google.com/citations?user={profile_id}&hl=en&sortby=pubdate"
    driver.get(base_url)

    # Click the "Show More" button until it disappears
    while True:
        try:
            print("Clicking \"Show More\" button...")
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "gsc_bpf_more"))
            )
            show_more_button.click()
            time.sleep(2)  # Wait for the page to load new content
        except Exception as e:
            print(f"No more 'Show More' button found: {e}")
            break

    page_source = driver.page_source
    driver.quit()
    return page_source

def get_scholar_profile_papers(profile_id):
    page_source = get_full_profile_page(profile_id)
    soup = BeautifulSoup(page_source, "html.parser")
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
