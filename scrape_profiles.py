from bs4 import BeautifulSoup
import requests
import time
import re
import logging

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


def build_article_uri(article_id):
    """Build url for direct access of Scholar information for an article ID
    """
    params = {'hl': 'en', 
              'view_op': 'view_citation', 
              'citation_for_view': article_id}
    params_str = '&'.join(f'{key}={value}' for key,value in params.items())
    return f"https://scholar.google.com/citations?{params_str}"


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
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "gsc_bpf_more"))
            )
            show_more_button.click()
            time.sleep(2)  # Wait for the page to load new content
        except Exception as e:
            break

    page_source = driver.page_source
    driver.quit()
    return page_source


def get_profile_page(profile_id):
    """Use the standard requests library to capture a google profile page.
        Lacks webpage interaction, so only the most recent 20 articles can be captured.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
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
            "url": build_article_uri(article_id),
            "authors": [author.strip() for author in author_list.split(',')],
            "pub_source": venue,
            "pub_date": year
        })
        
    # No papers and using selenium? Try using a basic requests call as a backup.
    if not papers and use_selenium:
        papers = get_scholar_profile_papers(profile_id, False)

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
    from argparse import ArgumentParser
    parser = ArgumentParser('Scrape Google Scholar profile and article pages for information on '
                            'articles published by research faculty. Selenium is optionally required '
                            'for full profile scraping.')
    parser.add_argument('--infile', 
                        default='./profiles.json',
                        help="A JSON file containing user profile IDs to use for scraping. "
                        "The `get_profiles.py` script may be used to produce this file.")
    parser.add_argument('--outdir', 
                        default='./articles',
                        help="The directory name in which profile article JSON files should be saved.")
    args = parser.parse_args()
    
    import os
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)
        
    import json
    with open('profiles.json', 'r') as fi:
        profiles = json.load(fi)
        
    # randomized sleep function to help avoid bot detection
    import random
    sleep = lambda x=0: time.sleep((2**x) * random.randint(10,20))

    # scrape article information 
    from scrape_article import fetch_publication_info
    profile_papers = {}
    for name,profile_id in profiles.items():
        if profile_id:
            print(f'Scraping basic info of articles from {name}\'s Google Scholar profile...')
            try:
                # Scrape articles off the profile page
                papers = get_scholar_profile_papers(profile_id)
                profile_papers[name] = papers
                
                print(f' - Found {len(papers)} articles')

                with open(f'{os.path.join(args.outdir, name)}.json', 'w') as fi:
                    json.dump(papers, fi, indent=4)

            except KeyboardInterrupt:
                import sys
                sys.exit()
            except:
                logging.warning(f"Encountered error when scraping {name}!")
            sleep()

    print(f'Updating article information with direct queries...')
    tot_paper_num = sum(len(papers) for name,papers in profile_papers.items())
    cur_paper_num = 0
    for name,papers in profile_papers.items():
        for paper in papers:
            # Print the current article url
            print(f"[{cur_paper_num}/{tot_paper_num}] {paper['url']}")
            better_info = {}
            
            # make scraping requests for article information
            # retry on failures with increasing sleep interval
            # give up after 14 attempts
            i = 0   # sleep delay is multiplied by 2**i
            while i < 14:
                try:
                    # Scrape better article information from the article's page
                    sleep(i)
                    better_info = fetch_publication_info(paper['id'])
                    break  # quit loop
                except KeyboardInterrupt:
                    import sys
                    sys.exit()
                except:
                    logging.warning(f"Encountered error when scraping {name}!")
                    i += 1
                    
            paper.update(better_info)
            cur_paper_num += 1

        with open(f'{os.path.join(args.outdir, name)}.json', 'w') as fi:
            json.dump(papers, fi, indent=4)
