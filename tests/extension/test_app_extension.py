# -*- coding: utf-8 -*-
"""
    test
    ~~~~
    Sanic-CORS is a simple extension to Sanic allowing you to support cross
    origin resource sharing (CORS) using a simple decorator.

    :copyright: (c) 2017 by Ashley Sommer (based on flask-cors by Cory Dolphin).
    :license: MIT, see LICENSE for more details.
"""

import re
from ..base_test import SanicCorsTestCase
from sanic import Sanic
from sanic.response import json, text

from sanic_cors import *
from sanic_cors.core import *

letters = 'abcdefghijklmnopqrstuvwxyz'  # string.letters is not PY3 compatible

class AppExtensionRegexp(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)
        CORS(self.app, resources={
            r'/test_list': {'origins': ["http://foo.com", "http://bar.com"]},
            r'/test_string': {'origins': 'http://foo.com'},
            r'/test_set': {
                'origins': set(["http://foo.com", "http://bar.com"])
            },
            r'/test_subdomain_regex': {
                'origins': r"http?://\w*\.?example\.com:?\d*/?.*"
            },
            r'/test_regex_list': {
                'origins': [r".*.example.com", r".*.otherexample.com"]
            },
            r'/test_regex_mixed_list': {
                'origins': ["http://example.com", r".*.otherexample.com"]
            },
            r'/test_send_wildcard_with_origin': {
                'send_wildcard': True
            },
            re.compile('/test_compiled_subdomain_\w*'): {
                'origins': re.compile("http://example\d+.com")
            },
            r'/test_defaults': {}
        })

        @self.app.route('/test_defaults', methods=['GET', 'HEAD', 'OPTIONS'])
        def wildcard(request):
            return text('Welcome!')

        @self.app.route('/test_send_wildcard_with_origin', methods=['GET', 'HEAD', 'OPTIONS'])
        def send_wildcard_with_origin(request):
            return text('Welcome!')

        @self.app.route('/test_list', methods=['GET', 'HEAD', 'OPTIONS'])
        def test_list(request):
            return text('Welcome!')

        @self.app.route('/test_string', methods=['GET', 'HEAD', 'OPTIONS'])
        def test_string(request):
            return text('Welcome!')

        @self.app.route('/test_set', methods=['GET', 'HEAD', 'OPTIONS'])
        def test_set(request):
            return text('Welcome!')

        @self.app.route('/test_subdomain_regex', methods=['GET', 'HEAD', 'OPTIONS'])
        def test_set(request):
            return text('Welcome!')

        @self.app.route('/test_regex_list', methods=['GET', 'HEAD', 'OPTIONS'])
        def test_set(request):
            return text('Welcome!')

        @self.app.route('/test_regex_mixed_list', methods=['GET', 'HEAD', 'OPTIONS'])
        def test_set(request):
            return text('Welcome!')

        @self.app.route('/test_compiled_subdomain_regex', methods=['GET', 'HEAD', 'OPTIONS'])
        def test_set(request):
            return text('Welcome!')

    def test_defaults_no_origin(self):
        ''' If there is no Origin header in the request,
            by default the '*' should be sent
        '''
        for resp in self.iter_responses('/test_defaults'):
            self.assertEqual(resp.headers.get(ACL_ORIGIN), '*')

    def test_defaults_with_origin(self):
        ''' If there is an Origin header in the request, the
            Access-Control-Allow-Origin header should be included.
        '''
        for resp in self.iter_responses('/test_defaults', origin='http://example.com'):
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get(ACL_ORIGIN), 'http://example.com')

    def test_send_wildcard_with_origin(self):
        ''' If there is an Origin header in the request, the
            Access-Control-Allow-Origin header should be included.
        '''
        for resp in self.iter_responses('/test_send_wildcard_with_origin', origin='http://example.com'):
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get(ACL_ORIGIN), '*')

    def test_list_serialized(self):
        ''' If there is an Origin header in the request, the
            Access-Control-Allow-Origin header should be echoed.
        '''
        resp = self.get('/test_list', origin='http://bar.com')
        self.assertEqual(resp.headers.get(ACL_ORIGIN),'http://bar.com')

    def test_string_serialized(self):
        ''' If there is an Origin header in the request,
            the Access-Control-Allow-Origin header should be echoed back.
        '''
        resp = self.get('/test_string', origin='http://foo.com')
        self.assertEqual(resp.headers.get(ACL_ORIGIN), 'http://foo.com')

    def test_set_serialized(self):
        ''' If there is an Origin header in the request,
            the Access-Control-Allow-Origin header should be echoed back.
        '''
        resp = self.get('/test_set', origin='http://bar.com')

        allowed = resp.headers.get(ACL_ORIGIN)
        # Order is not garaunteed
        self.assertEqual(allowed, 'http://bar.com')

    def test_not_matching_origins(self):
        for resp in self.iter_responses('/test_list', origin="http://bazz.com"):
            self.assertFalse(ACL_ORIGIN in resp.headers)

    def test_subdomain_regex(self):
        for sub in letters:
            domain = "http://%s.example.com" % sub
            for resp in self.iter_responses('/test_subdomain_regex',
                                            headers={'origin': domain}):
                self.assertEqual(domain, resp.headers.get(ACL_ORIGIN))

    def test_compiled_subdomain_regex(self):
        for sub in [1, 100, 200]:
            domain = "http://example%s.com" % sub
            for resp in self.iter_responses('/test_compiled_subdomain_regex',
                                            headers={'origin': domain}):
                self.assertEqual(domain, resp.headers.get(ACL_ORIGIN))
        for resp in self.iter_responses('/test_compiled_subdomain_regex',
                                        headers={'origin': "http://examplea.com"}):
            self.assertEqual(None, resp.headers.get(ACL_ORIGIN))

    def test_regex_list(self):
        for parent in 'example.com', 'otherexample.com':
            for sub in letters:
                domain = "http://%s.%s.com" % (sub, parent)
                for resp in self.iter_responses('/test_regex_list',
                                                headers={'origin': domain}):
                    self.assertEqual(domain, resp.headers.get(ACL_ORIGIN))

    def test_regex_mixed_list(self):
        '''
            Tests  the corner case occurs when the send_always setting is True
            and no Origin header in the request, it is not possible to match
            the regular expression(s) to determine the correct
            Access-Control-Allow-Origin header to be returned. Instead, the
            list of origins is serialized, and any strings which seem like
            regular expressions (e.g. are not a '*' and contain either '*'
            or '?') will be skipped.

            Thus, the list of returned Access-Control-Allow-Origin header
            is garaunteed to be 'null', the origin or "*", as per the w3
            http://www.w3.org/TR/cors/#access-control-allow-origin-response-header

        '''
        for sub in letters:
            domain = "http://%s.otherexample.com" % sub
            for resp in self.iter_responses('/test_regex_mixed_list',
                                            origin=domain):
                self.assertEqual(domain, resp.headers.get(ACL_ORIGIN))

        self.assertEquals("http://example.com",
            self.get('/test_regex_mixed_list', origin='http://example.com').headers.get(ACL_ORIGIN))


class AppExtensionList(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)
        CORS(self.app, resources=[r'/test_exposed', r'/test_other_exposed'],
             origins=['http://foo.com', 'http://bar.com'])

        @self.app.route('/test_unexposed', methods=['GET', 'HEAD', 'OPTIONS'])
        def unexposed(request):
            return text('Not exposed over CORS!')

        @self.app.route('/test_exposed', methods=['GET', 'HEAD', 'OPTIONS'])
        def exposed1(request):
            return text('Welcome!')

        @self.app.route('/test_other_exposed', methods=['GET', 'HEAD', 'OPTIONS'])
        def exposed2(request):
            return text('Welcome!')

    def test_exposed(self):
        for resp in self.iter_responses('/test_exposed', origin='http://foo.com'):
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get(ACL_ORIGIN), 'http://foo.com')

    def test_other_exposed(self):
        for resp in self.iter_responses('/test_other_exposed', origin='http://bar.com'):
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get(ACL_ORIGIN), 'http://bar.com')

    def test_unexposed(self):
        for resp in self.iter_responses('/test_unexposed', origin='http://foo.com'):
            self.assertEqual(resp.status, 200)
            self.assertFalse(ACL_ORIGIN in resp.headers)


class AppExtensionString(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)
        CORS(self.app, resources=r'/api/*',
             headers='Content-Type',
             expose_headers='X-Total-Count',
             automatic_options=False,
             origins='http://bar.com')

        @self.app.route('/api/v1/foo', methods=['GET', 'HEAD', 'OPTIONS'])
        def exposed1(request):
            return json({"success": True})

        @self.app.route('/api/v1/bar', methods=['GET', 'HEAD', 'OPTIONS'])
        def exposed2(request):
            return json({"success": True})

        @self.app.route('/api/v1/special', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, origins='http://foo.com', automatic_options=True)
        def overridden(request):
            return json({"special": True})

        @self.app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
        def index(request):
            return text('Welcome')

    def test_exposed(self):
        for path in '/api/v1/foo', '/api/v1/bar':
            for resp in self.iter_responses(path, origin='http://bar.com'):
                self.assertEqual(resp.status, 200)
                self.assertEqual(resp.headers.get(ACL_ORIGIN), 'http://bar.com')
                self.assertEqual(resp.headers.get(ACL_EXPOSE_HEADERS),
                                 'X-Total-Count')
            for resp in self.iter_responses(path, origin='http://foo.com'):
                self.assertEqual(resp.status, 200)
                self.assertFalse(ACL_ORIGIN in resp.headers)
                self.assertFalse(ACL_EXPOSE_HEADERS in resp.headers)

    def test_unexposed(self):
        for resp in self.iter_responses('/', origin='http://bar.com'):
            self.assertEqual(resp.status, 200)
            self.assertFalse(ACL_ORIGIN in resp.headers)
            self.assertFalse(ACL_EXPOSE_HEADERS in resp.headers)

    def test_override(self):
        for resp in self.iter_responses('/api/v1/special', origin='http://foo.com'):
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get(ACL_ORIGIN), 'http://foo.com')

            self.assertFalse(ACL_EXPOSE_HEADERS in resp.headers)

        for resp in self.iter_responses('/api/v1/special', origin='http://bar.com'):
            self.assertEqual(resp.status, 200)
            self.assertFalse(ACL_ORIGIN in resp.headers)
            self.assertFalse(ACL_EXPOSE_HEADERS in resp.headers)


class AppExtensionError(SanicCorsTestCase):
    def test_value_error(self):
        try:
            app = Sanic(__name__)
            CORS(app, resources=5)
            self.assertTrue(False, "Should've raised a value error")
        except ValueError:
            pass


class AppExtensionDefault(SanicCorsTestCase):
    def test_default(self):
        '''
            By default match all.
        '''

        self.app = Sanic(__name__)
        CORS(self.app)

        @self.app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
        def index(request):
            return text('Welcome')

        for resp in self.iter_responses('/', origin='http://foo.com'):
            self.assertEqual(resp.status, 200)
            self.assertTrue(ACL_ORIGIN in resp.headers)


class AppExtensionExampleApp(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)
        CORS(self.app, resources={
            r'/api/*': {'origins': ['http://blah.com', 'http://foo.bar']}
        })

        @self.app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
        def index(request):
            return text('')

        @self.app.route('/api/foo', methods=['GET', 'HEAD', 'OPTIONS'])
        def test_wildcard(request):
            return text('')

        @self.app.route('/api/', methods=['GET', 'HEAD', 'OPTIONS'])
        def test_exact_match(request):
            return text('')

    def test_index(self):
        '''
            If regex does not match, do not set CORS
        '''
        for resp in self.iter_responses('/', origin='http://foo.bar'):
            self.assertFalse(ACL_ORIGIN in resp.headers)

    def test_wildcard(self):
        '''
            Match anything matching the path /api/* with an origin
            of 'http://blah.com' or 'http://foo.bar'
        '''
        for origin in ['http://foo.bar', 'http://blah.com']:
            for resp in self.iter_responses('/api/foo', origin=origin):
                self.assertTrue(ACL_ORIGIN in resp.headers)
                self.assertEqual(origin, resp.headers.get(ACL_ORIGIN))

    def test_exact_match(self):
        '''
            Match anything matching the path /api/* with an origin
            of 'http://blah.com' or 'http://foo.bar'
        '''
        for origin in ['http://foo.bar', 'http://blah.com']:
            for resp in self.iter_responses('/api/', origin=origin):
                self.assertTrue(ACL_ORIGIN in resp.headers)
                self.assertEqual(origin, resp.headers.get(ACL_ORIGIN))


class AppExtensionCompiledRegexp(SanicCorsTestCase):
    def test_compiled_regex(self):
        '''
            Ensure we do not error if the user specifies an compiled regular
            expression.
        '''
        import re
        self.app = Sanic(__name__)
        CORS(self.app, resources=re.compile('/api/.*'))

        @self.app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
        def index(request):
            return text('Welcome')

        @self.app.route('/api/v1', methods=['GET', 'HEAD', 'OPTIONS'])
        def example(request):
            return text('Welcome')

        for resp in self.iter_responses('/'):
            self.assertFalse(ACL_ORIGIN in resp.headers)

        for resp in self.iter_responses('/api/v1', origin='http://foo.com'):
            self.assertTrue(ACL_ORIGIN in resp.headers)


class AppExtensionBadRegexp(SanicCorsTestCase):
    def test_value_error(self):
        '''
            Ensure we do not error if the user specifies an bad regular
            expression.
        '''

        self.app = Sanic(__name__)
        CORS(self.app, resources="[")

        @self.app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
        def index(request):
            return text('Welcome')

        for resp in self.iter_responses('/'):
            self.assertEqual(resp.status, 200)


if __name__ == "__main__":
    unittest.main()
