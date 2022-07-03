from app.scrapper import concept_scrapper, html_style_scrapper
from app.model.ml_model import *

if __name__ == "__main__":
    # concept = concept_scrapper.concept_scrapper('video')
    concept = concept_scrapper.concept_scrapper('img')


    model, labels =  build_model('app/resources/data_test.csv', 'app/resources/model.sav', 'app/resources/glove.6B.300d.gs', 'app/resources/rules.json')
    predicted = predict_desc(concept['desc'], model, labels)
    print(predicted)