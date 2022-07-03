from flask import Flask
from flask_restful import Api

# Import endpoints
from app.endpoints.scrapper_endpoint import Scrapper
from app.endpoints.comparator_endpoint import Comparator

# Initialize the flask application 
app = Flask(__name__)
api = Api(app)

# Add scrapper to the api
api.add_resource(Scrapper, '/scrapper')
api.add_resource(Comparator, '/comparator')