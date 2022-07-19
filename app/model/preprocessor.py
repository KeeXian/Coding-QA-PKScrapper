# -*- coding: utf-8 -*-
"""
Preprocessor Module

This module contains the necessary functions to preprocess the text
The main function is the text_preprocessing function
"""
import re
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
nltk.download('punkt')
nltk.download('words')
nltk.download('wordnet')

# Create tokenizer and lemmatizer
tokenizer = nltk.RegexpTokenizer(r'\w+')
lemmatizer = WordNetLemmatizer()
english_words = set(nltk.corpus.words.words())

def lemmatize_text(text):
    """
    This function lemmatizes the text and returns the lemmatized text
    text: string
    return lemmatized text
    """
    def get_wordnet_pos(word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)

    return " ".join([lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in tokenizer.tokenize(text)])

# Function to perform text preprocessing
def text_preprocessing(text):
    """
    This function performs text preprocessing and returns the processed text
    text: string
    return preprocessed text
    """
    text = text.lower()
    text = re.sub('<[^<]+?>', 'TAG', text)
    text = lemmatize_text(text)
    return text

if __name__ == '__main__':
    text = "The <a> tag defines a hyperlink, which is used to link from one page to another."
    print(text_preprocessing(text))