from http.client import responses
import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize
from app.api.url import generate_url

# # Scrape topics
# def topic_scrapper(topic, po_language):
#     """
#     This function scrapes the w3school webpage for html topics
#     """
#     po_language = po_language.lower()
#     topic = topic.lower()

#     # Check if the language is supported
#     url = f'https://www.w3schools.com/{po_language}/default.asp'
#     responses = requests.get(url)
#     if responses.status_code != 200:
#         print("Topic not found. Skipping...")
#         return topic
#     soup = BeautifulSoup(responses.content, 'html.parser')

#     # Find appropriate link to topic
#     menu = soup.find_all('div', {'id': 'leftmenuinnerinner'})[0]
#     for li in menu.find_all('a'):
#         prev_sibling = li.find_previous_sibling('h2')
#         if prev_sibling and prev_sibling.text == 'HTML Tutorial' and li.text.lower() == ('html ' + topic).lower():
#             url = li.get('href')
#             break
    
#     # Extract topic description
#     desc = []
#     responses = requests.get(f'https://www.w3schools.com/{po_language}/{url}')
#     if responses.status_code != 200:
#         print("Topic not found. Skipping...")
#         return topic
#     soup = BeautifulSoup(responses.content, 'html.parser')
#     content = soup.find('div', {'id': 'main'})

#     for p in content:
#         if p.name == 'p':
#             for sentence in sent_tokenize(p.text):
#                 desc.append(sentence)
#         if p.name == 'li' and p.parent.name == 'ul':
#             for sentence in sent_tokenize(p.text):
#                 desc.append(sentence)
    

#     # Extract topic examples
#     examples = []
#     exampleHTML = soup.find_all('div', {'class': 'w3-code'})
#     for example in exampleHTML:
#         examples.append(example.text)
    
#     return {
#         'title': topic,
#         'desc': desc,
#         'examples': examples
#     }

# scrape for topics
def topic_scrapper(po_language, topic_display_name):
    """
    This function scrapes the w3school webpage for html topics
    """
    po_language = po_language.lower()
    topic_display_name = topic_display_name.lower()

    # Using scrapper to scrape necessary data from the webpage
    url = generate_url('w3schools', po_language, topic_display_name)
    responses = requests.get(url)
    if responses.status_code != 200:
        print("Topic not found. Skipping...")
        return {
            'title': topic,
            'desc': [],
            'examples': []
        }  
    soup = BeautifulSoup(responses.content, 'html.parser')
    content = soup.find('div', {'id': 'main'})

    # Extract the descriptions of the topic
    desc = []
    for p in content:
        if p.name == 'p':
            for sentence in sent_tokenize(p.text):
                desc.append(sentence)
        if p.name == 'li' and p.parent.name == 'ul':
            for sentence in sent_tokenize(p.text):
                desc.append(sentence)
    

    # Extract topic examples
    examples = []
    exampleHTML = soup.find_all('div', {'class': 'w3-code'})
    for example in exampleHTML:
        examples.append(example.text)
    
    return {
        'title': topic_display_name,
        'desc': desc,
        'examples': examples
    }  