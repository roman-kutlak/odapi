"""
A client wrapper for the Oxford Dictionaries API.

"""

import requests

__all__ = ['Client', 'OupClientError', 'ConfigError', 'RequestError', 'ArgumentError']


class OupClientError(Exception):
    """General Client Error"""


class RequestError(OupClientError):
    """HTTP Request error"""
    def __init__(self, msg, response):
        super().__init__(msg)
        self.response = response


class ArgumentError(OupClientError):
    """Error representing incorrect/conflicting arguments passed to a client"""


class ConfigError(OupClientError):
    """Error representing incorrect configuration of a client"""


class Client(object):
    """The client wraps requests calls and provides sensible defaults to simplify querying the OD API"""

    def __init__(self, endpoint='https://od-api.oxforddictionaries.com/api/v1', app_id=None, app_key=None, headers=None):
        self.endpoint = endpoint
        self.headers = headers or {}
        if app_id:
            self.headers.setdefault('app_id', app_id)
        if app_key:
            self.headers.setdefault('app_key', app_key)
        if not (self.headers.get('app_id') and self.headers.get('app_key')):
            raise ConfigError('You need to provide the API credentials: app_id and app_key')
        if self.headers.setdefault('Accept', 'application/json') not in ('application/json', ):
            raise ConfigError('The client can consume only JSON')

    def frequency(self, word, lexical_category=None):
        """Retrieve a frequency of a word or a phrase."""
        n = word.count(' ')
        if n:
            return self.ngram_frequency(n + 1, word)
        else:
            return self.word_frequency(tc=word, lexical_category=lexical_category)

    def word_frequency(self, tc='', lemma='', wordform='', lexical_category=''):
        """Retrieve a frequency of a given word based on the provided params."""
        result = self.word_stats(tc, lemma, wordform, lexical_category)
        return result['frequency']

    def words_stats(self, tc='', lemma='', wordform='', lexical_category='', **kwargs):
        """Retrieve a list of words and their frequencies based on the provided params."""
        params = kwargs
        if not (tc or lemma or wordform or lexical_category):
            raise ArgumentError('You need to provide at least one of "tc, lemma, wordform, lexical_category".')
        if wordform:
            params['wordform'] = wordform
        if tc:
            params['trueCase'] = tc
        if lemma:
            params['lemma'] = lemma
        if lexical_category:
            params['lexicalCategory'] = lexical_category
        data = self.request('/stats/frequency/words/en/', params=params)
        return data['results']

    def word_stats(self, tc='', lemma='', wordform='', lexical_category='', **kwargs):
        """Retrieve statistical info about a word based on the provided params."""
        params = kwargs
        if not (tc or lemma or wordform or lexical_category):
            raise ArgumentError('You need to provide at least one of "tc, lemma, wordform, lexical_category".')
        if wordform:
            params['wordform'] = wordform
        if tc:
            params['trueCase'] = tc
        if lemma:
            params['lemma'] = lemma
        if lexical_category:
            params['lexicalCategory'] = lexical_category
        data = self.request('/stats/frequency/word/en/', params=params)
        return data['result']

    def ngrams(self, n, *, tokens=None, contains=None, **kwargs):
        """Retrieve a list of ngrams based on the provided params."""
        params = kwargs
        if not (tokens or contains):
            raise ArgumentError('You need to provide one of "tokens, contains".')
        if tokens and contains:
            raise ArgumentError('You need to provide either "tokens" or "contains".')
        if tokens:
            params['tokens'] = tokens
        if tokens:
            params['tokens'] = tokens
        data = self.request('/stats/frequency/ngrams/en/nmc/{}/'.format(n), params=params)
        return data['results']

    def ngram_frequency(self, n, tokens=None, **kwargs):
        """Return the frequency of an ngram."""
        results = self.ngrams(n, tokens=tokens, **kwargs)
        return results[0]['frequency'] if results else 0

    def request(self, path, params):
        r = requests.get(self.endpoint + path, params=params, headers=self.headers)
        if r.status_code != 200:
            raise RequestError('OD API Error', r)
        return r.json()
