import requests
from bs4 import BeautifulSoup
import re


def get_scholar_profile_id(query):
    """Search Google Scholar profiles using the provided query 
        and return the ID of the most relevant profile.
    """
    search_url = "https://scholar.google.com/citations"
    params = {"mauthors": query, "hl": "en", "view_op": "search_authors"}

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_url, params=params, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    profile_link = soup.find("a", href=re.compile(r"user=.*"))
    
    if profile_link:
        profile_url = profile_link['href']
        profile_id_match = re.search(r"user=([\w-]+)", profile_url)
        if profile_id_match:
            return profile_id_match.group(1)
    
    return None


if __name__ == "__main__":
    # Example usage
    faculty_names = ["Matthew Wright"]
    faculty_profiles = {name: get_scholar_profile_id(f'{name} rit.edu') for name in faculty_names}

    for name, profile_id in faculty_profiles.items():
        print(f"Name: {name}, Profile ID: {profile_id}")

