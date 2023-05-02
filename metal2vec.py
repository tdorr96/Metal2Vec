import os
import json
import gensim
from nltk.tokenize import sent_tokenize, word_tokenize


class MySentences(object):

    def __init__(self, data_dir='band_data/', lowercase=True):

        self.data_dir = data_dir
        self.lowercase = lowercase

    def __iter__(self):

        for file_name in os.listdir(self.data_dir):

            if not file_name.endswith('.json'):
                # Don't try and process non-jsons, e.g. ".DS_Store"!
                continue

            with open(os.path.join(self.data_dir, file_name), 'r') as open_f:
                band = json.load(open_f)

            for band_review in band['Band Reviews']:

                # `sent_tokenize` doesn't consider new lines without punctuation as sentence boundaries,
                # so first split into paragraphs, which is basically a collection of sentences
                paragraphs = [p for p in band_review.split('\n') if p]
                for para in paragraphs:
                    for sent in sent_tokenize(para):
                        if self.lowercase:
                            sent = sent.lower()
                        yield word_tokenize(sent)


def train_model(model_name_to_save):

    sentences = MySentences()
    model = gensim.models.Word2Vec(sentences)
    model.save(model_name_to_save)


if __name__ == '__main__':

    train_model('metal2vec.model')
