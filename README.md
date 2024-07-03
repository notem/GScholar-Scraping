# Google Scholar Faculty Article webscraper

This repository contains a collection of scripts to aid in the gathering of information from Google Scholar. Usage is simple: (1) use the `get_profiles.py` script to find the Google profile IDs associated with faculty names at your institution, and (2) use the `scrape_profiles.py` script to gather information on all the research articles associated with the profiles. Results are saved as JSON files.

* `python get_profiles.py --faculty_list faculty.txt --outfile profiles.json`
* `python scrape_profiles.py --infile profiles.json --outdir profiles/`

Additionally, extra scripts are provided to perform (1) scraping of arbitrary queries to Google Scholar kwith `query_scholar.py` and (2) scrape information from a Google Scholar article page directly using the article's ID with `scrape_article.py`.

The `scrape_profiles.py` script will fill a directory containing JSON files. Each JSON file will contain the scraped article information for all articles on a profile. The name of the JSON file is the faculty profile that was scraped. This JSON formatted data can be transformed into plain text using the `generate_citations.py` script. Example usage is below.

* `python generate_citations.py --indir ./articles/ --outdir ./citations/`


NOTE: Google will frequently identify the browsing behavior produced by the scripts as "suspicious", which will cause the scraping to fail. To address is this issue, the `scrape_profiles.py` script is configured with an increasing wait between failed requests. Google's behavior seems to reset within a 24 hour period, at which point scraping will be resumed. Running multiple instances of the script to scrape profiles concurrently on different IPs is recommended...
