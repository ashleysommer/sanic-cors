# -*- coding: utf-8 -*-
"""
    extension
    ~~~~
    Sanic-CORS is a simple extension to Sanic allowing you to support cross
    origin resource sharing (CORS) using a simple decorator.

    :copyright: (c) 2017 by Ashley Sommer (based on flask-cors by Cory Dolphin).
    :license: MIT, see LICENSE for more details.
"""
from functools import update_wrapper, partial
from inspect import isawaitable

import sanic
from sanic import exceptions, response
from spf import SanicPlugin
from .core import *
from distutils.version import LooseVersion
import logging


SANIC_VERSION = LooseVersion(sanic.__version__)
SANIC_0_4_1 = LooseVersion("0.4.1")


class CORS(SanicPlugin):
    __slots__ = tuple()
    """
    Initializes Cross Origin Resource sharing for the application. The
    arguments are identical to :py:func:`cross_origin`, with the addition of a
    `resources` parameter. The resources parameter defines a series of regular
    expressions for resource paths to match and optionally, the associated
    options to be applied to the particular resource. These options are
    identical to the arguments to :py:func:`cross_origin`.

    The settings for CORS are determined in the following order

    1. Resource level settings (e.g when passed as a dictionary)
    2. Keyword argument settings
    3. App level configuration settings (e.g. CORS_*)
    4. Default settings

    Note: as it is possible for multiple regular expressions to match a
    resource path, the regular expressions are first sorted by length,
    from longest to shortest, in order to attempt to match the most
    specific regular expression. This allows the definition of a
    number of specific resource options, with a wildcard fallback
    for all other resources.

    :param resources:
        The series of regular expression and (optionally) associated CORS
        options to be applied to the given resource path.

        If the argument is a dictionary, it's keys must be regular expressions,
        and the values must be a dictionary of kwargs, identical to the kwargs
        of this function.

        If the argument is a list, it is expected to be a list of regular
        expressions, for which the app-wide configured options are applied.

        If the argument is a string, it is expected to be a regular expression
        for which the app-wide configured options are applied.

        Default : Match all and apply app-level configuration

    :type resources: dict, iterable or string

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
    """

    def __init__(self, *args, **kwargs):
        super(CORS, self).__init__(*args, **kwargs)


    def on_before_registered(self, context, *args, **kwargs):
        context._options = kwargs
        if not CORS.on_before_registered.has_run:
            debug = partial(context.log, logging.DEBUG)
            _ = _make_cors_request_middleware_function(self, debug)
            _ = _make_cors_response_middleware_function(self, debug)
            CORS.on_before_registered.has_run = True

    on_before_registered.has_run = False


    def on_registered(self, context, *args, **kwargs):
        # this will need to be called more than once, for every app it is registered on.
        self.init_app(context, *args, **kwargs)


    def init_app(self, context, *args, **kwargs):
        app = context.app
        log = context.log
        _options = context._options
        debug = partial(log, logging.DEBUG)
        # The resources and options may be specified in the App Config, the CORS constructor
        # or the kwargs to the call to init_app.
        options = get_cors_options(app, _options, kwargs)

        # Flatten our resources into a list of the form
        # (pattern_or_regexp, dictionary_of_options)
        resources = parse_resources(options.get('resources'))

        # Compute the options for each resource by combining the options from
        # the app's configuration, the constructor, the kwargs to init_app, and
        # finally the options specified in the resources dictionary.
        resources = [
            (pattern, get_cors_options(app, options, opts))
            for (pattern, opts) in resources
        ]
        context.options = options
        context.resources = resources
        # Create a human readable form of these resources by converting the compiled
        # regular expressions into strings.
        resources_human = dict([(get_regexp_pattern(pattern), opts) for (pattern, opts) in resources])
        debug("Configuring CORS with resources: {}".format(resources_human))
        try:
            assert app.error_handler

            def _exception_response_wrapper(ctx, f):
                # wrap app's original exception response function
                # so that error responses have proper CORS headers
                def wrapper(ctx, req, e):
                    opts = ctx.options
                    # get response from the original handler
                    resp = f(req, e)
                    # SanicExceptions are equiv to Flask Aborts, always apply CORS to them.
                    if (req is not None and resp is not None) and \
                            (isinstance(e, exceptions.SanicException) or opts.get('intercept_exceptions', True)):
                        try:
                            try:
                                path = req.path
                            except AttributeError:
                                path = req.url
                            if path is not None:
                                for res_regex, res_options in resources:
                                    if try_match(path, res_regex):
                                        debug("Request to '{:s}' matches CORS resource '{}'. "
                                              "Using options: {}".format(
                                              path, get_regexp_pattern(res_regex), res_options))
                                        set_cors_headers(req, resp, ctx, res_options)
                                        break
                                else:
                                    debug('No CORS rule matches')
                            else:
                                pass
                        except AttributeError:
                            # not sure why certain exceptions doesn't has
                            # an accompanying request
                            pass
                    if req is not None and SANIC_0_4_1 < SANIC_VERSION:
                        # On Sanic > 0.4.1, these exceptions have normal CORS middleware applied automatically.
                        # So set a flag to skip our manual application of the middleware.
                        try:
                            request_context = ctx.request[id(req)]
                            request_context[SANIC_CORS_SKIP_RESPONSE_MIDDLEWARE] = "1"
                        except AttributeError:
                            debug("Cannot find the request context. Is request already finished?")
                    return resp

                return update_wrapper(partial(update_wrapper(wrapper, f), ctx), f)

            app.error_handler.response = _exception_response_wrapper(context, app.error_handler.response)
        except (AttributeError, AssertionError):
            # Blueprints have no error_handler. Just skip error_handler initialisation
            pass

    async def route_wrapper(self, route, req, context, request_args, request_kw,
                            *decorator_args, **decorator_kw):
        _ = decorator_kw.pop('with_context')  # ignore this.
        _options = decorator_kw
        options = get_cors_options(context.app, _options)
        if options.get('automatic_options') and req.method == 'OPTIONS':
            resp = response.HTTPResponse()
        else:
            resp = route(req, *request_args, **request_kw)
            if resp is not None:
                while isawaitable(resp):
                    resp = await resp
        if resp is not None:
            request_context = context.request[id(req)]
            set_cors_headers(req, resp, context, options)
            request_context[SANIC_CORS_EVALUATED] = "1"
        return resp


def _make_cors_request_middleware_function(plugin, debug):
    @plugin.middleware(relative="pre", attach_to='request', with_context=True)
    def cors_request_middleware(req, context):
        if req.method == 'OPTIONS':
            try:
                path = req.path
            except AttributeError:
                path = req.url
            resources = context.resources
            for res_regex, res_options in resources:
                if res_options.get('automatic_options') and try_match(path, res_regex):
                    debug("Request to '{:s}' matches CORS resource '{}'. "
                          "Using options: {}".format(
                           path, get_regexp_pattern(res_regex), res_options))
                    resp = response.HTTPResponse()
                    set_cors_headers(req, resp, context, res_options)
                    return resp
            else:
                debug('No CORS rule matches')
    return cors_request_middleware


def _make_cors_response_middleware_function(plugin, debug):
    @plugin.middleware(relative="post", attach_to='response', with_context=True)
    async def cors_response_middleware(req, resp, context):
        try:
            request_context = context.request[id(req)]
        except AttributeError:
            debug("Cannot find the request context. Is request already finished?")
            return False
        # `resp` can be None in the case of using Websockets
        if resp is None:
            return False
        if SANIC_0_4_1 < SANIC_VERSION and request_context.get(SANIC_CORS_SKIP_RESPONSE_MIDDLEWARE):
            debug('CORS was handled in the exception handler, skipping')
            # On Sanic > 0.4.1, an exception might already have CORS middleware run on it.
            return False

        # If CORS headers are set in a view decorator, pass
        elif request_context.get(SANIC_CORS_EVALUATED):
            debug('CORS have been already evaluated, skipping')
            return False

        try:
            path = req.path
        except AttributeError:
            path = req.url

        resources = context.resources
        for res_regex, res_options in resources:
            if try_match(path, res_regex):
                debug("Request to '{}' matches CORS resource '{:s}'. Using options: {}".format(
                      path, get_regexp_pattern(res_regex), res_options))
                set_cors_headers(req, resp, context, res_options)
                break
        else:
            debug('No CORS rule matches')
    return cors_response_middleware


instance = cors = CORS()
__all__ = ["cors", "CORS"]
