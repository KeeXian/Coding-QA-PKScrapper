# This file functions to use machine learning to predict the tag of a given description.

# Importing the libraries
# Importing the libraries
import numpy as np
import pandas as pd
import re
import pickle

# Function for Text Processing
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB

from app.model_old.hybrid import RuleAugmentedEstimator


def build_model(csv_file):
    """
    This function loads the model
    """
    data = pd.read_csv(csv_file, encoding='unicode_escape')
    X = pd.DataFrame({'tag': data.iloc[:, 1].values})
    X['tag'] = X['tag'].str.lower()

    # Preprocessing the data
    labelencoder_y = LabelEncoder()
    y = data.iloc[:, 2].values
    y = pd.Series(labelencoder_y.fit_transform(y))
    labels = labelencoder_y.classes_
   
    rules = {
        "tag": [
            ("contains", "tip", "TIP"),
        ]
    }
    classifier = RuleAugmentedEstimator(MultinomialNB(), CountVectorizer(max_features=1500), rules)
    classifier.fit(X, y)

    pickle.dump(classifier, open('model.pkl', 'wb'))
    pickle.dump(labelencoder_y, open('labels.pkl', 'wb'))
    return classifier, labels


def load_model(model_file, label_file):
    """
    This function loads the model
    """
    model = pickle.load(open(model_file, 'rb'))
    labelencoder_y = pickle.load(open(label_file, 'rb'))
    labels = labelencoder_y.classes_
    return [model, labels]


def predict_desc(list_of_desc, model, labels):
    """
    This function predicts the type of description of a given list of descriptions
    """
    # Convert input array to dataframe
    list_of_desc = pd.DataFrame({'tag': list_of_desc})
    list_of_desc['tag'] = list_of_desc['tag'].str.lower()

    # Predict
    predictions = model.predict(list_of_desc)
    labelList = []
    for prediction in predictions:
        if type(prediction) == int:
            labelList.append(labels[prediction])
        else:
            labelList.append(prediction)

    return labelList
