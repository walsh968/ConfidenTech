from googleapiclient.discovery import build

API_KEY = 'AIzaSyCMizf1CsepV8Psf6pnU3hy0FZXQTAXZFA'
CSE_ID = '86970aef48dab4539'

# adding in a comment to push so vercel deploys
'''
Method which utilizes the Google Custom Search API to take a query and retrieve the top
    resulting website titles and links to them
@param query is the query to search the web with
@returns a list of tuples where the first element is the website title, the second is
    the website link, and the third is a site description
'''
def get_sites(query):
    # Instantiate list of websites to be returned from query
    listOfSites = []

    # Build custom serach service and retrieve top 10 website titles and links
    service = build("customsearch", "v1", developerKey=API_KEY)
    titlesAndLinks = service.cse().list(q=query, cx=CSE_ID).execute()

    # Append top 5 websites to listOfSites and return them
    for item in titlesAndLinks.get('items', []):
        listOfSites.append((item['title'], item['link'], item['snippet']))
    
    print(f'list of sites: {listOfSites}')

    # Return list of tuples
    return listOfSites

import arxiv
'''
Method for querying academic database arxiv to extract relevant research papers
@param query is the query to search the database with
@returns a list of tuples where the first element is the paper title, the second is
    a summary of the paper, and the third is a link to the pdf
'''
def get_research_papers(query):
    # Instantiate list of relevant paper infor to be returned
    threeTuples = []

    # Get top 5 results from the entered search query
    papers = arxiv.Search(query=query, max_results=5)

    # Loop through returned papers' info and append a tuple of title, summary, and link
    for paper in papers:
        threeTuples.append((paper.title, paper.summary, paper.pdf_url))
    
    # Return the list of three tuples
    return threeTuples


import requests
from bs4 import BeautifulSoup
from readability import Document

'''
Method that takes in a url and scrapes the text content of that webpage
@param url is the link for a website to be scraped
@returns a string with the main textual content of a webpage
'''
def get_text_content(url):
    # Get raw html content of webpage
    htmlContent = requests.get(url).text

    # Convert raw html content into Document object
    document = Document(htmlContent)
    
    # Extract main textual content (HTML format most likely)
    textContentHTML = document.summary()

    # Parse using bs4
    soup = BeautifulSoup(textContentHTML, "html.parser")

    # Return parsed textual content
    return soup.get_text(separator='\n').strip()
