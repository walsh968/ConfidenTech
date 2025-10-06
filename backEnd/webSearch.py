from googleapiclient.discovery import build

API_KEY = 'AIzaSyCMizf1CsepV8Psf6pnU3hy0FZXQTAXZFA'
CSE_ID = '86970aef48dab4539'


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

    # Return list of tuples
    return listOfSites