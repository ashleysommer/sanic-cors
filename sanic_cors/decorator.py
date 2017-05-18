# -*- coding: utf-8 -*-
"""
    decorator
    ~~~~
    This unit exposes a single decorator which should be used to wrap a
    Sanic route with. It accepts all parameters and options as
    the CORS extension.

    :copyright: (c) 2017 by Ashley Sommer (based on flask-cors by Cory Dolphin).
    :license: MIT, see LICENSE for more details.
"""
import asyncio
from functools import update_wrapper
from .core import *

LOG = logging.getLogger(__name__)


def cross_origin(app, *args, **kwargs):
    """
    This function is the decorator which is used to wrap a Sanic route with.
    In the simplest case, simply use the default parameters to allow all
    origins in what is the most permissive configuration. If this method
    modifies state or performs authentication which may be brute-forced, you
    should add some degree of protection, such as Cross Site Forgery
    Request protection.

    :param origins:
        The origin, or list of origins to allow requests from.
        The origin(s) may be regular expressions, case-sensitive strings,
        or else an asterisk

        Default : '*'
    :type origins: list, string or regex

    :param methods:
        The method or list of methods which the allowed origins are allowed to
        access for non-simple requests.

        Default : [GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE]
    :type methods: list or string

    :param expose_headers:
        The header or list which are safe to expose to the API of a CORS API
        specification.

        Default : None
    :type expose_headers: list or string

    :param allow_headers:
        The header or list of header field names which can be used when this
        resource is accessed by allowed origins. The header(s) may be regular
        expressions, case-sensitive strings, or else an asterisk.

        Default : '*', allow all headers
    :type allow_headers: list, string or regex

    :param supports_credentials:
        Allows users to make authenticated requests. If true, injects the
        `Access-Control-Allow-Credentials` header in responses. This allows
        cookies and credentials to be submitted across domains.

        :note: This option cannot be used in conjuction with a '*' origin

        Default : False
    :type supports_credentials: bool

    :param max_age:
        The maximum time for which this CORS request maybe cached. This value
        is set as the `Access-Control-Max-Age` header.

        Default : None
    :type max_age: timedelta, integer, string or None

    :param send_wildcard: If True, and the origins parameter is `*`, a wildcard
        `Access-Control-Allow-Origin` header is sent, rather than the
        request's `Origin` header.

        Default : False
    :type send_wildcard: bool

    :param vary_header:
        If True, the header Vary: Origin will be returned as per the W3
        implementation guidelines.

        Setting this header when the `Access-Control-Allow-Origin` is
        dynamically generated (e.g. when there is more than one allowed
        origin, and an Origin than '*' is returned) informs CDNs and other
        caches that the CORS headers are dynamic, and cannot be cached.

        If False, the Vary header will never be injected or altered.

        Default : True
    :type vary_header: bool

    :param automatic_options:
        Only applies to the `cross_origin` decorator. If True, Sanic-CORS will
        override Sanic's default OPTIONS handling to return CORS headers for
        OPTIONS requests.

        Default : True
    :type automatic_options: bool

    """
    _options = kwargs

    def decorator(f):
        nonlocal _options
        LOG.debug("Enabling %s for cross_origin using options:%s", f, _options)

        # Sanic does not have the same automatic OPTIONS handling that Flask does,
        # and Sanic does not allow other middleware to alter the allowed methods on a route
        # So this decorator cannot work the same as it does in Flask-CORS.
        #
        # # If True, intercept OPTIONS requests by modifying the view function,
        # # replicating Sanic's default behavior, and wrapping the response with
        # # CORS headers.
        # #
        # # If f.provide_automatic_options is unset or True, Sanic's route
        # # decorator (which is actually wraps the function object we return)
        # # intercepts OPTIONS handling, and requests will not have CORS headers
        # if _options.get('automatic_options', True):
        #     f.required_methods = getattr(f, 'required_methods', set())
        #     f.required_methods.add('OPTIONS')
        #     f.provide_automatic_options = False

        async def wrapped_function(req, *args, **kwargs):
            nonlocal _options
            # Handle setting of Sanic-Cors parameters
            options = get_cors_options(app, _options)

            if options.get('automatic_options') and req.method == 'OPTIONS':
                resp = response.HTTPResponse()
            else:
                resp = f(req, *args, **kwargs)
                while asyncio.iscoroutine(resp):
                    resp = await resp

            set_cors_headers(req, resp, options)
            req.headers[SANIC_CORS_EVALUATED] = "1"
            return resp

        return update_wrapper(wrapped_function, f)
    return decorator
