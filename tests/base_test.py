# -*- coding: utf-8 -*-
"""
    test
    ~~~~
    Sanic-CORS is a simple extension to Sanic allowing you to support cross
    origin resource sharing (CORS) using a simple decorator.

    :copyright: (c) 2017 by Ashley Sommer (based on flask-cors by Cory Dolphin).
    :license: MIT, see LICENSE for more details.
"""
from sanic import Sanic
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from sanic_cors.core import *


class SanicCorsTestCase(unittest.TestCase):

    def shortDescription(self):
        """
        Get's the one liner description to be displayed.
        Source:
        http://erikzaadi.com/2012/09/13/inheritance-within-python-unit-tests/
        """
        doc = self.id()[self.id().rfind('.')+1:]
        return "%s.%s" % (self.__class__.__name__, doc)

    def iter_verbs(self, c):
        ''' A simple helper method to iterate through a range of
            HTTP Verbs and return the test_client bound instance,
            keeping writing our tests as DRY as possible.
        '''
        for verb in ['get', 'head', 'options']:
            yield getattr(c, verb)

    def iter_responses(self, path, verbs=['get', 'head', 'options'], **kwargs):
        for verb in verbs:
            yield self._request(verb.lower(), path, **kwargs)

    def _request(self, verb, path, *args, **kwargs):
        _origin = kwargs.pop('origin', None)
        headers = kwargs.pop('headers', {})
        if _origin:
            headers.update(Origin=_origin)
        #if not str(path).startswith("http") and not str(path).startswith("/"):
        #    path = ''.join(['/', path])

        try:
            c = self.test_client
        except AttributeError:
            c = self.test_client = self.app.test_client
        request, response = getattr(c, verb)(uri=path, debug=True, headers=headers, *args, **kwargs)
        return response

    def get(self, *args, **kwargs):
        return self._request('get', *args, **kwargs)

    def head(self, *args, **kwargs):
        return self._request('head', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request('post', *args, **kwargs)

    def options(self, *args, **kwargs):
        return self._request('options', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._request('put', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._request('patch', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request('delete', *args, **kwargs)

    def preflight(self, path, method='GET', cors_request_headers=None, json=True, **kwargs):
        kwargs['headers'] = kwargs.get('headers', {})

        if cors_request_headers:
            kwargs['headers'].update({'Access-Control-Request-Headers': ', '.join(cors_request_headers)})
        if json:
            kwargs['headers'].update({'Content-Type':'application/json'})

        kwargs['headers'].update({'Access-Control-Request-Method': method})

        return self.options(path, **kwargs)

    def assertHasACLOrigin(self, resp, origin=None):
        if origin is None:
            self.assertTrue(ACL_ORIGIN in resp.headers)
        else:
            self.assertTrue(resp.headers.get(ACL_ORIGIN) == origin)
