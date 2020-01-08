# -*- coding: utf-8 -*-
"""
    test
    ~~~~

    Sanic-Cors tests module
"""

from ..base_test import SanicCorsTestCase
from sanic import Sanic
from sanic.response import HTTPResponse
try:
    # Sanic compat Header from Sanic v19.9.0 and above
    from sanic.compat import Header as CIMultiDict
except ImportError:
    try:
        # Sanic server CIMultiDict from Sanic v0.8.0 and above
        from sanic.server import CIMultiDict
    except ImportError:
        raise RuntimeError("Your version of sanic does not support "
                           "CIMultiDict")
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
            resp.headers['set-cookie'] = 'foo'
            resp.headers.add('set-cookie', 'bar')
            return resp

    def test_multiple_set_cookie_headers(self):
        resp = self.get('/test_multiple_set_cookie_headers')
        try:
            # Sanic compat Header, in 19.9.0 and above
            cookies = set(resp.headers.get_all('set-cookie'))
        except AttributeError:
            try:
                # Sanic CIMultiDict, in v0.8.0 and above
                cookies = set(resp.headers.getall('set-cookie'))
            except AttributeError:
                try:
                    # Sanic Test Client in Sanic 19.12.0 and above.
                    cookies = set(resp.headers.getlist('set-cookie',
                                                     split_commas=True))
                except AttributeError:
                    cookies = set(resp.headers.get('set-cookie').split(','))
        cookies = set(x.strip().lower() for x in cookies)
        self.assertEqual(cookies, {'foo', 'bar'})
        self.assertEqual(len(cookies), 2)

if __name__ == "__main__":
    unittest.main()
