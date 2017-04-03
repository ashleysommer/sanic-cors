# -*- coding: utf-8 -*-
"""
    test
    ~~~~

    Sanic-Cors tests module
"""

from ..base_test import SanicCorsTestCase
from sanic import Sanic
from sanic.response import text
from sanic_cors import *
from sanic_cors.core import *


class ExposeHeadersTestCase(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)

        @self.app.route('/test_default', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app)
        def test_default(request):
            return text('Welcome!')

        @self.app.route('/test_override', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, expose_headers=["X-My-Custom-Header", "X-Another-Custom-Header"])
        def test_override(request):
            return text('Welcome!')

    def test_default(self):
        for resp in self.iter_responses('/test_default', origin='www.example.com'):
            self.assertTrue(resp.headers.get(ACL_EXPOSE_HEADERS) is None,
                            "No Access-Control-Expose-Headers by default")

    def test_override(self):
        ''' The specified headers should be returned in the ACL_EXPOSE_HEADERS
            and correctly serialized if it is a list.
        '''
        for resp in self.iter_responses('/test_override', origin='www.example.com'):
            self.assertEqual(resp.headers.get(ACL_EXPOSE_HEADERS),
                             'X-Another-Custom-Header, X-My-Custom-Header')

if __name__ == "__main__":
    unittest.main()
