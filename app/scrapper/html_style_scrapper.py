from http.client import responses
import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize

from app.api.url import generate_url

test_link = "https://www.w3schools.com/html/tryit.asp?filename=tryhtml_styles_background-color"
# Function to scrape html styling
def html_styling_scrapper(property):
    """
    This function scrapes the sources for css styling via html style tag
    """
    url = generate_url('tutorialspoint', 'html', 'change ' + property)
    responses = requests.get(url)
    if responses.status_code != 200:
        print("Tutorialspoint Url not found. Skipping...")
        return None
    soup = BeautifulSoup(responses.content, 'html.parser')

    # Extract description from the page
    content = soup.find('div', {'class': 'tutorial-content'})
    sent = content.find('p').text
    desc = sent_tokenize(sent)

    # Extract examples from the page
    examples = content.find('pre').text

    return {
        'property': property,
        'desc': desc,
        'examples': examples
    }