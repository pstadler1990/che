import yaml
import nltk
from bs4 import BeautifulSoup
from langdetect import detect
from nltk.corpus import stopwords
from textblob import TextBlob
from nltk.tokenize import RegexpTokenizer


config = yaml.safe_load(open('config.yml'))
tokenizer = RegexpTokenizer(r'\w+')


def _text_get_lang(text):
    return detect(text)


def _text_get_nouns(text):
    # TODO: Try replacing with nltk as textblob's performance (especially on German) isn't that good..
    return TextBlob(text).noun_phrases


def _clear_html(content):
    return BeautifulSoup(content, 'lxml').text


def _remove_stopwords(tokens, language='english'):
    return list(filter(lambda word: (word not in stopwords.words(language)
                                     and str(word).isalpha()) and len(word) > config['processing']['min_word_length'], tokens))


def _str_get_tokens(text):
    return [token.lower() for token in tokenizer.tokenize(text)]


def _get_word_frequencies(tokens):
    return nltk.FreqDist(tokens)


def nlp_process(content, clear_html=True, extract_keywords=True, summerize=True):
    return [], []
    # content_cleared = _clear_html(content) if clear_html else content
    #
    # nouns = _text_get_nouns(content_cleared)
    #
    # tokens = _str_get_tokens(content_cleared)
    # filtered_tokens = _remove_stopwords(tokens)
    # word_frequencies = _get_word_frequencies(filtered_tokens)
    #
    # # TODO: Only use nouns as keywords
    #
    # return word_frequencies.most_common(15) if extract_keywords else None, ''
