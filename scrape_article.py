import requests
from bs4 import BeautifulSoup
from pprint import pprint


def fetch_publication_info(article_ID):
    """Fetch article information from a Google Scholar article view page.
    """
    # Encode the article ID into a weburl
    url = f'https://scholar.google.com/citations'
    params = {'hl': 'en', 
              'view_op': 'view_citation', 
              'citation_for_view': article_ID}

    # Send a request to Google Scholar
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
        
    # Initialize a dictionary to store the article information
    article_info = {}

    # Extract the title
    title_tag = soup.find('div', id='gsc_oci_title')
    if title_tag:
        article_info['title'] = title_tag.text
    
    # Extract table fields
    fields = soup.find_all('div', class_='gs_scl')
    for field in fields:
        field_name = field.find('div', class_='gsc_oci_field').text.strip()
        field_value = field.find('div', class_='gsc_oci_value').text.strip()
        
        if field_name == "Authors":
            proc = lambda text: text.split(',')
            article_info['authors'] = proc(field_value)
            
        elif field_name in ("Conference", "Journal", "Book"):
            proc = lambda text: text
            article_info['pub_source'] = proc(field_value)
            
        elif field_name == "Publication date":
            proc = lambda text: text
            article_info['pub_date'] = proc(field_value)
            
        elif field_name == "Description":
            proc = lambda text: text
            article_info['description'] = proc(field_value)
            
    # Extract the total citations separately
    citations_div = soup.find('div', style='margin-bottom:1em')
    if citations_div:
        citation_link = citations_div.find('a')
        if citation_link:
            proc = lambda text: int(text.replace('Cited by ',''))
            article_info['citations'] = proc(citation_link.text.strip())
    
    return article_info


if __name__ == "__main__":
    # Example usage
    article_id = "icDo19sAAAAJ:u5HHmVD_uO8C"
    info = fetch_publication_info(article_id)
    pprint(info)