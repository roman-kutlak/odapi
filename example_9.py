import os
from pprint import pprint

from odapi_client import *

# TODO: replace with your own
app_id, app_key = os.environ['app_id'], os.environ['app_key']
url = 'https://od-api.oxforddictionaries.com/api/v1/stats/frequency/ngrams/en/nmc/2/'

if __name__ == '__main__':
    client = Client(app_id=os.environ['app_id'], app_key=os.environ['app_key'])
    ngrams = client.ngrams(n=2, contains='testing', length=10)
    pprint(ngrams)
    pprint(('length:', len(ngrams)))
    pprint(('# of requests:', client.num_queries))
