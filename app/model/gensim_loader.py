# -*- coding: utf-8 -*-
"""
Gensim Loader Module

This module contains the function to load and modify gensim models
"""
from gensim.models import KeyedVectors

# Load Standard Word2Vec Glove Model
def load_glove_model(glove_file):
    glove_model = KeyedVectors.load(glove_file)
    return glove_model