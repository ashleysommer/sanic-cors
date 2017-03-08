# -*- coding: utf-8 -*-
"""
    test
    ~~~~
    Sanic-CORS is a simple extension to Sanic allowing you to support cross
    origin resource sharing (CORS) using a simple decorator.

    :copyright: (c) 2017 by Ashley Sommer (based on flask-cors by Cory Dolphin).
    :license: MIT, see LICENSE for more details.
"""
from datetime import timedelta
import sys
from ..base_test import SanicCorsTestCase
from sanic import Sanic
from sanic.response import text

from sanic_cors import *
from sanic_cors.core import *


class MaxAgeTestCase(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)

        @self.app.route('/defaults')
        @cross_origin(self.app)
        def defaults(request):
            return text('Should only return headers on OPTIONS')

        @self.app.route('/test_string', methods=['GET', 'OPTIONS'])
        @cross_origin(self.app, max_age=600)
        def test_string(request):
            return text('Open!')

        @self.app.route('/test_time_delta', methods=['GET', 'OPTIONS'])
        @cross_origin(self.app, max_age=timedelta(minutes=10))
        def test_time_delta(request):
            return text('Open!')

    def test_defaults(self):
        ''' By default, no max-age headers should be returned
        '''
        for resp in self.iter_responses('/defaults', origin='www.example.com'):
            self.assertFalse(ACL_MAX_AGE in resp.headers)

    def test_string(self):
        ''' If the methods parameter is defined, always return the allowed
            methods defined by the user.
        '''
        resp = self.preflight('/test_string', origin='www.example.com')
        self.assertEqual(resp.headers.get(ACL_MAX_AGE), '600')

    def test_time_delta(self):
        ''' If the methods parameter is defined, always return the allowed
            methods defined by the user.
        '''
        # timedelta.total_seconds is not available in older versions of Python
        if sys.version_info < (2, 7):
            return

        resp = self.preflight('/test_time_delta', origin='www.example.com')
        self.assertEqual(resp.headers.get(ACL_MAX_AGE), '600')


if __name__ == "__main__":
    unittest.main()
