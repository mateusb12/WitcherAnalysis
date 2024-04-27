from spacy.lang import en as english
from spacy import load

def load_nlp_model() -> english:
    model = load('en_core_web_sm')
    print("NLP model loaded")
    return model