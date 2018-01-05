"""
Example of obtaining statistical information about the lemma "test" limited
to verbs.

"""

import os
import requests
from pprint import pprint

# TODO: replace with your own credentials
app_id, app_key = os.environ['app_id'], os.environ['app_key']
url = 'https://od-api.oxforddictionaries.com/api/v1/stats/frequency/word/en/'

if __name__ == '__main__':
    r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key},
                     params={
                         'lemma': 'test',
                         'lexicalCategory': 'verb'
                     })
    pprint(r.json() if r.status_code == 200 else r.text)
