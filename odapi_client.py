"""
A client wrapper for the Oxford Dictionaries API.

"""

import requests
import collections

from math import log2

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

    _corpus_size = None

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

    @property
    def corpus_size(self):
        if self._corpus_size is None:
            the_stats = self.word_stats(wordform='the')
            Client._corpus_size = the_stats['normalizedFrequency'] * 1000 * 1000
        return self._corpus_size

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
        # TODO: add loop for limit + offset
        return data['results']

    def ngrams(self, n, *, tokens=None, contains=None, **kwargs):
        """Retrieve a list of ngrams based on the provided params."""
        params = kwargs
        if not (tokens or contains):
            raise ArgumentError('You need to provide one of "tokens, contains".')
        if tokens and contains:
            raise ArgumentError('You need to provide either "tokens" or "contains".')
        if tokens:
            params['tokens'] = tokens
        if contains:
            params['contains'] = contains
        data = self.request('/stats/frequency/ngrams/en/nmc/{}/'.format(n), params=params)
        # TODO: add loop for limit + offset
        return data['results']

    def ngram_frequency(self, n, tokens=None, **kwargs):
        """Return the frequency of an ngram."""
        results = self.ngrams(n, tokens=tokens, **kwargs)
        return results[0]['frequency'] if results else 0

    def request(self, path, params):
        r = requests.get(self.endpoint + path, params=params, headers=self.headers)
        # TODO: raise more specific errors
        if r.status_code != 200:
            raise RequestError('OD API Error', r)
        rv = r.json()
        if 'results' in rv:
            # lists are limited to 100 elements so query for the rest if necessary
            limit = rv['metadata']['options']['limit']
            offset = rv['metadata']['options']['offset']
            if rv['metadata']['total'] > limit + offset:
                params['offset'] = offset + limit
                rv['results'].extend(self.request(path, params)['results'])
        return rv

    def frequencies(self, *words):
        bigrams = [w for w in words if w.count(' ') == 1]
        trigrams = [w for w in words if w.count(' ') == 2]
        fourgrams = [w for w in words if w.count(' ') == 3]
        tcs = [w for w in words if ' ' not in w]
        if len(bigrams) > 10 or len(trigrams) > 10 or len(fourgrams) > 10 or len(tcs) > 10:
            raise ArgumentError('At most 10 items per query.')
        word_results = tcs and self.request('/stats/frequency/words/en/', {'trueCases': tcs})['results']
        bigram_results = bigrams and self.request('/stats/frequency/ngrams/en/nmc/2/', {'tokens': bigrams})['results']
        trigram_results = trigrams and self.request('/stats/frequency/ngrams/en/nmc/3/', {'tokens': trigrams})['results']
        fourgram_results = fourgrams and self.request('/stats/frequency/ngrams/en/nmc/4/', {'tokens': fourgrams})['results']
        rv = collections.defaultdict(int)
        # collate wordforms by a true case
        for r in word_results:
            rv[r['trueCase']] += r['frequency']
        for r in bigram_results + trigram_results + fourgram_results:
            compound_word = ' '.join(r['tokens'])
            rv[compound_word] += r['frequency']
        # return in the same order as args passed with 0 where word was not present in corpus
        return collections.OrderedDict({k: rv[k] for k in words})

    def pmi(self, w1, w2):
        """Calculate word PMI

        PMI = log2(P(w1, w2) / P(w1) * P(w2))
        PMI(w1, w2) = log2(C(w1, w2)) + log2(N) − log2(C(w1)) − log2(C(w2))

        """
        n = self.corpus_size
        c_w1_w2, c_w1, c_w2 = tuple(self.frequencies(w1 + ' ' + w2, w1, w2).values())
        if not (c_w1_w2 and c_w1 and c_w2):
            return 0.0
        pmi = log2(c_w1_w2) + log2(n) - log2(c_w1) - log2(c_w2)
        return pmi
