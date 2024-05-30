import requests
from bs4 import BeautifulSoup
import datetime


def fetch_recent_faculty_publications(query, year=None):
    """Run a query through Google Scholar and return basic information 
        on retrieved articles, with optional filtering by year.
    """
    # Encode the faculty name to insert into the URL
    query = '+'.join(query.split())
    url = f'https://scholar.google.com/scholar'
    params = {'hl': 'en', 'q': query}
    if year is not None:
        params['as_ylo'] = year

    # Send a request to Google Scholar
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    publications = []

    # Find publication entries and check the publication year
    for entry in soup.find_all('div', class_='gs_ri'):
        title = entry.h3.a.text if entry.h3 and entry.h3.a else 'No title available'
        link = entry.h3.a['href'] if entry.h3 and entry.h3.a else 'No link available'
        year = entry.find('div', class_='gs_a').text

        publications.append({'title': title, 
                             'link': link, 
                             'year': year})

    return publications


if __name__ == "__main__":
    # Example usage
    from argparse import ArgumentParser
    parser = ArgumentParser("Scrape Google Scholar article search results using a query.")
    parser.add_argument('--query', 
                        required=True,
                        help="")
    parser.add_argument('--year',
                        required=False,
                        default=None,
                        help="(Optional) Publication year by which to filter the query results.", 
                        type=int)
    args = parser.parse_args()
    
    publications = fetch_recent_faculty_publications(args.query, year=args.year)
    for info in publications:
        print(info)
