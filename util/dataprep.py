# -*- coding: utf-8 -*-
"""dataprep.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1swpf79n5lQfBdFDDrMLF5v5njYvMTDLx
"""

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
import os
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing import sequence

# Paths for GloVe vectors and datasets
_glove_vectors = '/content/drive/MyDrive/myproject/glove.twitter.27B.200d.txt'
_train_path = '/content/drive/MyDrive/myproject/datasets/split/train.csv'
_test_path = '/content/drive/MyDrive/myproject/datasets/split/test.csv'
_val_path = '/content/drive/MyDrive/myproject/datasets/split/val.csv'

def get_glove_embeddings(word_index):
    """Load GloVe embeddings and create an embedding matrix."""
    embeddings_index = {}
    try:
        with open(_glove_vectors, encoding="utf8") as glove_vectors:
            for line in glove_vectors:
                values = line.split()
                word = values[0]
                coefs = np.asarray(values[1:], dtype='float32')
                embeddings_index[word] = coefs
    except Exception as e:
        print(f"Error loading GloVe vectors: {e}")

    # Create embedding matrix
    embedding_matrix = np.zeros((len(word_index) + 1, 200))  # 200 for 200d embeddings
    for word, i in word_index.items():
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector
    return embedding_matrix

def get_vectors(word_index):
    """Get embedding vectors for the words in the vocabulary."""
    return get_glove_embeddings(word_index)

def get_data():
    """Load, clean, and prepare the dataset for model training."""
    # Load datasets
    try:
        train = pd.read_csv(_train_path)
        test = pd.read_csv(_test_path)
        val = pd.read_csv(_val_path)
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return None

    # Concatenate datasets
    df = pd.concat([train, test, val], ignore_index=True)

    # Check for NaN values in the 'body' and 'rating' columns
    print("NaN values in concatenated dataset's rating column:", df['rating'].isna().sum())
    df.dropna(subset=['body', 'rating'], inplace=True)

    # Tokenize sentences
    sentences = df.body.apply(lambda x: str(x).split()).tolist()

    # Set up tokenizer
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(sentences)
    word_index = tokenizer.word_index

    # Get the length of vectors
    vectors = get_vectors(word_index)
    vocab_size = len(word_index) + 1
    embedding_size = 200

    # Make data into tokens
    X = tokenizer.texts_to_sequences(sentences)
    X = sequence.pad_sequences(X)

    # Prepare train, test, and validation data
    X_train = X[0:len(train)]
    y_train = train.rating.values

    X_test = X[len(train):(len(train) + len(test))]
    y_test = test.rating.values

    X_val = X[(len(train) + len(test)):]
    y_val = val.rating.values

    return X_train, y_train, X_test, y_test, X_val, y_val, vocab_size, embedding_size, vectors

# Execute the function to prepare the data
if __name__ == "__main__":
    data = get_data()
    if data:
        X_train, y_train, X_test, y_test, X_val, y_val, vocab_size, embedding_size, vectors = data
        print("Data preparation complete.")