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


class OptionsTestCase(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)

        @self.app.route('/test_default', methods=['OPTIONS'])
        @cross_origin(self.app)
        def test_default(request):
            return text('Welcome!')

        @self.app.route('/test_async_default', methods=['GET', 'OPTIONS'])
        @cross_origin(self.app)
        async def test_async_default(request):
            return text('Async Welcome!')

        @self.app.route('/test_no_options_and_not_auto', methods=['GET', 'POST', 'PUT', 'DELETE'])
        @cross_origin(self.app, automatic_options=False)
        def test_no_options_and_not_auto(request):
            return text('Welcome!')

        @self.app.route('/test_options_and_not_auto', methods=['OPTIONS'])
        @cross_origin(self.app, automatic_options=False)
        def test_options_and_not_auto(request):
            return text('Welcome!')

    def test_defaults(self):
        '''
            The default behavior should automatically provide OPTIONS
            and return CORS headers.
        '''
        resp = self.options('/test_default', origin='http://foo.bar.com')
        self.assertEqual(resp.status, 200)
        self.assertTrue(ACL_ORIGIN in resp.headers)

        # TODO: this is duplicated (from flask-cors)
        resp = self.options('/test_default', origin='http://foo.bar.com')
        self.assertEqual(resp.status, 200)
        self.assertTrue(ACL_ORIGIN in resp.headers)

        resp = self.options('/test_async_default', origin='http://foo.bar.com')
        self.assertEqual(resp.status, 200)
        self.assertTrue(ACL_ORIGIN in resp.headers)

        resp = self.get('/test_async_default', origin='http://foo.bar.com')
        self.assertEqual(resp.status, 200)
        self.assertTrue(ACL_ORIGIN in resp.headers)
        self.assertEqual(resp.body, b"Async Welcome!")


    def test_no_options_and_not_auto(self):
        '''
            If automatic_options is False, and the view func does not provide
            OPTIONS, then Sanic will throw a 405 Method not Allowed
        '''
        resp = self.options('/test_no_options_and_not_auto')
        self.assertEqual(resp.status, 405)
        self.assertFalse(ACL_ORIGIN in resp.headers)

        resp = self.options('/test_no_options_and_not_auto', origin='http://foo.bar.com')
        self.assertEqual(resp.status, 405)
        self.assertFalse(ACL_ORIGIN in resp.headers)

    def test_options_and_not_auto(self):
        '''
            If OPTIONS is in methods, and automatic_options is False,
            the view function must return a response.
        '''
        resp = self.options('/test_options_and_not_auto', origin='http://foo.bar.com')
        self.assertEqual(resp.status, 200)
        self.assertTrue(ACL_ORIGIN in resp.headers)
        self.assertEqual(resp.body.decode("utf-8"), u"Welcome!")

        # TODO: This is duplicated (from flask-cors)
        resp = self.options('/test_options_and_not_auto', origin='http://foo.bar.com')
        self.assertEqual(resp.status, 200)
        self.assertTrue(ACL_ORIGIN in resp.headers)
        self.assertEqual(resp.body.decode("utf-8"), u"Welcome!")

if __name__ == "__main__":
    unittest.main()
