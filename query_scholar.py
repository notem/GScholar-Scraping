import requests
from bs4 import BeautifulSoup
import datetime

def fetch_recent_faculty_publications(faculty_name, year=2023):

    # Encode the faculty name to insert into the URL
    query = '+'.join(faculty_name.split())
    url = f'https://scholar.google.com/scholar'
    params = {'as_ylo': year, 'hl': 'en', 'q': query}

    # Send a request to Google Scholar
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print('Failed to retrieve data')
        return []

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    publications = []

    # Find publication entries and check the publication year
    for entry in soup.find_all('div', class_='gs_ri'):
        title = entry.h3.a.text if entry.h3 and entry.h3.a else 'No title available'
        link = entry.h3.a['href'] if entry.h3 and entry.h3.a else 'No link available'
        year = entry.find('div', class_='gs_a').text

        publications.append((title, link, year))

    return publications

# Example usage
faculty_name = "Matthew Wright Rochester Institute of Technology RIT"
publications = fetch_recent_faculty_publications(faculty_name)
for title, link, year in publications:
    print(title, link, year)
