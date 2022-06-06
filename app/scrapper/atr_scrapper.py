import re
import requests
from bs4 import BeautifulSoup

# Extract attributes of html tags in a text
def extract_html_attributes(text):
    """
    Extract attributes of html tags in a text
    :param text: text
    :return: list of attributes
    """
    # Find all html tags
    html_tags = re.findall('<[^>]+>', text)
    # Extract the attributes
    attributes = []
    for tag in html_tags:
        # Find the attribute
        atr = re.findall(' (\w*)=', tag)
        # Add the attribute to the list
        attributes.extend(atr)
    return attributes


# Scrape for the important attributes of a html tag
def atr_scrapper(html_tag, tag_atr):
    """
    Scrape for the important attributes of a html tag
    :param html_tag: html tag
    :return: dictionary of important attributes
    """
    w3schools_url = f'https://www.w3schools.com/tags/att_{html_tag}_{tag_atr}.asp'
    print(w3schools_url)
    responses = requests.get(w3schools_url)
    if responses.status_code != 200:
        print(f'Attribute {tag_atr} not found. Skipping...')
        return None
    
    soup = BeautifulSoup(responses.content, 'html.parser')
    # Find the definition and usage section
    res = next((title for title in soup.find_all('h2') if title.text == 'Definition and Usage'), None)
    if res:
        # Find the paragraph containing the description
        desc = res.find_next_sibling('p')
        # Extract the description
        description = desc.text
        # Return the description and examples
        return {
            'description': description,
        }
    else:
        print('No definition for ' + tag_atr)
        return None


# Testing
if __name__ == '__main__':
    html = '<p class="Text" hoho="Testing">This is a paragraph.</p> <kk test="asdwda">'
    print(extract_html_attributes(html))

    print(atr_scrapper('a', 'href'))