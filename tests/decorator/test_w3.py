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
from sanic.response import text
from sanic_cors import *
from sanic_cors.core import *


class OriginsW3TestCase(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)

        @self.app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, origins='*', send_wildcard=False, always_send=False)
        def allowOrigins(request):
            ''' This sets up sanic-cors to echo the request's `Origin` header,
                only if it is actually set. This behavior is most similar to
                the actual W3 specification, http://www.w3.org/TR/cors/ but
                is not the default because it is more common to use the
                wildcard configuration in order to support CDN caching.
            '''
            return text('Welcome!')

        @self.app.route('/default-origins', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, send_wildcard=False, always_send=False)
        def noWildcard(request):
            ''' With the default origins configuration, send_wildcard should
                still be respected.
            '''
            return text('Welcome!')

    def test_wildcard_origin_header(self):
        ''' If there is an Origin header in the request, the
            Access-Control-Allow-Origin header should be echoed back.
        '''
        example_origin = 'http://example.com'
        headers = {'Origin': example_origin}
        for resp in self.iter_responses('/', headers=headers):
            self.assertEqual(
                resp.headers.get(ACL_ORIGIN),
                example_origin
            )

    def test_wildcard_no_origin_header(self):
        ''' If there is no Origin header in the request, the
            Access-Control-Allow-Origin header should not be included.
        '''
        for resp in self.iter_responses('/'):
            self.assertTrue(ACL_ORIGIN not in resp.headers)

    def test_wildcard_default_origins(self):
        ''' If there is an Origin header in the request, the
            Access-Control-Allow-Origin header should be echoed back.
        '''
        example_origin = 'http://example.com'
        headers = {'Origin': example_origin}
        for resp in self.iter_responses('/default-origins', headers=headers):
            self.assertEqual(resp.headers.get(ACL_ORIGIN), example_origin)


if __name__ == "__main__":
    unittest.main()
