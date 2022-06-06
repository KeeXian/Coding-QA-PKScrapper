# This file functions to use machine learning to predict the tag of a given description.

# Importing the libraries
import numpy as np
import pandas as pd

# Function for Text Processing
from sklearn.preprocessing import LabelEncoder
from app.model.dnn_hybrid import RuleAugmentedEstimator

# Function to build a dnn model using the following files:
# 1. model.h5
# 2. glove.6B.300d.gs
# 3. data.csv
def build_model(csv_file, model_file, glove_file):
    """
    This function loads the model
    """
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
   
    rules = {
        "tag": [
            ("contains", "tip", "TIP"),
            ("match", "^[0-9]*$", "NUMBER"),
            ("match", "^[0-9]*[.][0-9]*$", "NUMBER"),
            ("contains", "^the [^ ]+( HTML| html)? tag|element", "DESC"),
            ("contains", "^to", "INS"),
            ("length", 7, "TIP"),
            ("contains", "global attributes", "INFO"),
            ("contains", "event attributes", "INFO"),
            ("contains", "in this example", "INFO"),
        ]
    }
    classifier = RuleAugmentedEstimator(model_file, glove_file, rules, labels)
    return classifier, labels
  

def predict_desc(list_of_desc, model, labels):
    """
    This function predicts the type of description of a given list of descriptions
    """
    list_of_desc = pd.DataFrame({'tag': list_of_desc})
    list_of_desc['tag'] = list_of_desc['tag'].str.lower()
    predictions = model.predict(list_of_desc)
    return predictions
