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


class MethodsCase(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)

        @self.app.route('/defaults', methods=['GET', 'POST', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app)
        def defaults(request):
            return text('Should only return headers on pre-flight OPTIONS request')

        @self.app.route('/test_methods_defined', methods=['POST', 'OPTIONS'])
        @cross_origin(self.app, methods=['POST'])
        def test_get(request):
            return text('Only allow POST')

    def test_defaults(self):
        ''' Access-Control-Allow-Methods headers should only be returned
            if the client makes an OPTIONS request.
        '''

        self.assertFalse(ACL_METHODS in self.get('/defaults', origin='www.example.com').headers)
        self.assertFalse(ACL_METHODS in self.head('/defaults', origin='www.example.com').headers)
        res = self.preflight('/defaults', 'POST', origin='www.example.com')
        for method in ALL_METHODS:
            self.assertTrue(method in res.headers.get(ACL_METHODS))

    def test_methods_defined(self):
        ''' If the methods parameter is defined, it should override the default
            methods defined by the user.
        '''
        self.assertFalse(ACL_METHODS in self.get('/test_methods_defined').headers)
        self.assertFalse(ACL_METHODS in self.head('/test_methods_defined').headers)

        res = self.preflight('/test_methods_defined', 'POST', origin='www.example.com')
        self.assertTrue('POST' in res.headers.get(ACL_METHODS))

        res = self.preflight('/test_methods_defined', 'PUT', origin='www.example.com')
        self.assertFalse(ACL_METHODS in res.headers)

        res = self.get('/test_methods_defined', origin='www.example.com')
        self.assertFalse(ACL_METHODS in res.headers)

if __name__ == "__main__":
    unittest.main()
