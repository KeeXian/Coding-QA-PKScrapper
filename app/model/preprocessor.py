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

# Function to lemmatize text
def lemmatize_text(text):
    def get_wordnet_pos(word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)

    return " ".join([lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in tokenizer.tokenize(text) if word in english_words])

# Function to perform text preprocessing
def text_preprocessing(text):
    """
    This function processes the text and returns the processed text
    """
    text = text.lower()
    text = re.sub('<[^<]+?>', 'TAG', text)
    text = lemmatize_text(text)
    return text