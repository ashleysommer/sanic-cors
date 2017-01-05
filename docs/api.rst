API Docs
==========

This package exposes a Sanic extension which by default enables CORS support on all routes, for all origins and methods. It allows parameterization of all CORS headers on a per-resource level. The package also contains a decorator, for those who prefer this approach.

Extension
~~~~~~~~~

This is the suggested approach to enabling CORS. The default configuration
will work well for most use cases.

.. autoclass:: sanic_cors.CORS

Decorator
~~~~~~~~~

If the `CORS` extension does not satisfy your needs, you may find the
decorator useful. It shares options with the extension, and should be simple
to use.

.. autofunction:: sanic_cors.cross_origin


Using `CORS` with cookies
~~~~~~~~~~~~~~~~~~~~~~~~~

By default, Sanic-CORS does not allow cookies to be submitted across sites,
since it has potential security implications. If you wish to enable cross-site
cookies, you may wish to add some sort of
`CSRF <http://en.wikipedia.org/wiki/Cross-site_request_forgery>`__
protection to keep you and your users safe.

To allow cookies or authenticated requests to be made
cross origins, simply set the `supports_credentials` option to `True`. E.G.

.. code:: python


    from sanic import Sanic, session
    from sanic.response import text
    from sanic_cors import CORS

    app = Sanic(__name__)
    CORS(app, supports_credentials=True)

    @app.route("/")
    def hello_world(request):
      return text("Hello, %s" % session['username'])

Using `CORS` with Blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sanic-CORS supports blueprints out of the box. Simply pass a `blueprint`
instance to the CORS extension, and everything will just work.

.. literalinclude:: ../examples/blueprints_based_example.py
  :language: python
  :lines: 23-


Examples
~~~~~~~~~

Using the `CORS` extension
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../examples/app_based_example.py
   :language: python
   :lines: 29-


Using the `cross_origins` decorator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../examples/view_based_example.py
   :language: python
   :lines: 27-
