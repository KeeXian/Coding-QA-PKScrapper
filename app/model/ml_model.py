# -*- coding: utf-8 -*-
"""
Machine Learning Model Module

This module contains the functions to build the machine learning model
The main function is the build_model and predict_desc functions
"""

# Importing the libraries
import numpy as np
import pandas as pd
import json

from sklearn.preprocessing import LabelEncoder
from app.model.ml_hybrid import RuleAugmentedEstimator

def build_model(csv_file, model_file, glove_file, rule_file):
    """
    This function builds a SVM model using the following files:
    1. model.sav
    2. glove.6B.300d.gs
    3. data.csv
    4. rules.json
    Please ensure that the files are in the resources folder
    """
    # Load the data
    data = pd.read_csv(csv_file, encoding='unicode_escape')
    data = data.loc[data['tag'] != 'ATR']
    data = data.loc[data['tag'] != 'EXP']
    data = data.loc[data['tag'] != 'DIFFERENCES']

    X = pd.DataFrame({'tag': data.iloc[:, 1].values})
    # Preprocessing the data
    labelencoder_y = LabelEncoder()
    y = data.iloc[:, 2].values
    y = pd.Series(labelencoder_y.fit_transform(y))
    labels = labelencoder_y.classes_
    
    # Load the model
    rules = json.load(open(rule_file))
    classifier = RuleAugmentedEstimator(model_file, glove_file, rules, labels)
    return classifier, labels
  

def predict_desc(list_of_desc, model, labels):
    """
    This function predicts the type of description of a given list of descriptions
    list_of_desc: list of descriptions
    model: machine learning model
    labels: labels of the descriptions
    """
    list_of_desc = pd.DataFrame({'tag': list_of_desc})
    list_of_desc['tag'] = list_of_desc['tag'].str.lower()
    predictions = model.predict(list_of_desc)
    return predictions
