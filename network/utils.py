import re
from keras.preprocessing.text import one_hot
from keras.preprocessing.sequence import pad_sequences
import tensorflow as tf


# Load your TensorFlow SavedModel
model = tf.keras.models.load_model('E:/Book Bimarsha Social/Book Bimarsha Social Final/network/IMDB_sentiment_analysis_final')


def preprocess_and_predict(sentence, vocabulary_size=5000, max_length=500):
     # Lowercasing
    sentence = sentence.lower()
    # Remove punctuation
    sentence = re.sub(r'[^\w\s]', ' ', sentence)
    # One-hot encoding
    encoded = one_hot(sentence, vocabulary_size)
    # Padding
    padded = pad_sequences([encoded], maxlen=max_length, padding='post')
    
    # Convert the processed_text to a Tensor
    processed_text_tensor = tf.constant(padded, dtype=tf.float32)
    
    # Make predictions using the model
    prediction = model.predict(processed_text_tensor)
    return prediction[0][0]
