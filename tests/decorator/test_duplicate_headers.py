# -*- coding: utf-8 -*-
"""
    test
    ~~~~

    Sanic-Cors tests module
"""

from ..base_test import SanicCorsTestCase
from sanic import Sanic
from sanic.response import HTTPResponse
from sanic.server import CIDict

from sanic_cors import *
from sanic_cors.core import *


class AllowsMultipleHeaderEntries(SanicCorsTestCase):
    """
    Note, under the new change in Sanic 0.3.0, where Sanic changed from using multidict.CIMultiDict
    to its own CIDict implementation, we can no longer store multiple versions of the same header.
    """
    def setUp(self):
        self.app = Sanic(__name__)

        @self.app.route('/test_multiple_set_cookie_headers')
        @cross_origin(self.app)
        def test_multiple_set_cookie_headers(request):
            resp = HTTPResponse(body="Foo bar baz")
            resp.headers = CIDict()
            resp.headers['set-cookie'] = 'foo'
            resp.headers['set-cookie'] = 'bar'
            return resp

    def test_multiple_set_cookie_headers(self):
        resp = self.get('/test_multiple_set_cookie_headers')
        self.assertEqual(resp.headers.get('set-cookie'), 'bar')
        #self.assertEqual(len(resp.headers.get_all('set-cookie')), 2)

if __name__ == "__main__":
    unittest.main()
