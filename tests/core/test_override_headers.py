# -*- coding: utf-8 -*-
"""
    test
    ~~~~

    Sanic-Cors tests module
"""

from ..base_test import SanicCorsTestCase
#from sanic import Sanic, Response
from sanic import Sanic
from sanic.response import HTTPResponse

from sanic_cors import *
from sanic_cors.core import *

class ResponseHeadersOverrideTestCaseIntegration(SanicCorsTestCase):
    def setUp(self):
        self.app = Sanic(__name__)
        CORS(self.app)

        @self.app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
        def index(request):
            return HTTPResponse(body='Welcome', headers={"custom": "dictionary"})


    def test_override_headers(self):
        '''
            Ensure we work even if response.headers is set to something other than a MultiDict.
        '''
        for resp in self.iter_responses('/'):
            self.assertTrue(ACL_ORIGIN in resp.headers)

if __name__ == "__main__":
    unittest.main()
