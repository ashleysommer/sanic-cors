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


class SupportsCredentialsCase(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)

        @self.app.route('/test_credentials_supported')
        @cross_origin(self.app, supports_credentials=True)
        def test_credentials_supported(request):
            return text('Credentials!')

        @self.app.route('/test_credentials_unsupported')
        @cross_origin(self.app, supports_credentials=False)
        def test_credentials_unsupported(request):
            return text('Credentials!')

        @self.app.route('/test_default')
        @cross_origin(self.app)
        def test_default(request):
            return text('Open!')

    def test_credentials_supported(self):
        ''' The specified route should return the
            Access-Control-Allow-Credentials header.
        '''
        resp = self.get('/test_credentials_supported', origin='www.example.com')
        self.assertEquals(resp.headers.get(ACL_CREDENTIALS), 'true')

    def test_default(self):
        ''' The default behavior should be to disallow credentials.
        '''
        resp = self.get('/test_default', origin='www.example.com')
        self.assertFalse(ACL_CREDENTIALS in resp.headers)

        resp = self.get('/test_default')
        self.assertFalse(ACL_CREDENTIALS in resp.headers)

    def test_credentials_unsupported(self):
        ''' The default behavior should be to disallow credentials.
        '''
        resp = self.get('/test_credentials_unsupported', origin='www.example.com')
        self.assertFalse(ACL_CREDENTIALS in resp.headers)

        resp = self.get('/test_credentials_unsupported')
        self.assertFalse(ACL_CREDENTIALS in resp.headers)

if __name__ == "__main__":
    unittest.main()
