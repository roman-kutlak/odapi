"""
Example of obtaining first 100 bigrams (2-grams) containing the word "testing"

The API has an implicit limit of 100 results returned in a query. If you want
the remaining items you will have to use the parameter `offset` to iterate
through the results.

"""

import os
import requests
from pprint import pprint

# TODO: replace with your own credentials
app_id, app_key = os.environ['app_id'], os.environ['app_key']
url = 'https://od-api.oxforddictionaries.com/api/v1/stats/frequency/ngrams/en/nmc/2/'

if __name__ == '__main__':
    r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key},
                     params={
                         'contains': 'testing',
                     })
    pprint(r.json() if r.status_code == 200 else r.text)
