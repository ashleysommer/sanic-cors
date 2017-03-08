# -*- coding: utf-8 -*-
"""
    test
    ~~~~
    Sanic-CORS is a simple extension to Sanic allowing you to support cross
    origin resource sharing (CORS) using a simple decorator.

    :copyright: (c) 2017 by Ashley Sommer (based on flask-cors by Cory Dolphin).
    :license: MIT, see LICENSE for more details.
"""

from ..base_test import SanicCorsTestCase
from sanic import Sanic
from sanic.response import HTTPResponse, text
from sanic.server import CIDict

from sanic_cors import *


class VaryHeaderTestCase(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)

        @self.app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app)
        def wildcard(request):
            return text('Welcome!')

        @self.app.route('/test_consistent_origin', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, origins='http://foo.com')
        def test_consistent(request):
            return text('Welcome!')

        @self.app.route('/test_vary', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, origins=["http://foo.com", "http://bar.com"])
        def test_vary(request):
            return text('Welcome!')

        @self.app.route('/test_existing_vary_headers')
        @cross_origin(self.app, origins=["http://foo.com", "http://bar.com"])
        def test_existing_vary_headers(request):
            return HTTPResponse('', status=200, headers=CIDict({'Vary': 'Accept-Encoding'}))

    def test_default(self):
        '''
            By default, allow all domains, which means the Vary:Origin header
            should be set.
        '''
        for resp in self.iter_responses('/', origin="http://foo.com"):
            self.assertTrue('Vary' in resp.headers)

    def test_consistent_origin(self):
        '''
            If the Access-Control-Allow-Origin header will change dynamically,
            the Vary:Origin header should be set.
        '''
        for resp in self.iter_responses('/test_consistent_origin', origin="http://foo.com"):
            self.assertFalse('Vary' in resp.headers)

    def test_varying_origin(self):
        ''' Resources that wish to enable themselves to be shared with
            multiple Origins but do not respond uniformly with "*" must
            in practice generate the Access-Control-Allow-Origin header
            dynamically in response to every request they wish to allow.

            As a consequence, authors of such resources should send a Vary:
            Origin HTTP header or provide other appropriate control directives
            to prevent caching of such responses, which may be inaccurate if
            re-used across-origins.
        '''
        example_origin = 'http://foo.com'
        for resp in self.iter_responses('/test_vary', origin=example_origin):
            self.assertHasACLOrigin(resp)
            self.assertEqual(resp.headers.get('Vary'), 'Origin')

    def test_consistent_origin_concat(self):
        '''
            If Sanic-Cors adds a Vary header and there is already a Vary
            header set, the headers should be combined and comma-separated.
        '''

        resp = self.get('/test_existing_vary_headers', origin="http://foo.com")
        self.assertEqual(set(resp.headers.getall('Vary')),
                         set(['Origin', 'Accept-Encoding']))

if __name__ == "__main__":
    unittest.main()
