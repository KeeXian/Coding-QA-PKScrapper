from http.client import responses
import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize

# Return language
# For this I will only  be referencing from geeksforgeeks
def language_scrapper(po_language):
    url = f'https://www.geeksforgeeks.org/{po_language}/'
    responses = requests.get(url)
    if responses.status_code != 200:
        print("GeekforGeeks Url not found. Skipping...")
        return {
            'language': po_language,
            'desc': '',
            'examples': []
        }

    html = responses.content
    soup = BeautifulSoup(html, 'html.parser')

    # Extract descriptions
    desc = []
    div = soup.find('div', {'class': 'entry-content'})
    # Scrape the first paragraph
    for p in div.find_all('p'):
        if len(p) > 0:
            # Obtain the first few sentences of the first paragraph
            for sentence in sent_tokenize(p.text)[:4]:
                sentence = sentence.strip()
                desc.append(sentence.replace('\xa0', ' '))
            break

    # Extract examples
    example_list = []
    examples = soup.find_all('div', {'class': 'tabcontent'})
    for example in examples:
        example_list.append(example.text)

    language = {
        'name': po_language,
        'desc': " ".join(desc),
        'examples': example_list
    }
    return language

# Testing function
if __name__ == '__main__':
    language = language_scrapper('html')
    print(language)