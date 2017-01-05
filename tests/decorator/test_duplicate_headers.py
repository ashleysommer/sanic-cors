# -*- coding: utf-8 -*-
"""
    test
    ~~~~

    Sanic-Cors tests module
"""

from ..base_test import SanicCorsTestCase
from sanic import Sanic
from sanic.response import HTTPResponse
from multidict import CIMultiDict

from sanic_cors import *
from sanic_cors.core import *


class AllowsMultipleHeaderEntries(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)

        @self.app.route('/test_multiple_set_cookie_headers')
        @cross_origin(self.app)
        def test_multiple_set_cookie_headers(request):
            resp = HTTPResponse(body="Foo bar baz")
            resp.headers = CIMultiDict()
            resp.headers.add('set-cookie', 'foo')
            resp.headers.add('set-cookie', 'bar')
            return resp

    def test_multiple_set_cookie_headers(self):
        resp = self.get('/test_multiple_set_cookie_headers')
        self.assertEqual(len(resp.headers.getall('set-cookie')), 2)

if __name__ == "__main__":
    unittest.main()
