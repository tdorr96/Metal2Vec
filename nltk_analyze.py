import os
import json
from nltk.tokenize import word_tokenize
from nltk.text import Text, TextCollection


def init_text_collection_object(data_dir='band_data', lowercase=True):
    # Initialize an NLTK Text object for each review, then store all of them in an NLTK TextCollection object

    all_texts = []

    for file_name in os.listdir(data_dir):

        if not file_name.endswith('.json'):
            # Don't try and process non-jsons, e.g. ".DS_Store"!
            continue

        with open(os.path.join(data_dir, file_name), 'r') as open_f:
            band = json.load(open_f)

        for band_review in band['Band Reviews']:

            if lowercase:
                band_review = band_review.lower()

            review_tokens = word_tokenize(band_review)
            all_texts.append(Text(review_tokens))

    return TextCollection(all_texts)
