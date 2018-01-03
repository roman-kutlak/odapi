"""
Example usage of the Oxford Dictionaries API

Created: 2018-01-02
Author: Oxford University Press

"""

import os

from odapi_client import Client


def main():
    client = Client(app_id=os.environ['app_id'], app_key=os.environ['app_key'])
    print('net:', client.frequency('net'))
    print('Net:', client.frequency('Net'))
    print('on the net:', client.frequency('on the net'))
    print('on the Net:', client.frequency('on the Net'))
    print('z z z:', client.ngrams(3, tokens='z z z'))
    print('on the Net:', client.ngram_frequency(3, tokens='on the Net'))
    print('z z z:', client.ngram_frequency(3, tokens='z z z'))


if __name__ == '__main__':
    main()
