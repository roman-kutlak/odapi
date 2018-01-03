import requests

import unittest
import unittest.mock

from odapi_client import Client, OupClientError, RequestError


class TestClient(unittest.TestCase):

    def test_request_error(self):
        with unittest.mock.patch('odapi_client.requests') as requests_mock:
            requests_mock.get().status_code = 400
            client = Client(app_id='hoover', app_key='craft')
            self.assertRaises(RequestError, client.request, '/', {})


if __name__ == '__main__':
    unittest.main()
