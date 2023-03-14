import requests

def fetch_ga_papers(query, max_results=10):
    base_url = 'http://export.arxiv.org/api/query?'
    search_query = f'cat:astro-ph.GA+AND+{query}'
    params = {
        'search_query': search_query,
        'start': 0,
        'max_results': max_results
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f'Error fetching papers: {response.status_code}')

query = 'Galactic+archaeology'
papers_xml = fetch_ga_papers(query)

# Proceed with parsing, downloading, and processing the papers as described above
