import time

from spacy.lang import en as english
from spacy import load


def load_nlp_model() -> english:
    start = time.time()
    model = load('en_core_web_sm')
    end = time.time()
    print(f"NLP Model loaded in {round(end - start, 2)} seconds")
    return model


def main():
    model = load_nlp_model()


if __name__ == '__main__':
    main()
