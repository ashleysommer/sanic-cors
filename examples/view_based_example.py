"""
Sanic-Cors example
===================
This is a tiny Sanic Application demonstrating Sanic-Cors, making it simple
to add cross origin support to your sanic app!

:copyright: (c) 2017 by Ashley Sommer (based on flask-cors by Cory Dolphin).
:license:   MIT/X11, see LICENSE for more details.
"""
from sanic import Sanic
from sanic.response import json, text
import logging
try:
    # The typical way to import sanic-cors
    from sanic_cors import cross_origin
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)

    from sanic_cors import cross_origin


app = Sanic('SanicCorsViewBasedExample')
logging.basicConfig(level=logging.INFO)


@app.route("/", methods=['GET', 'OPTIONS'])
@cross_origin(app)
def hello_world(request):
    '''
        This view has CORS enabled for all domains, representing the simplest
        configuration of view-based decoration. The expected result is as
        follows:

        $ curl --include -X GET http://127.0.0.1:5000/ \
            --header Origin:www.examplesite.com

        >> HTTP/1.0 200 OK
        Content-Type: text/html; charset=utf-8
        Content-Length: 184
        Access-Control-Allow-Origin: *
        Server: Werkzeug/0.9.6 Python/2.7.9
        Date: Sat, 31 Jan 2015 22:29:56 GMT

        <h1>Hello CORS!</h1> Read about my spec at the
        <a href="http://www.w3.org/TR/cors/">W3</a> Or, checkout my documentation
        on <a href="https://github.com/ashleysommer/sanic-cors">Github</a>

    '''
    return text('''<h1>Hello CORS!</h1> Read about my spec at the
<a href="http://www.w3.org/TR/cors/">W3</a> Or, checkout my documentation
on <a href="https://github.com/ashleysommer/sanic-cors">Github</a>''')


@app.route("/api/v1/users/create", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(app, allow_headers=['Content-Type'])
def cross_origin_json_post(request):
    '''
        This view has CORS enabled for all domains, and allows browsers
        to send the Content-Type header, allowing cross domain AJAX POST
        requests.

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

    return json({"success":True})

if __name__ == "__main__":
    app.run(debug=True)
