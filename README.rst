Sanic-CORS
==========

|Build Status| |Latest Version| |Supported Python versions|
|License|

A Sanic extension for handling Cross Origin Resource Sharing (CORS),
making cross-origin AJAX possible. Based on
`flask-cors <https://github.com/corydolphin/flask-cors>`__ by Cory Dolphin.

This package has a simple philosophy, when you want to enable CORS, you
wish to enable it for all use cases on a domain. This means no mucking
around with different allowed headers, methods, etc. By default,
submission of cookies across domains is disabled due to the security
implications, please see the documentation for how to enable
credential'ed requests, and please make sure you add some sort of
`CSRF <http://en.wikipedia.org/wiki/Cross-site_request_forgery>`__
protection before doing so!

**December 2021 Notice:**
If you need compatibility with Sanic v21.12+, upgrade to Sanic-CORS v2.0

**Sept 2021 Notice:**
Please upgrade to Sanic-CORS v1.0.1 if you need compatibility with Sanic v21.9,<21.12

**Older Notice:**
Please upgrade to Sanic-CORS v1.0.0 if you need compatibility with Sanic v21.3+ (and don't forget to replace SPF with SPTK)
Please upgrade to Sanic-CORS v0.10.0 if you need compatibility with Sanic v19.12+. See `here <https://github.com/huge-success/sanic/issues/1749#issuecomment-571881532>`_ for more details.

Installation
------------

Install the extension with using pip, or easy\_install.

.. code:: bash

    $ pip install -U sanic-cors

Usage
-----

This package exposes a Sanic extension which by default enables CORS support on
all routes, for all origins and methods. It allows parameterization of all
CORS headers on a per-resource level. The package also contains a decorator,
for those who prefer this approach.

Simple Usage
~~~~~~~~~~~~

In the simplest case, initialize the Sanic-Cors extension with default
arguments in order to allow CORS for all domains on all routes.

.. code:: python

    from sanic import Sanic
    from sanic.response import text
    from sanic_cors import CORS, cross_origin

    app = Sanic(__name__)
    CORS(app)

    @app.route("/", methods=['GET', 'OPTIONS'])
    def hello_world(request):
      return text("Hello, cross-origin-world!")

Resource specific CORS
^^^^^^^^^^^^^^^^^^^^^^

Alternatively, you can specify CORS options on a resource and origin
level of granularity by passing a dictionary as the `resources` option,
mapping paths to a set of options.

.. code:: python

    app = Sanic(__name__)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route("/api/v1/users", methods=['GET', 'OPTIONS'])
    def list_users(request):
      return text("user example")

Route specific CORS via decorator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This extension also exposes a simple decorator to decorate sanic routes
with. Simply add ``@cross_origin(app)`` below a call to Sanic's
``@app.route(..)`` to allow CORS on a given route.

.. code:: python

    @app.route("/", methods=['GET', 'OPTIONS'])
    @cross_origin(app)
    def hello_world(request):
      return text("Hello, cross-origin-world!")

Sanic-Ext Usage
~~~~~~~~~~~~~~~

Sanic-CORS can use Sanic-Ext to load the plugin for you.
(But you need to make sure to disable the built-in sanic-ext CORS support too)

.. code:: python

    from sanic import Sanic
    from sanic.response import text
    from sanic_ext import Extend
    from sanic_cors.extension import CORS
    app = Sanic(__name__)
    CORS_OPTIONS = {"resources": r'/*', "origins": "*", "methods": ["GET", "POST", "HEAD", "OPTIONS"]}
    # Disable sanic-ext built-in CORS, and add the Sanic-CORS plugin
    Extend(app, extensions=[CORS], config={"CORS": False, "CORS_OPTIONS": CORS_OPTIONS})

    @app.route("/", methods=['GET', 'OPTIONS'])
    def hello_world(request):
      return text("Hello, cross-origin-world!")


Documentation
-------------

For a full list of options, please see the flask-cors
`documentation <http://flask-cors.corydolphin.com/en/latest/api.html#extension>`__.

Preflight Requests
------------------
CORS requests have to send `pre-flight requests <https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS#Preflighted_requests_in_CORS>`_
via the options method, Sanic by default only allows the ``GET`` method, in order to
service your CORS requests you must specify ``OPTIONS`` in the methods argument to
your routes decorator.

Sanic-CORS includes an ``automatic_options`` configuration parameter to
allow the plugin handle the ``OPTIONS`` response automatically for you. This is enabled by default, but you
can turn it off if you wish to do your own ``OPTIONS`` response.

.. code:: python

    CORS(app, automatic_options=True)

    @app.delete('/api/auth')
    @auth.login_required
    async def auth_logout(request):
    auth.logout_user(request)
        return json(None, status=OK)

or with the app config key:

.. code:: python

    app = Sanic(__name__)
    app.config['CORS_AUTOMATIC_OPTIONS'] = True

    CORS(app)

    @app.delete('/api/auth')
    @auth.login_required
    async def auth_logout(request):
        auth.logout_user(request)
        return json(None, status=OK)

or directly on the route with the ``cross_origin`` decorator:

.. code:: python

    @app.route('/api/auth', methods={'DELETE','OPTIONS'})
    @auth.login_required
    @cross_origin(app, automatic_options=True)
    async def auth_logout(request):
        auth.logout_user(request)
        return json(None, status=OK)

Note: For the third example, you must use ``@route()``, rather than
``@delete()`` because you need to enable both ``DELETE`` and ``OPTIONS`` to
work on that route, even though the decorator is handling the ``OPTIONS``
response.

Tests
-----

A simple set of tests is included in ``test/``. To run, install nose,
and simply invoke ``nosetests`` or ``python setup.py test`` to exercise
the tests.

Contributing
------------

Questions, comments or improvements? Please create an issue on
`Github <https://github.com/ashleysommer/sanic-cors>`__. I do my best to
include every contribution proposed in any way that I can.

Credits
-------

This Sanic extension is based upon the `Decorator for the HTTP Access
Control <http://flask.pocoo.org/snippets/56/>`__ written by Armin
Ronacher.

.. |Build Status| image:: https://api.travis-ci.org/ashleysommer/sanic-cors.svg?branch=master
   :target: https://travis-ci.org/ashleysommer/sanic-cors
.. |Latest Version| image:: https://img.shields.io/pypi/v/Sanic-Cors.svg
   :target: https://pypi.python.org/pypi/Sanic-Cors/
.. |Supported Python versions| image:: https://img.shields.io/pypi/pyversions/Sanic-Cors.svg
   :target: https://img.shields.io/pypi/pyversions/Sanic-Cors.svg
.. |License| image:: http://img.shields.io/:license-mit-blue.svg
   :target: https://pypi.python.org/pypi/Sanic-Cors/
