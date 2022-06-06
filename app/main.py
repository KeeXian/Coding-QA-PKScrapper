from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import os
import time

# Import scrappers needed to scrape website
from app.scrapper.concept_scrapper import *
from app.scrapper.po_language_scrapper import *
from app.scrapper.html_style_scrapper import *
from app.scrapper.atr_scrapper import *

# Import models
from app.model.ml_model import *

# Initialize the flask application 
app = Flask(__name__)
api = Api(app)

# # Preload the models
# data_file = None
# model = None
# labels = None
# if os.path.exists('app/resources/model.sav') and os.path.exists('app/resources/glove.6B.300d.gs') and os.path.exists('app/resources/data_test.csv'):
#     start = time.time()
#     model, labels = build_model('app/resources/data_test.csv', 'app/resources/model.sav', 'app/resources/glove.6B.300d.gs')
#     end = time.time()
#     print('Model loaded in: ' + str(end - start))
# else:
#     print('Model not found')

class Scrapper(Resource):
    def get(self):

        # Load the model
        start = time.time()
        model, labels =  build_model('app/resources/data_test.csv', 'app/resources/model.sav', 'app/resources/glove.6B.300d.gs', 'app/resources/rules.json')
        end = time.time()
        print('Model loaded in: ' + str(end - start))

        # Check if model is loaded
        if model is not None:
            return {   
                'status': 200,
                'message': 'Model loaded successfully'
            }

        return {
            'status': 404,
            'message': 'Model not found'
        }

    def post(self):
        # Create parser
        parser = reqparse.RequestParser()
        parser.add_argument('po_language', type=str)
        parser.add_argument('topic', type=str)
        parser.add_argument('tags', action='append')
        parser.add_argument('html_style', action='append')
        args = parser.parse_args() 

        # Data and Tag
        po_language = args['po_language']
        topic = args['topic']
        tags = args['tags']
        html_style = args['html_style']
        print('PO_Language: ', po_language, 'Topic: ', topic, 'Tags: ', tags, 'HTML_Style: ', html_style)
        
        # OutputData
        language = ''
        topic_data = {}
        data = []

        try:
            # Load the models
            model, labels =  build_model('app/resources/data_test.csv', 'app/resources/model.sav', 'app/resources/glove.6B.300d.gs', 'app/resources/rules.json')

            # Scrape website
            if po_language:
                language = language_scrapper(po_language)

            if tags and len(tags) > 0:
                for tag in tags:
                    tag = tag.strip()

                    # Use scrapper to perform concept scrapping
                    concept = concept_scrapper(tag)
                    if len(concept['desc']) <= 0:
                        continue

                    # Predict type of description
                    predicted = predict_desc(concept['desc'], model, labels)

                    # Insert data
                    df = pd.DataFrame(columns=['desc', 'tag'])
                    for i, desc in enumerate(concept['desc']):
                        if desc not in df['desc'].values:
                            df = pd.concat([df, pd.DataFrame({'desc': [desc], 'tag': [predicted[i]]})])
                    
                    # Obtain the first 3 descriptions and instructions
                    descriptive = df[df['tag'] == 'DESC'].head(3)
                    instruction = df[df['tag'] == 'INS'].head(3)

                    # Insert data
                    descriptive = descriptive['desc'].values
                    instruction = instruction['desc'].values

                    # # Find major attributes in the examples
                    # attributes = []
                    # for example in concept['examples']:
                    #     example_attrs = extract_html_attributes(example)
                    #     if len(example_attrs) > 0:
                    #         for attr in example_attrs:
                    #             if attr not in attributes:
                    #                 attributes.extend([atr_scrapper(tag, attr)])
                    
                    data.append({
                        'name': tag,
                        'wh-desc': descriptive.tolist(),
                        'how-desc': instruction.tolist(),
                        'example': concept['examples'],
                        'syntax': concept['syntax'],
                        'instruction': concept['instruction'],
                    })
            
            if html_style and len(html_style) > 0:
                for style in html_style:
                    style = style.strip()

                    # Use the html style scrapper to perform scrapping
                    response = html_styling_scrapper(style)
                    data.append({
                        'name': style,
                        'desc': response['desc'],
                        'example': [response['examples']]
                    })

            # Response if there is no data scrapped
            if len(data) <= 0:
                return {
                    'status': 404,
                    'message': 'No data found',
                    'body': {
                        'po_language': language,
                        'topic': topic_data,
                        'concepts': data,
                    }
                }
            
            # Response if there is data scrapped
            return {
                'status': 200,
                'message': 'Successfully scrapped data',
                'body': {
                    'po_language': language,
                    'topic': topic_data,
                    'concepts': data,
                }
            }

        except Exception as e:
            print(e)
            return {
                'status': 500,
                'message': e,
            }

# Add scrapper to the api
api.add_resource(Scrapper, '/scrapper')