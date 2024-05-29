from bs4 import BeautifulSoup
import requests
import time
import re
import logging
from pprint import pprint

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Chrome(options=options)
    driver.quit()
    USE_SELENIUM = True
except:
    logging.warning("Selenium ChromeDriver is not available.")
    USE_SELENIUM = False


def get_profile_page_selenium(profile_id):
    """Use Selenium to visit a google profile page, and interact with 
        the "Show More" button (when necessary) to capture a complete HTML page.
        Requires that the host has chromium installed for the Chrome webdriver to work.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Chrome(options=options)
    
    params = {'user': profile_id, 
              'hl': 'en', 
              'sortby': 'pubdate'}
    params_str = '&'.join(f'{key}={value}' for key,value in params.items())
    base_url = f"https://scholar.google.com/citations?{params_str}"
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


def get_profile_page(profile_id):
    """Use the standard requests library to capture a google profile page.
        Lacks webpage interaction, so only the most recent 20 articles can be captured.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    base_url = f"https://scholar.google.com/citations"
    params = {'user': profile_id, 'hl': 'en', 'sortby': 'pubdate'}

    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.text


def get_scholar_profile_papers(profile_id, use_selenium=USE_SELENIUM):
    """Use Selenium to scrape all articles associated with a google scholar profile.
    """
    if use_selenium:
        page_source = get_profile_page_selenium(profile_id)
        
    if not use_selenium:
        page_source = get_profile_page(profile_id)
        
    soup = BeautifulSoup(page_source, "html.parser")
    papers = []

    for row in soup.find_all("tr", class_="gsc_a_tr"):
        title_tag = row.find("a", class_="gsc_a_at")
        title = title_tag.text
        article_id = parse_article_id(title_tag['href'])
        
        author_tag = row.find("div", class_="gs_gray")
        author_list = author_tag.text if author_tag else ""
        
        venue_year_tag = row.find_all("div", class_="gs_gray")[-1]
        venue_year_text = venue_year_tag.text if venue_year_tag else ""
        venue, year = parse_venue_and_year(venue_year_text)

        papers.append({
            "title": title,
            "id": article_id,
            "authors": author_list,
            "venue": venue,
            "year": year
        })

    return papers


def parse_venue_and_year(venue_year_text):
    """Extract publication venue and year
    """
    match = re.search(r"(.+), (\d{4})", venue_year_text)
    if match:
        venue = match.group(1).strip()
        year = match.group(2).strip()
    else:
        venue = venue_year_text.strip()
        year = ""
    return venue, year


def parse_article_id(article_url):
    """Extract the google scholar article ID from an article URL
    """
    match = re.search(r'citation_for_view=([^&]+)', article_url)
    if match:
        return match.group(1)
    else:
        return ""


if __name__ == "__main__":
    # Example usage
    profile_id = "icDo19sAAAAJ"
    papers = get_scholar_profile_papers(profile_id)

    for paper in papers:
        pprint(paper)