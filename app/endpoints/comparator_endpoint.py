
import numpy as np
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_restful import Resource, reqparse

# Import mongoDB
if __name__ != '__main__':
    from app.api.po_knowledge_db import load_concepts
    from app.model.preprocessor import text_preprocessing
else:
    # NoSQL database for storing programming concepts and its configurations
    import pymongo
    # Establish connection
    conn = "mongodb+srv://KeeXian:BoQNvdupdznEhqLF@programmingknowledgedat.m95zw.mongodb.net/ProgrammingKnowledgeDatabase?retryWrites=true&w=majority"
    client = pymongo.MongoClient(conn, connect=False)
    db = client.ProgrammingKnowledge
    print('Successfully established connection to database')

    # Load concept data from database
    def load_concepts(concept_name, language):
        # Retrieve language id
        language_id = db.PO_language.find_one({'name': language.upper()})['_id']

        # Retrieve concept data
        collection = db.Concept
        concept = collection.find_one({'name': concept_name.lower(), 'language': language_id})
        if concept is not None:
            return concept
        else:
            return None

# returns the cosine similarity value of the two given texts
def compute_cosine_similarity(text1, text2):
    
    # stores text in a list
    list_text = [text1, text2]
    
    # converts text into vectors with the TF-IDF 
    vectorizer = TfidfVectorizer(stop_words='english')
    vectorizer.fit_transform(list_text)
    tfidf_text1, tfidf_text2 = vectorizer.transform([list_text[0]]), vectorizer.transform([list_text[1]])
    
    # computes the cosine similarity
    cs_score = cosine_similarity(tfidf_text1, tfidf_text2)
    return np.round(cs_score[0][0],2)


# compute the average of the cosine similarity of the descriptions of two concepts
def compute_average_cosine_similarity(concept1, concept2, po_language):
    # Load concepts
    concept_1 = load_concepts(concept1, po_language)
    concept_2 = load_concepts(concept2, po_language)

    # Compute the average cosine similarity
    if concept_1 and concept_2:
        cosine_similarity = 0.0
        counter = 0

        # Descriptions of the first concept
        desc_text_1 = ''
        for desc_1 in concept_1['wh-desc']:
            # Replace the html tags with tags
            if len(concept_1['name']) > 1:
                words = word_tokenize(desc_1)
                for index, word in enumerate(words):
                    if concept_1['name'] == word or '<'+concept_1['name']+'>' == word:
                        words[index] = 'tag'
                desc_text_1 += text_preprocessing(' '.join(words))

        # Descriptions of the first concept
        desc_text_2 = ''
        for desc_2 in concept_2['wh-desc']:
            # Replace the html tags with tags
            if len(concept_2['name']) > 1:
                words = word_tokenize(desc_2)
                for index, word in enumerate(words):
                    if concept_2['name'] == word or '<'+concept_2['name']+'>' == word:
                        words[index] = 'tag'
                desc_text_2 += text_preprocessing(' '.join(words))

        # Compute the cosine similarity
        cosine_similarity += compute_cosine_similarity(desc_text_1, desc_text_2)
        return cosine_similarity
    else:
        return -1.0

class Comparator(Resource):
    def get(self):
        return {
            'status': 200,
            'message': 'Comparator endpoint'
        }
    
    def post(self):
        # Create parser
        parser = reqparse.RequestParser()
        parser.add_argument('po_language', type=str)
        parser.add_argument('concept_1', type=str)
        parser.add_argument('concept_2', type=str)

        try:
            # Data and Tag
            args = parser.parse_args()
            po_language = args['po_language']
            concept_1_name = args['concept_1']
            concept_2_name = args['concept_2']

            # Compute the average cosine similarity
            cosine_similarity = compute_average_cosine_similarity(concept_1_name, concept_2_name, po_language)
            return {
                'status': 200,
                'cosine_similarity': cosine_similarity
            }

        except Exception as e:
            print(e)
            return {
                'status': 500,
                'cosine_similarity': -1.0
            }

if __name__ == "__main__": 
   print(compute_average_cosine_similarity('strong', 'strong', 'html'))