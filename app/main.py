# -*- coding: utf-8 -*-
"""
Main module of the application

This module is the main module that creates the Flask Restful API with all its endpoints.
"""
from flask import Flask
from flask_restful import Api

# Import endpoints
from app.endpoints.scrapper_endpoint import Scrapper

# Initialize the flask application 
app = Flask(__name__)
api = Api(app)

# Add scrapper to the api
api.add_resource(Scrapper, '/scrapper')