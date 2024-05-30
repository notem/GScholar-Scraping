import requests
from bs4 import BeautifulSoup
import re


def get_scholar_profile_id(query):
    """Search Google Scholar profiles using the provided query 
        and return the ID of the most relevant profile.
    """
    search_url = "https://scholar.google.com/citations"
    params = {"mauthors": query, "hl": "en", "view_op": "search_authors"}

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    response = requests.get(search_url, params=params, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    profile_link = soup.find("a", href=re.compile(r"user=.*"))
    
    if profile_link:
        profile_url = profile_link['href']
        profile_id_match = re.search(r"user=([\w-]+)", profile_url)
        if profile_id_match:
            return profile_id_match.group(1)
    
    return ''


if __name__ == "__main__":
    from argparse import ArgumentParser
    
    parser = ArgumentParser('Use Google Scholar profile search to find profile pages for research faculty.')
    parser.add_argument('--faculty_list', 
                        required=True,
                        help="A new-line separated plaintext file containing faculty names to query.")
    parser.add_argument('--search_terms', 
                        required=False, 
                        default='rit.edu',
                        help="Additional search terms to restrict the profile search. "
                        "Using your institution's email domain is recommend.")
    parser.add_argument('--outfile', 
                        default='profiles.json',
                        help='The JSON file to which profile IDs should be saved.')
    args = parser.parse_args()
    
    with open(args.faculty_list, 'r') as fi:
        faculty_names = [line.strip() for line in fi]
    
    faculty_profiles = {name: get_scholar_profile_id(f'{name} {args.search_terms}') for name in faculty_names}

    for name, profile_id in faculty_profiles.items():
        if profile_id:
            print(f"Name: {name}, Profile: https://scholar.google.com/citations?hl=en&user={profile_id}")
        else:
            print(f"Name: {name}, Profile: N/A")
        
    import json
    with open(args.outfile,'w') as fi:
        json.dump(faculty_profiles, fi, indent=4)
