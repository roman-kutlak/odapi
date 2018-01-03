"""
Example usage of the Oxford Dictionaries API

Created: 2018-01-02
Author: Oxford University Press

"""

import os

from odapi_client import Client


class Examples:

    client = Client(app_id=os.environ['app_id'], app_key=os.environ['app_key'])

    def __init__(self, app_id=None, app_key=None, headers=None):
        if app_id and app_key:
            self.client = Client(app_id=app_id, app_key=app_key, headers=headers)

    def simple(self):
        print('net:', self.client.frequency('net'))
        print('Net:', self.client.frequency('Net'))
        print('on the net:', self.client.frequency('on the net'))
        print('on the Net:', self.client.frequency('on the Net'))

    def simple_with_lexical_categories(self):
        words = [
            ('test', 'noun'),
            ('test', 'verb'),
            ('testing', 'noun'),
            ('testing', 'verb')
        ]
        for w, lc in words:
            print(w, lc, self.client.frequency(w, lexical_category=lc))

    def wordforms(self, lemma='test', lexical_category=None):
        """Print wordforms of a lemma found in the corpus"""
        results = self.client.words_stats(lemma=lemma, lexical_category=lexical_category)
        lex_cat = '' if not lexical_category else ' with lexical category "{}"'.format(lexical_category)
        print('Wordforms of lemma "{}"{}'.format(lemma, lex_cat))
        for r in list(sorted(set(r['trueCase'] for r in results))):
            print(r)

    def word_scores(self, words=None):
        words = words or [
            'the', 'head', 'professional', 'radioactive',
            'galvanize', 'merengue', 'satinize', 'NonsenseWord'
        ]
        for w in words:
            print(w, self.word_score(w))

    def word_score(self, word='test'):
        """Return a score of a word based on its frequency"""
        stats = self.client.word_stats(tc=word)
        normalized_freq = stats['normalizedFrequency']
        frequency = stats['frequency']
        basic_score = len(word)
        # http://public.oed.com/how-to-use-the-oed/key-to-frequency/
        if 1000 <= normalized_freq:  # band 8
            multiplier = 0.5
        elif 100 <= normalized_freq < 1000:  # band 7
            multiplier = 0.75
        elif 10 <= normalized_freq < 100:  # band 6
            multiplier = 1.0
        elif 1 <= normalized_freq < 10:  # band 5
            multiplier = 1.25
        elif 0.1 <= normalized_freq < 1:  # band 4
            multiplier = 1.5
        elif 0.01 <= normalized_freq < 0.1:  # band 3
            multiplier = 1.75
        elif 0 < normalized_freq < 0.01:  # band 2
            multiplier = 2.0
        else:  # band 1
            multiplier = 0
        final_score = basic_score * multiplier
        return final_score, multiplier, normalized_freq, frequency

    def more_frequent(self, word1='you and myself', word2='you and I'):
        if self.client.frequency(word1) < self.client.frequency(word2):
            return word2
        return word1

    def frequency(self, word, lexical_category=None):
        return self.client.frequency(word, lexical_category=lexical_category)


if __name__ == '__main__':
    examples = Examples()
    examples.simple()
    examples.simple_with_lexical_categories()
    examples.word_scores()
    examples.more_frequent()
