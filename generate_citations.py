import os
import json
import logging

def entry_filter(item):
    """
    Run checks against entries in the JSON articles list.
    If the entry fails a check, do not include it in the final plain text results.
    """
    if 'patent' in item['pub_source'].lower():
        return False
    #if 'arxiv' in item['pub_source'].lower():
    #    return False
    if not item['pub_source']:
        return False
    if not item['pub_date']:
        return False
    return True

def build_citation(item):
    """
    Construct a plaintext citation for the article entry.
    Returns as a string
    """
    def process_author(author_str):
        """
        Process an article's author name into a [first-initials] [last-name] format.
        """
        str1 = ''
        pieces = author_str.split(' ')
        for i in range(len(pieces)-1):
            str1 += pieces[i][0]
        str2 = pieces[-1]
        if str1:
            return f'{str1} {str2}'
        else:
            return str2

    def process_date(date_str):
        """
        Process an article date string into the publication year.
        """
        pieces = date_str.split('/')
        return pieces[0]
            
    # list of authors string
    authors_str = ', '.join([process_author(author) for author in item['authors']])
    # pub source and year string
    pub_str = f"{item['pub_source']}, {process_date(item['pub_date'])}"

    # construct full citation
    citation = f"\"{item['title']}\"\n{authors_str} - {pub_str}"
    return citation


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--indir', 
            default = './articles',
            help="Path to directory that contains JSON lists of articles")
    parser.add_argument('--outdir',
            default = './citations',
            help="Path to directory to store the generated article citations within. The directory will be create if necessary.")
    args = parser.parse_args()

    rt_dir = args.indir
    out_dir = args.outdir

    try:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    except:
        logging.warn("Failed to create output directory!")
    
    fnames = os.listdir(rt_dir)
    fnames = [fname for fname in fnames if '.json' in fname]
    for fname in fnames:
        print(f'Generating citations for {fname}...')
        pth = os.path.join(rt_dir, fname)
        with open(pth, 'r') as fi:
            items = json.load(fi)
        citations = [build_citation(item) for item in items if entry_filter(item)]
        new_pth = os.path.join(out_dir, fname.replace('.json', '.txt'))
        with open(new_pth, 'w') as fi:
            fi.write('\n\n'.join(citations))

