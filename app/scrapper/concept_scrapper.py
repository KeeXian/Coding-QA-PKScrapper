import re
import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize
import logging

from app.api.url import generate_url

# Main function to scrape contents
def concept_scrapper(tag=''):
    concept = {
        'tag': tag,
        'desc': [],
        'examples': set(()),
        'syntax': set(()),
    }

    # Special case for h1 to h6 tags
    if tag.lower() in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        concept = techonnet_scrapper(tag, concept)
        concept = quackit_scrapper(tag, concept)
    else:
        # Scrape through all the mentioned sources
        for scrapper in scrappers:
            concept = scrapper(tag, concept)
        
    if len(concept['desc']):
        return {
            'tag': tag,
            'desc': concept['desc'],
            'examples': list(concept['examples']),
            'syntax': list(concept['syntax']),
        }
    else:
        return {
            'tag': tag,
            'desc': [],
            'examples': [],
            'syntax': [],
        }


def w3school_scrapper(tag, concept):
    """
    This function scrapes the w3school webpage and returns the data in a dictionary
    """
    tag = re.sub('\d', 'n', tag)

    # Finding an existing source to scrape the data
    url = f'https://www.w3schools.com/tags/tag_{tag}.asp'
    try:
        if requests.get(url).status_code != 200:
            url = generate_url('w3schools', 'html', tag)
            if requests.get(url).status_code != 200 or 'tags' not in url:
                print("W3School Url not found. Skipping...")
                return concept

    except Exception as e:
        print(e)
        return concept
    
    responses = requests.get(url)
    soup = BeautifulSoup(responses.content, 'html.parser')
    # Extract descriptions
    desc = soup.find_all('div', {'id': 'main'})[0]
    if desc:
        found_description = False
        for p in desc:
            prev_sibling = p.find_previous_sibling('h2')
            if prev_sibling and prev_sibling.text == 'Definition and Usage':
                found_description = True
            else:
                found_description = False

            if found_description:
                for sentence in sent_tokenize(p.text):
                    
                    # Remove sentences that resembles: The <hr> tag also supports the Global Attributes in HTML.
                    if re.search('The <\w+> tag also supports the (Global|Event) Attributes in HTML', sentence):
                        continue
                    concept['desc'].append(sentence.replace('\n',''))
        
        # Extract examples
        examples = soup.find_all('div', {'class': 'w3-example'})
        if examples:
            for example in examples:
                e = example.find('div', {'class': 'w3-code'})
                if e:
                    concept['examples'].add(e.text)

        print('Successfully scraped ' + tag + ' from W3Schools')
    else:
        print('W3Schools main content not found for ' + tag)

    return concept

# Scrape data from dev mozilla website
def dev_mozilla_scrapper(tag, concept):
    
    # Finding an existing source to scrape the data
    url = f'https://developer.mozilla.org/en-US/docs/Web/HTML/Element/{tag}'
    try:
        responses = requests.get(url)
        if responses.status_code != 200:
            # If its a header tag, replace it with h1 to h6
            if tag == 'a':
                url = generate_url('mdnwebdocs', 'html', 'anchor')
            else:
                url = generate_url('mdnwebdocs', 'html', tag)
            responses = requests.get(url)
            if responses.status_code != 200 or 'HTML/Element' not in url:
                print("Dev Mozilla Url not found. Skipping...")
                return concept
    except Exception as e:
        print(e)
        return concept

    html = responses.content
    soup = BeautifulSoup(html, 'html.parser')    
    # Extract descriptions
    content = soup.select_one('.main-page-content')
    if content:
        div = content.find('div')
        for p in div:
            if p.name == 'p':
                for sentence in sent_tokenize(p.text):
                    concept['desc'].append(sentence)
        
        # Extract examples
        editors = div.find_all('iframe')
        for editor in editors:
            editor_url = editor.get('src')
            editor_response = requests.get(editor_url)
            if editor_response.status_code != 200:
                continue
            code_soup = BeautifulSoup(editor_response.content, 'html.parser')
            code_div = code_soup.select('#html-editor')[0]
            concept['examples'].add(code_div.text)

        # Extract some more examples from the preloaded examples at the bottom of the page
        preload = content.find_all('pre')
        for pre in preload:
            if pre.text:
                concept['examples'].add(pre.text)

        print('Successfully scraped ' + tag + ' from Dev Mozilla')
    
    else:
        print('Dev Mozilla main content not found for ' + tag)

    return concept


def geek_scrapper(tag, concept):

    # Finding an existing source to scrape the data
    url = f'https://www.geeksforgeeks.org/html-{tag}-tag/'
    if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        url = f'https://www.geeksforgeeks.org/html-heading/'

    try:
        if requests.get(url).status_code != 200:
            url = generate_url('geeksforgeeks', 'html', tag)
            if 'html' not in url or requests.get(url).status_code != 200:
                print("Geek Url not found. Skipping...")
                return concept
    except Exception as e:
        print(e)
        return concept

    responses = requests.get(url)
    html = responses.content
    soup = BeautifulSoup(html, 'html.parser')   
    # Extract descriptions
    content = soup.find('article', {'class': 'content'})
    if content:
        descs = content.find('div', {'class': 'text'})
        # Extract description
        for p in descs.find_all('p'):
            # Check if next sibling text is syntax
            next_sibling = p.find_next_sibling('strong') 
            if next_sibling and next_sibling.text == 'Syntax':
                for sentence in sent_tokenize(p.text)[:4]:
                    concept['desc'].append(sentence.replace('\xa0', ' '))
        
        # Extract syntaxes
        syntax = descs.find('pre')
        if syntax:
            concept['syntax'].add(syntax.text)

    else:
        print("No content found for " + tag)
    
    print('Successfully scraped ' + tag + ' from GeeksforGeeks')
    return concept

# Scraping from tutorialspoint website
def tutorialspoint_scrapper(tag, concept):
    # Finding the correct url
    responses = None
    url = f'https://www.tutorialspoint.com/html/html_{tag}_tag.htm'
    try:
        if requests.get(url).status_code != 200:
            url = generate_url('tutorialspoint', 'html', tag)
        
        if 'html' not in url:
            raise Exception('Invalid URL')

        responses = requests.get(url)    
    except Exception as e:
        print("TutorialsPoint URL not found. Skipping...")
        return concept
    
    html = responses.content
    soup = BeautifulSoup(html, 'html.parser')

    # Extract descriptions
    main_div = soup.find('div', {'id': 'mainContent'})
    if main_div:
        for p in main_div.find_all('p'):
            prev_sibling = p.find_previous_sibling('h2')
            if prev_sibling and prev_sibling.text == 'Description':
                for sentence in sent_tokenize(p.text):
                    concept['desc'].append(sentence)
        
        # Extract examples
        codes = main_div.find('pre', {'class': 'prettyprint'})
        concept['examples'].add(codes.text)
        print('Successfully scraped ' + tag + ' from TutorialsPoint')

    else:
        print('TutorialsPoint main div not found. Skipping...')

    return concept

# Scrape from javaTpoint website
def java_tpoint_scrapper(tag, concept):
    url = f'https://www.javatpoint.com/html-{tag}-tag'
    try:
        if requests.get(url).status_code != 200:
            url = f'https://www.javatpoint.com/html5-{tag}-tag'
            if requests.get(url).status_code != 200:
                url = f'https://www.javatpoint.com/{tag}-html'
                if requests.get(url).status_code != 200:
                    url = generate_url('javatpoint', 'html', tag)

        if 'html' not in url:
            raise Exception('Invalid URL')
    except:
        print('JavaTpoint URL not found. Skipping...')
        return concept


    responses = requests.get(url)
    html = responses.content
    soup = BeautifulSoup(html, 'html.parser')

    # Extract descriptions
    main_div = soup.find('div', {'id': 'city'})
    if main_div:
        # Find the tile tag and the horizontal line in main div
        title = main_div.find('h1')
        hr = main_div.find('hr')

        for p in main_div.find_all('p'):
            # Check if the p tag is wrapped in between a h1 and hr
            prev_siblings = p.find_previous_siblings()
            next_siblings = p.find_next_siblings()
            if title in prev_siblings and hr in next_siblings:
                for sentence in sent_tokenize(p.text):
                    concept['desc'].append(sentence)

        # Extract examples
        codes = main_div.find('div', {'class': 'codeblock'})
        if codes:
            concept['examples'].add(codes.text)
    else:
        logging.error('No main div found')

    print('Successfully scraped ' + tag + ' from JavaTpoint')
    return concept

# Extract data from tutorial_republic
def tutorial_republic_scrapper(tag, concept):
    url = f'https://www.tutorialrepublic.com/html-reference/html-{tag}-tag.php'
    try:
        if requests.get(url).status_code != 200:
            url = generate_url('tutorialrepublic', 'html', tag)
            if 'html' not in url or requests.get(url).status_code != 200:
                print('Tutorial Republic URL not found. Skipping...')
                return concept
    except:
        print('Tutorial Republic URL not found. Skipping...')
        return concept
    
    responses = requests.get(url)
    html = responses.content
    soup = BeautifulSoup(html, 'html.parser')

    main_div = soup.find('div', {'class': 'content'})
    if main_div:
        # Extract descriptions
        for p in main_div.find_all('p'):
            prev_sibling = p.find_previous_sibling('h2')
            next_sibling = p.find_next_sibling('div', {'class': 'shadow'})
            if prev_sibling and prev_sibling.text == 'Description' and next_sibling:
                concept['desc'].append(p.text)
        
        # Extract examples
        examples = main_div.find_all('div', {'class': 'example'})
        for example in examples:
            code = example.find('code', {'class': 'language-markup'})
            concept['examples'].add(code.text)

    print('Successfully scraped ' + tag + ' from Tutorial Republic')
    return concept

# Extract syntax from website tutorialrepublic
def tutorial_republic_syntax_scrapper(tag, concept):
    # Testing the url
    url = f'https://www.tutorialrepublic.com/html-reference/html-{tag}-tag.php'
    try:
        if requests.get(url).status_code != 200:
            # Try to generate url
            url = generate_url('tutorialrepublic', 'html', tag)
            if 'html' not in url or requests.get(url).status_code != 200:
                print('Tutorial Republic URL not found. Skipping...')
                return concept
    except:
        print('Tutorial Republic URL not found. Skipping...')
        return concept
    
    # Extract html content
    responses = requests.get(url)
    html = responses.content
    soup = BeautifulSoup(html, 'html.parser')

    # Main content of the website
    main_div = soup.find('div', {'class': 'content'})
    if main_div:
        # Extract syntax
        syntax = main_div.find('div', {'class': 'syntax'})
        if syntax:
            concept['syntax'].add(syntax.text)

        # Extract example
        examples = main_div.find_all('div', {'class': 'example'})
        for example in examples:
            prev_sibling = example.find_previous_sibling('h2')
            if prev_sibling and prev_sibling.text == 'Syntax':
                code = example.find('code', {'class': 'language-markup'})
                concept['examples'].add(code.text)
                break
        
    print('Successfully scraped syntax ' + tag + ' from Tutorial Republic')

    return concept

# Scrape from TechOnNet Website
def techonnet_scrapper(tag, concept):
    # Find the suitable url
    url = f'https://www.techonthenet.com/html/elements/{tag}_tag.php'
    try:
        if requests.get(url).status_code != 200:
            url = generate_url('techonnet', 'html', tag)
            if 'html/elements' not in url or requests.get(url).status_code != 200:
                print('TechOnNet URL not found. Skipping...')
                return concept
    except:
        print('TechOnNet URL not found. Skipping...')
        return concept
    
    # Extract html content
    responses = requests.get(url)
    html = responses.content
    soup = BeautifulSoup(html, 'html.parser')

    # Main content of the website
    main_div = soup.find('div', {'class': 'article'})
    if main_div:
        # Loop through the sections
        for section in main_div.find_all('div', {'class': 'section'}):
            # Find the description section
            section_title = section.find('h2')
            if section_title and section_title.text == 'Description':
                # Extract description
                for p in section.find_all('p'):
                    concept['desc'].append(p.text)
            
            # Find the syntax section
            elif section_title and section_title.text == 'Syntax':
                concept['syntax'].add(section.find('code').text)

        print('Successfully scraped ' + tag + ' from TechOnNet')
    else:
        print('Main content not found...')

    return concept

# Scrape from Quackit website
def quackit_scrapper(tag, concept):
    # Find the suitable url
    url = f'https://www.quackit.com/html/tags/html_{tag}_tag.cfm'
    try:
        if requests.get(url).status_code != 200:
            url = generate_url('quackit', 'html', tag)
            if 'html/tags' not in url or requests.get(url).status_code != 200:
                print('Quackit URL not found. Skipping...')
                return concept
    except:
        print('Quackit URL not found. Skipping...')
        return concept
    
    # Extract html content
    responses = requests.get(url)
    html = responses.content
    soup = BeautifulSoup(html, 'html.parser')

    # Main content of the website
    main_div = soup.find('article', {'class': 'content'})
    if main_div:
        # Description
        concept['desc'].append(main_div.find('p', {'class': 'lead'}).text)

        # Instructions
        for p in main_div.find_all('p'):
            prev = p.find_previous_sibling('h2')
            if prev and prev.text == 'Syntax':
                concept['desc'].append(p.text)
                break
        
        # Syntax
        syntax = main_div.find('div', {'class': 'code-only'})
        if syntax:
            concept['syntax'].add(syntax.text)

        # Example
        for form in main_div.find_all('form'):
            prev = form.find_previous_sibling('h2')
            if prev and prev.text == 'Examples':
                code = form.find('div', {'class': 'code-pane'})
                if code:
                    concept['examples'].add(code.text)
        
        print('Successfully scraped ' + tag + ' from Quackit')
    
    else:
        print('Main content not found...')
    
    return concept

scrappers = [
    w3school_scrapper,
    geek_scrapper,
    tutorialspoint_scrapper,
    java_tpoint_scrapper,
    tutorial_republic_scrapper,
    tutorial_republic_syntax_scrapper,
    techonnet_scrapper,
    quackit_scrapper
]