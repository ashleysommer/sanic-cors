# Change Log

## 0.9.9.post4
This is the last version of sanic-cors to support Sanic 0.8.3
- Update to Sanic 18.12LTS (or higher) to use future Sanic-CORS releases

Bump Sanic-Plugins-Framework to 0.8.2.post1 to fix a big.
- This is also the last version of SPF to support Sanic 0.8.3

_**Note**_, Sanic v19.12.0 (and 19.12.2) _do not_ work with Sanic-CORS 0.9.9 series or earlier.
A new version coming out soon will work with sanic v19.12.

## 0.9.9.post3
Revert previous patch. Sorry @donjar

## 0.9.9.post2
Apply fix for async error handlers. Thanks @donjar

## 0.9.9.post1
Actually fix import of headers on latest Sanic versions

## 0.9.9
Fix import of headers on latest Sanic versions

## 0.9.8.post3
Bump minimum required Sanic-Plugins-Framework version to 0.8.2
 - This fixes compatibility with ASGI mode, as well as alternate server runners like gunicorn server runner.

## 0.9.8.post2
Bump minimum required Sanic-Plugins-Framework version to 0.8.1
 - This allows us to use the new entrypoints feature to advertise the sanic_cors plugin to SPF apps.
 - See app_config_example for an example of how this works

## 0.9.8.post1
Fix an issue where engineio websockets library can return a response of [], and Sanic will pass that onto response-middlewares.
- We now just check for resp truthiness, so if a resp is None, or False, or [] or any other Falsy value, then we skip applying middleware.

## 0.9.8
Bump minimum required Sanic-Plugins-Framework version to 0.7.0
 - There were some recent important bugs fixed in SPF, so we want to specify a new min SPF version.

## 0.9.7
Changes to allow pickling of the Sanic-CORS Plugin on a Sanic App
 - This is to allow Multiprocessing via `workers=` on Windows
Bump minimum required Sanic-Plugins-Framework version to 0.6.4.dev20181101
 - This release includes similar pickling fixes in order to solve Windows multiprocessing issues in Sanic-Plugins-Framework 


## 0.9.6
Minimum supported sanic is now 0.7.0 (removes legacy support)
Automatic-Options route now sets EVALUATED flag to prevent the response middleware from running again.
Fixed a bug in `response.headers.add()` function all.
Updated all (c)2017 text to (c)2018 (very late, I know)

## 0.9.5
Finally a new Sanic is released on PyPI.
Bump min sanic to v0.8.1
Bump sanic-plugins-framework to latest
Use CIMultiDict from Sanic by default, rather than CIDict
Fix a test which broke after the CIDict change

## 0.9.4
TODO: Fill in

## 0.9.3
TODO: Fill in

## 0.9.2
On Sanic 0.6.0, some exceptions can be thrown _after_ a request has finished. In this case, the request context has been destroyed and cannot be accessed. Added a fix for those scenarios.

## 0.9.1
Bumped to new version of SPF, to handle tracking multiple Request contexts at once.

## 0.9.0
Ported Sanic-CORS to use Sanic-Plugins-Framework!

This is a big change. Some major architectural changes needed to occur.

All tests pass, so hopefully there's no fallout in any user facing way.

No longer tracking SANIC version numbers, we are doing our own versioning now.

## 0.6.0.2
Bug fixes, see git commits

## 0.6.0.1
Bug fixes, see git commits

## 0.6.0.0
Update to Sanic 0.6.0

## 0.5.0.0
Update to Sanic 0.5.x

## 0.4.1
Update to Sanic 0.4.1

## 0.1.0
Initial release of Sanic-Cors, ported to Sanic from Flask-Cors v3.0.2

# Flask-Cors Change Log

## 3.0.2
Fixes Issue #187: regression whereby header (and domain) matching was incorrectly case sensitive. Now it is not, making the behavior identical to 2.X and 1.X.

## 3.0.1
Fixes Issue #183: regression whereby regular expressions for origins with an "?" are not properly matched.

## 3.0.0

This release is largely a number of small bug fixes and improvements, along with a default change in behavior, which is technically a breaking change.

**Breaking Change**
We added an always_send option, enabled by default, which makes Sanic-CORS inject headers even if the request did not have an 'Origin' header. Because this makes debugging far easier, and has very little downside, it has also been set as the default, making it technically a breaking change. If this actually broke something for you, please let me know, and I'll help you work around it. (#156) c7a1ecdad375a796155da6aca6a1f750337175f3


Other improvements:
* Adds building of universal wheels (#175) 4674c3d54260f8897bd18e5502509363dcd0d0da
* Makes Sanic-CORS compatible with OAuthLib's custom header class ... (#172) aaaf904845997a3b684bc6677bdfc91656a85a04
* Fixes incorrect substring matches when strings are used as origins or headers (#165) 9cd3f295bd6b0ba87cc5f2afaca01b91ff43e72c
* Fixes logging when unknown options are supplied (#152) bddb13ca6636c5d559ec67a95309c9607a3fcaba


## 2.1.3
Fixes Vary:Origin header sending behavior when regex origins are used.


## 2.1.2
Fixes package installation. Requirements.txt was not included in Manifest.


## 2.1.1
Stop dynamically referecing logger.

Disable internal logging by default and reduce logging verbosity

## 2.1.0
Adds support for Flask Blueprints.

## 2.0.1
Fixes Issue #124 where only the first of multiple headers with the same name would be passed through.

## 2.0.0
**New Defaults**

1. New defaults allow all origins, all headers.

**Breaking Changes**

1. Removed always_send option.
1. Removed 'headers' option as a backwards-compatible alias for 'allowed_headers' to reduce confusion.

## 2.0.0rc1
Would love to get some feedback to make sure there are no unexpected regressions. This should be backwards compatible for most people.

Update default options and parameters in a backwards incompatible way.

By default, all headers are now allowed, and only requests with an
Origin header have CORS headers returned. If an Origin header is not
present, no CORS headers are returned.

Removed the following options: always_send, headers.

Extension and decorator are now in separate modules sharing a core module.
Test have been moved into the respective tests.extension and tests.decorator
modules. More work to decompose these tests is needed.


## 1.10.3
Release Version 1.10.3
* Adds logging to Sanic-Cors so it is easy to see what is going on and why
* Adds support for compiled regexes as origins

Big thanks to @michalbachowski and @digitizdat!

## 1.10.2
This release fixes the behavior of Access-Control-Allow-Headers and Access-Control-Expose-Headers, which was previously swapped since 1.9.0.

To further fix the confusion, the `headers` parameter was renamed to more explicitly be `allow_headers`.

Thanks @maximium for the bug report and implementation!

## 1.10.1
This is a bug fix release, fixing:
Incorrect handling of resources and intercept_exceptions App Config options https://github.com/wcdolphin/sanic-cors/issues/84
Issue with functools.partial in 1.10.0 using Python 2.7.9 https://github.com/wcdolphin/sanic-cors/issues/83

Shoutout to @diiq and @joonathan for reporting these issues!

## 1.10.0
* Adds support for returning CORS headers with uncaught exceptions in production so 500s will have expected CORS headers set. This will allow clients to better surface the errors, rather than failing due to security. Reported and tested by @robertfw -- thanks!
* Improved conformance of preflight request handling to W3C spec.
* Code simplification and 100% test coverage :sunglasses:

## 1.9.0
* Improves API consistency, allowing a CORS resource of '*'
* Improves documentation of the CORS app extension
* Fixes test import errors on Python 3.4.1 (Thanks @wking )

## 1.8.1
Thanks to @wking's work in PR https://github.com/wcdolphin/sanic-cors/pull/71 `python setup.py test` will now work.


## v1.8.0
Adds support for regular expressions in the list of origins.

This allows subdomain wildcarding and should be fully backwards compatible.

Credit to @marcoqu for opening https://github.com/wcdolphin/sanic-cors/issues/54 which inspired this work

## Earlier
Prior version numbers were not kept track of in this system.
