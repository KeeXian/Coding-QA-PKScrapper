# NoSQL database for storing programming concepts and its configurations
import pymongo

# Establish connection
conn = "mongodb+srv://KeeXian:BoQNvdupdznEhqLF@programmingknowledgedat.m95zw.mongodb.net/ProgrammingKnowledgeDatabase?retryWrites=true&w=majority"
client = pymongo.MongoClient(conn, connect=False)
db = client.ProgrammingKnowledge
print('Successfully established connection to database')

# Reset collections
def reset_collections():
    db.PO_language.drop()
    db.Topic.drop()
    db.Concept.drop()
    db.Example.drop()
    
    db.create_collection('PO_language')
    db.create_collection('Topic')
    db.create_collection('Concept')
    db.create_collection('Example')
    print('Collections reset')

# Insert language data
def insert_language(language):

    collection = db.PO_language
    if collection.find_one({'name': language['name']}) is None:
        collection.insert_one({
            'name': language['name'],
            'desc': language['desc'],
            'example': language['examples']
        })
        print('Successfully inserted language: ', language['name'], ' into the database.')
    else:
        print('Language: ', language['name'], ' already exists in the database.')


# Update programming language data
def update_language(language):

    collection = db.PO_language
    if collection.find_one({'name': language['name']}) is not None:
        collection.update_one({'name': language['name']}, {'$set': {'desc': language['desc'], 'example': language['examples']}})
        print('Successfully updated language: ', language['name'], ' in the database.')
    else:
        print('Language: ', language['name'], ' not found in the database.')


# Insert topic data
def insert_topic(topic):

    collection = db.Topic
    if collection.find_one({'title': topic['title']}) is None:
        collection.insert_one({
            'title': topic['title'],
            'desc': topic['desc'],
        })
    
    return ('Successfully inserted topic: ', topic['title'])


# Update topic data
def update_topic(topic):

    collection = db.Topic
    if collection.find_one({'title': topic['title']}) is not None:
        collection.update_one({'title': topic['title']}, {'$set': {'desc': topic['desc'], 'example': topic['examples']}})
        print('Successfully updated topic: ', topic['title'], ' in the database.')
    else:
        print('Topic: ', topic['title'], ' not found in the database.')

# Insert concept data
def insert_concept(concept, language='', topic=''):

    collection = db.Concept
    data = {
        'language': db.PO_language.find_one({'name': language})['_id'],
        # 'topic': db.topic.find_one({'name': topic})['_id'],
        'name': concept['name'],
        'wh-desc': concept['wh-desc'].tolist(),
        'how-desc': concept['how-desc'].tolist(),       
    }

    if collection.find_one({'name': data['name']}) is None:
        try:
            collection.insert_one(data)
            print('Successfully inserted concept: ', data['name'])
        except pymongo.errors.InvalidDocument:
            print('Invalid document')


# Insert example data
def insert_example(examples, concept):
    collection = db.Example

    for example in examples['examples']:
        data = {
            'concept': db.Concept.find_one({'name': concept})['_id'],
            'example': example,
            'type': 'short'
        }
        if collection.find_one({'example': data['example']}) is None:
            try:
                collection.insert_one(data)
                print('Successfully inserted example: ', data['example'])
            except pymongo.errors.InvalidDocument:
                print('Invalid document')


def close_connection():
    client.close()
