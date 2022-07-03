import requests
from urllib.parse import quote


sources = {
    'w3schools': 'w3schools.com',
    'geeksforgeeks': 'geeksforgeeks.org',
    'mdnwebdocs': 'developer.mozilla.org',
    'tutorialspoint': 'tutorialspoint.com',
}


def generate_url(source, language, concept):
    """
    This function generates the url for the API call
    """

    try:
        # First api for google searching
        main = sources.get(source)
        query = language + ' ' + concept
        querystring = {"query": query, "gl": 'US', "max": "10", "site": main}
        url = "https://google-web-search.p.rapidapi.com/"
        headers = {
            "X-RapidAPI-Host": "google-web-search.p.rapidapi.com",
            "X-RapidAPI-Key": "30e5fcfedfmsh2c2d77585f32f6fp199c11jsn0cd2b5c3787d"
        }
        print('Running API1')
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = response.json()
        if data.get('results'):
            return data['results'][0]['url']

        # Use second api when first api quota is finished
        print('Running API2')
        query = language + ' ' + concept
        querystring = {"query": query, "gl": 'US', "max": "10", "site": main}
        url = "https://google-search1.p.rapidapi.com/google-search"
        querystring = {"hl":"en","q":quote(query),"gl":"us"}
        headers = {
            "X-RapidAPI-Host": "google-search1.p.rapidapi.com",
            "X-RapidAPI-Key": "30e5fcfedfmsh2c2d77585f32f6fp199c11jsn0cd2b5c3787d"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = response.json()
        if data.get('organic'):
            return data['organic'][0]['url']

        # Use third api when second api quota is finished
        print('Running API3')
        query = language + '+' + concept.replace(' ', '+')
        url = f"https://google-search3.p.rapidapi.com/api/v1/search/q={query}&gl=US&max=10&site={main}"
        headers = {
            "X-User-Agent": "desktop",
            "X-Proxy-Location": "EU",
            "X-RapidAPI-Host": "google-search3.p.rapidapi.com",
            "X-RapidAPI-Key": "30e5fcfedfmsh2c2d77585f32f6fp199c11jsn0cd2b5c3787d"
        }
        response = requests.request("GET", url, headers=headers)
        data = response.json()
        if data.get('results'):
            return data['results'][0]['link']

        print("All API quota finished. Skipping...")
        return 'All API quota finished'
    
    except Exception as e:
        print('Error:', e)
        return 'Cannot find the desired data. Please try again'
