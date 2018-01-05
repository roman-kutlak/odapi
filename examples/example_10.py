"""
Example of using the client library

"""

import os
from pprint import pprint

from odapi_client import *

if __name__ == '__main__':
    # TODO: replace with your own credentials credentials
    client = Client(app_id=os.environ['app_id'], app_key=os.environ['app_key'])
    words = ['test', 'unit test', 'smoke test']
    for word in words:
        res = client.frequency('test')
        pprint((word, res))
    res = client.frequencies(*words)
    pprint(res)
    pprint(('# of requests:', client.num_queries))
