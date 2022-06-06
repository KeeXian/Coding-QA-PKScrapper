# load and evaluate a saved model
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences

# Preprocess incoming data to fit the model
def add_padding(x, MAX_LENGTH=30, TRUNCATE_TYPE='post', PADDING_TYPE='post'):
    train_data_padded = pad_sequences(x, maxlen=MAX_LENGTH, truncating=TRUNCATE_TYPE, padding=PADDING_TYPE)
    return train_data_padded

# load model
def load_saved_model(model_name):
    model = load_model(model_name)
    return model

if __name__ == "__main__":
    # Test model
    import numpy as np
    from preprocessor import preprocess_batch

    test_x = preprocess_batch(['A horizontal ruler <hr> tag acts as a simple separator between page sections.', 'To create a link, you will need to specify where you would like the user to be directed to when the link is clicked by specifying the?href?attribute.'])
    labels = ['DESC', 'INFO', 'INS', 'TIP']
    test_x = add_padding(test_x)
    simple_model = load_saved_model('model.h5')
    predictions = simple_model.predict(test_x)

    for prediction in predictions:
        print('Prediction: ',np.argmax(prediction))
        print(labels[np.argmax(prediction)])


    print("Process finished --- %s seconds ---" % (time.time() - start_time))