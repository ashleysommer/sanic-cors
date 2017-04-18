"""
Sanic-Cors example
===================
This is a tiny Sanic Application demonstrating Sanic-Cors, making it simple
to add cross origin support to your sanic app!

:copyright: (c) 2017 by Ashley Sommer (based on flask-cors by Cory Dolphin).
:license: MIT/X11, see LICENSE for more details.
"""
from sanic import Sanic
from sanic.response import json, text
from sanic.exceptions import ServerError
import logging
try:
    from sanic_cors import CORS  # The typical way to import sanic-cors
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)
    from sanic_cors import CORS


app = Sanic('SanicCorsAppBasedExample')
logging.basicConfig(level=logging.INFO)

# To enable logging for sanic-cors,
logging.getLogger('sanic_cors').level = logging.DEBUG

# One of the simplest configurations. Exposes all resources matching /api/* to
# CORS and allows the Content-Type header, which is necessary to POST JSON
# cross origin.
CORS(app, resources=r'/api/*')


@app.route("/")
def hello_world(request):
    '''
        Since the path '/' does not match the regular expression r'/api/*',
        this route does not have CORS headers set.
    '''
    return text('''
<html>
    <h1>Hello CORS!</h1>
    <h3> End to end editable example with jquery! </h3>
    <a class="jsbin-embed" href="http://jsbin.com/zazitas/embed?js,console">JS Bin on jsbin.com</a>
    <script src="//static.jsbin.com/js/embed.min.js?3.35.12"></script>

</html>
''')

@app.route("/api/v1/users/", methods=['GET', 'OPTIONS'])
def list_users(request):
    '''
        Since the path matches the regular expression r'/api/*', this resource
        automatically has CORS headers set. The expected result is as follows:

        $ curl --include -X GET http://127.0.0.1:5000/api/v1/users/ \
            --header Origin:www.examplesite.com
        HTTP/1.0 200 OK
        Access-Control-Allow-Headers: Content-Type
        Access-Control-Allow-Origin: *
        Content-Length: 21
        Content-Type: application/json
        Date: Sat, 09 Aug 2014 00:26:41 GMT
        Server: Werkzeug/0.9.4 Python/2.7.8

        {
            "success": true
        }

    '''
    return json({"user": "joe"})


@app.route("/api/v1/users/create", methods=['POST', 'OPTIONS'])
def create_user(request):
    '''
        Since the path matches the regular expression r'/api/*', this resource
        automatically has CORS headers set.

        Browsers will first make a preflight request to verify that the resource
        allows cross-origin POSTs with a JSON Content-Type, which can be simulated
        as:
        $ curl --include -X OPTIONS http://127.0.0.1:5000/api/v1/users/create \
            --header Access-Control-Request-Method:POST \
            --header Access-Control-Request-Headers:Content-Type \
            --header Origin:www.examplesite.com
        >> HTTP/1.0 200 OK
        Content-Type: text/html; charset=utf-8
        Allow: POST, OPTIONS
        Access-Control-Allow-Origin: *
        Access-Control-Allow-Headers: Content-Type
        Access-Control-Allow-Methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
        Content-Length: 0
        Server: Werkzeug/0.9.6 Python/2.7.9
        Date: Sat, 31 Jan 2015 22:25:22 GMT


        $ curl --include -X POST http://127.0.0.1:5000/api/v1/users/create \
            --header Content-Type:application/json \
            --header Origin:www.examplesite.com


        >> HTTP/1.0 200 OK
        Content-Type: application/json
        Content-Length: 21
        Access-Control-Allow-Origin: *
        Server: Werkzeug/0.9.6 Python/2.7.9
        Date: Sat, 31 Jan 2015 22:25:04 GMT

        {
          "success": true
        }

    '''
    return json({"success": True})

@app.route("/api/exception")
def get_exception(request):
    '''
        Since the path matches the regular expression r'/api/*', this resource
        automatically has CORS headers set.

        Browsers will first make a preflight request to verify that the resource
        allows cross-origin POSTs with a JSON Content-Type, which can be simulated
        as:
        $ curl --include -X OPTIONS http://127.0.0.1:5000/exception \
            --header Access-Control-Request-Method:POST \
            --header Access-Control-Request-Headers:Content-Type \
            --header Origin:www.examplesite.com
        >> HTTP/1.0 200 OK
        Content-Type: text/html; charset=utf-8
        Allow: POST, OPTIONS
        Access-Control-Allow-Origin: *
        Access-Control-Allow-Headers: Content-Type
        Access-Control-Allow-Methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
        Content-Length: 0
        Server: Werkzeug/0.9.6 Python/2.7.9
        Date: Sat, 31 Jan 2015 22:25:22 GMT
    '''
    raise Exception("example")

@app.exception(ServerError)
def server_error(req, e):
    logging.exception('An error occurred during a request. %s', e)
    return text("An internal error occured", status=500)


if __name__ == "__main__":
    app.run(debug=True)
