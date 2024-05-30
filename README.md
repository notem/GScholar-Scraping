# Google Scholar Faculty Article webscraper

This repository contains a collection of scripts to aid in the gathering of information from Google Scholar. Usage is simple: (1) use the `get_profiles.py` script to find the Google profile IDs associated with faculty names at your institution, and (2) use the `scrape_profiles.py` script to gather information on all the research articles associated with the profiles. Results are saved as JSON files.

* `python get_profiles.py --faculty_list faculty.txt --outfile profiles.json`
* `python scrape_profiles.py --infile profiles.json --outdir profiles/`

Additionally, extra scripts are provided to perform (1) scraping of arbitrary queries to Google Scholar kwith `query_scholar.py` and (2) scrape information from a Google Scholar article page directly using the article's ID with `scrape_article.py`.

NOTE: remaining challenge is avoiding bot detection by Google services...