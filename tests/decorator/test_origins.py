# -*- coding: utf-8 -*-
"""
    test
    ~~~~
    Sanic-CORS is a simple extension to Sanic allowing you to support cross
    origin resource sharing (CORS) using a simple decorator.

    :copyright: (c) 2020 by Ashley Sommer (based on flask-cors by Cory Dolphin).
    :license: MIT, see LICENSE for more details.
"""

from ..base_test import SanicCorsTestCase
from sanic import Sanic
from sanic.response import text
import re
from sanic_cors import *
from sanic_cors.core import *

letters = 'abcdefghijklmnopqrstuvwxyz'  # string.letters is not PY3 compatible

class OriginsTestCase(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__.replace(".","-"))

        @self.app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app)
        def wildcard(request):
            return text('Welcome!')

        @self.app.route('/test_always_send')
        @cross_origin(self.app, always_send=True)
        def test_always_send(request):
            return text('Welcome!')

        @self.app.route('/test_always_send_no_wildcard')
        @cross_origin(self.app, always_send=True, send_wildcard=False)
        def test_always_send_no_wildcard(request):
            return text('Welcome!')

        @self.app.route('/test_send_wildcard_with_origin', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, send_wildcard=True)
        def test_send_wildcard_with_origin(request):
            return text('Welcome!')

        @self.app.route('/test_list')
        @cross_origin(self.app, origins=["http://foo.com", "http://bar.com"])
        def test_list(request):
            return text('Welcome!')

        @self.app.route('/test_string')
        @cross_origin(self.app, origins="http://foo.com")
        def test_string(request):
            return text('Welcome!')

        @self.app.route('/test_set')
        @cross_origin(self.app, origins=set(["http://foo.com", "http://bar.com"]))
        def test_set(request):
            return text('Welcome!')

        @self.app.route('/test_subdomain_regex', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, origins=r"http?://\w*\.?example\.com:?\d*/?.*")
        def test_subdomain_regex(request):
            return text('')

        @self.app.route('/test_compiled_subdomain_regex', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, origins=re.compile(r"http?://\w*\.?example\.com:?\d*/?.*"))
        def test_compiled_subdomain_regex(request):
            return text('')

        @self.app.route('/test_regex_list', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, origins=[r".*.example.com", r".*.otherexample.com"])
        def test_regex_list(request):
            return text('')

        @self.app.route('/test_regex_mixed_list', methods=['GET', 'HEAD', 'OPTIONS'])
        @cross_origin(self.app, origins=["http://example.com", r".*.otherexample.com"])
        def test_regex_mixed_list(request):
            return text('')

        @self.app.route('/test_multiple_protocols')
        @cross_origin(self.app, origins="https?://example.com")
        def test_multiple_protocols(request):
            return text('')

    def test_defaults_no_origin(self):
        ''' If there is no Origin header in the request, the
            Access-Control-Allow-Origin header should be '*' by default.
        '''
        for resp in self.iter_responses('/'):
            self.assertEqual(resp.headers.get(ACL_ORIGIN), '*')

    def test_defaults_with_origin(self):
        ''' If there is an Origin header in the request, the
            Access-Control-Allow-Origin header should be included.
        '''
        for resp in self.iter_responses('/', origin='http://example.com'):
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get(ACL_ORIGIN), 'http://example.com')

    def test_always_send_no_wildcard(self):
        '''
            If send_wildcard=False, but the there is '*' in the
            allowed origins, we should send it anyways.
        '''
        for resp in self.iter_responses('/'):
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get(ACL_ORIGIN), '*')

    def test_always_send_no_wildcard_origins(self):
        for resp in self.iter_responses('/'):
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get(ACL_ORIGIN), '*')


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
        self.assertEqual(resp.headers.get(ACL_ORIGIN), 'http://bar.com')

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
        for sub in letters:
            domain = "http://%s.example.com" % sub
            for resp in self.iter_responses('/test_compiled_subdomain_regex',
                                            headers={'origin': domain}):
                self.assertEqual(domain, resp.headers.get(ACL_ORIGIN))

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

        self.assertEqual("http://example.com",
            self.get('/test_regex_mixed_list', origin='http://example.com').headers.get(ACL_ORIGIN))

    def test_multiple_protocols(self):
        import logging
        logging.getLogger('sanic_cors').level = logging.DEBUG
        resp = self.get('/test_multiple_protocols', origin='https://example.com')
        self.assertEqual('https://example.com', resp.headers.get(ACL_ORIGIN))


if __name__ == "__main__":
    unittest.main()
