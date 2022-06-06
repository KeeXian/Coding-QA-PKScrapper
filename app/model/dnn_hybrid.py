from multiprocessing.dummy import Array
import numpy as np
import pandas as pd

import nltk
from typing import Dict

# Load glove model for preprocessing
from app.model.gensim_loader import load_glove_model
from app.model.lstm import load_saved_model, add_padding
from app.model.preprocessor import text_preprocessing

class RuleAugmentedEstimator():

    def __init__(self, base_model, glove_filename, rules: Dict, labels: Array):
        """Initializes the RuleAugmentedEstimator instance.
        Initializes the rule-augmented estimator by supplying the underlying
        sklearn estimator as well as the hard-coded rules.
        Args:
            base_model: The underlying dnn classifier.
              Must implement a fit and predict method.
            rules: The hard-coded rules in the format of a dictionary,
              with keys being the pandas dataframe column name, and the values
              being a tuple in the following form:
              
              (comparison operator, value, return value)
              Acceptable comparison operators are:
              "=", "<", ">", "<=", ">="
              Example:
              
              {"House Type": [
                  ("=", "Penthouse", 1.0),
                  ("=", "Shack", 0.0)
               ],
               "House Price": [
                   ("<", 1000.0, 0.0),
                   (">=", 500000.0, 1.0)
              ]}
        Examples:
            The below example illustrates how an instance of the 
            RuleAugmentedEstimator class can be initialized with a trained 
            sklearn GradientBoostingRegressor instance.
            >>> gbr = GradientBoostingRegressor()
            >>> rules = {"House Type": [
                            ("=", "Penthouse", 1.0),
                            ("=", "Shack", 0.0)
                         ],
                         "House Price": [
                            ("<", 1000.0, 0.0),
                            (">=", 500000.0, 1.0)
                        ]}
            >>> ra_estimator = RuleAugmentedEstimator(gbr, rules)
        """
        self.rules = rules
        self.base_model = load_saved_model(base_model)
        self.glove_model = load_glove_model(glove_filename)
        self.word_not_found = []
        self.english_words = set(nltk.corpus.words.words())
        self.labels = labels

    def __repr__(self):
        return "Rule Augmented Estimator:\n\n\t DNN Model: {}\n\t Rules: {}".format(self.base_model, self.rules)

    def __str__(self):
         return self.__str__

    # Convert words into word vectors
    def vectorizer(self, input):
        words = sorted(list(input.split()))
        word_vectors = []

        for word in words:
            try:
                word_vectors.append(self.glove_model.get_vector(word))
            except:
                if word not in self.word_not_found:
                    self.word_not_found.append(word)
                word_vectors.append(np.zeros(200))

        return word_vectors

    # Convert a batch of text data into word vectors
    def vectorize_batch(self, input):
    
        preprocessed_input = []
        for sentence in input:
            word_vectors = self.vectorizer(sentence)
            preprocessed_input.append(word_vectors)
        
        return preprocessed_input
    
    def predict(self, X: pd.DataFrame) -> np.array:
        """Gets predictions for the provided feature data.
        
        The predicitons are evaluated using the provided rules wherever possible
        otherwise the underlying estimator is used.
        
        Args:
            X: The feature data to evaluate predictions for.
        
        Returns:
            np.array: Evaluated predictions.
        """
        
        p_X = X.copy()
        p_X['prediction'] = np.nan

        for category, rules in self.rules.items():

            if category not in p_X.columns.values: continue

            for rule in rules:

                if rule[0] == "=":
                    p_X.loc[p_X[category] == rule[1], 'prediction'] = rule[2]

                elif rule[0] == "<":
                    p_X.loc[p_X[category] < rule[1], 'prediction'] = rule[2]

                elif rule[0] == ">":
                    p_X.loc[p_X[category] > rule[1], 'prediction'] = rule[2]

                elif rule[0] == "<=":
                    p_X.loc[p_X[category] <= rule[1], 'prediction'] = rule[2]

                elif rule[0] == ">=":
                    p_X.loc[p_X[category] >= rule[1], 'prediction'] = rule[2]
                
                elif rule[0] == "contains":
                    p_X.loc[p_X[category].str.contains(rule[1]), 'prediction'] = rule[2]

                elif rule[0] == "match":
                    p_X.loc[p_X[category].str.match(rule[1]), 'prediction'] = rule[2]
                
                elif rule[0] == "length":
                    p_X.loc[p_X[category].str.len < rule[1], 'prediction'] = rule[2]

                else:
                    print("Invalid rule detected: {}".format(rule))

        if len(p_X.loc[p_X['prediction'].isna()].index != 0):

            base_X = p_X.loc[p_X['prediction'].isna()].copy()
            base_X.drop('prediction', axis=1, inplace=True)
            base_X['tag'] = base_X['tag'].apply(text_preprocessing)
            
            # Perform vectorization with glove model here
            base_X = self.vectorize_batch(base_X['tag'].values)
            base_X = add_padding(base_X)

            # Perform prediction with base model
            predictions = []
            model_output = self.base_model.predict(base_X)
            for prediction in model_output:
                predictions.append(self.labels[np.argmax(prediction)])
            
            p_X.loc[p_X['prediction'].isna(), 'prediction'] = predictions

        return p_X['prediction'].values
    