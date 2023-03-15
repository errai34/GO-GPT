import os
import time
import requests
import feedparser
import urllib.parse

def fetch_papers(search_query, start=0, total_results=10, results_per_iteration=10, wait_time=3):
    base_url = 'http://export.arxiv.org/api/query?'
    search_query = urllib.parse.quote(search_query)

    papers = []

    print('Searching arXiv for %s' % search_query)

    for i in range(start, total_results, results_per_iteration):
        print("Results %i - %i" % (i, i + results_per_iteration))

        query = 'search_query=%s&start=%i&max_results=%i' % (search_query, i, results_per_iteration)

        response = requests.get(base_url + query)
        response.raise_for_status()

        feed = feedparser.parse(response.text)

        for entry in feed.entries:
            pdf_url = ''
            for link in entry.links:
                if link.type == 'application/pdf':
                    pdf_url = link.href
                    break

            paper = {
                "date": entry.published,
                "title": entry.title,
                "first_author": entry.authors[0].name,
                "summary": entry.summary,
                "pdf_url": pdf_url,
                "arxiv_id": entry.id.split('/abs/')[-1]
            }
            papers.append(paper)

        print('Bulk: %i' % 1)
        time.sleep(wait_time)

    return papers

def download_papers(papers, output_dir='./papers'):
    for paper in papers:
        pdf_url = paper['pdf_url']
        arxiv_id = paper['arxiv_id']
        output_path = os.path.join(output_dir, f"{arxiv_id}.pdf")

        print(f"Downloading {arxiv_id} to {output_path}")
        response = requests.get(pdf_url)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {arxiv_id}")

search_query = "ti:gaia sausage enceladus"
papers = fetch_papers(search_query)
download_papers(papers)

from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

def save_texts(pdf_texts, output_dir='./texts/'):
    for arxiv_id, text in pdf_texts.items():
        output_path = os.path.join(output_dir, f"{arxiv_id}.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Saved text for {arxiv_id} to {output_path}")

def pdf_to_text(pdf_path):
    output_string = StringIO()
    with open(pdf_path, 'rb') as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)

    return output_string.getvalue()

pdf_texts = {}
for paper in papers:
    arxiv_id = paper['arxiv_id']
    pdf_path = f"./papers/{arxiv_id}.pdf"
    text = pdf_to_text(pdf_path)
    pdf_texts[arxiv_id] = text
    print(f"Converted {arxiv_id} to text")

print(pdf_texts)

import re
import string

def clean_text(text):
    # Extract text between Abstract and Conclusion
    abstract_to_conclusion = re.search(r'ABSTRACT(.*?)CONCLUSION', text, flags=re.DOTALL | re.IGNORECASE)
    if abstract_to_conclusion:
        text = abstract_to_conclusion.group(1)

    # Remove URLs
    text = re.sub(r'http\S+', '', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove LaTeX expressions
    text = re.sub(r'\$[^$]+\$', '', text)

    # # Remove non-alphanumeric characters and extra whitespace
    # text = re.sub(r'\W+', ' ', text)

    # # Remove potential page numbers
    # text = re.sub(r'\b\d+\b', '', text)

    # Remove line breaks and page numbers
    text = re.sub(r'(\n+|\d+)', ' ', text)

    # Remove special characters except periods (.) and question marks (?)
    exclude = string.punctuation.replace('.', '').replace('?', '')
    text = ''.join(char for char in text if char not in exclude)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text.strip()


cleaned_texts = {}
for arxiv_id, text in pdf_texts.items():
    cleaned_text = clean_text(text)
    cleaned_texts[arxiv_id] = cleaned_text
    print(f"Cleaned text for {arxiv_id}")

# Save cleaned texts
save_texts(cleaned_texts, output_dir='./texts')

# # Load and preprocess cleaned texts
# preprocessed_texts = {}
# for paper in papers:
#     arxiv_id = paper['arxiv_id']
#     text = load_text(arxiv_id, input_dir='.texts')
#     preprocessed_text = preprocess_text(text)
#     preprocessed_texts[arxiv_id] = preprocessed_text
#     print(f"Preprocessed text for {arxiv_id}")

# print(preprocessed_texts)
