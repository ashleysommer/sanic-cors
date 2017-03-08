# -*- coding: utf-8 -*-
"""
    sanic_cors
    ~~~~
    Sanic-CORS is a simple extension to Sanic allowing you to support cross
    origin resource sharing (CORS) using a simple decorator.

    :copyright: (c) 2017 by Ashley Sommer (based on flask-cors by Cory Dolphin).
    :license: MIT, see LICENSE for more details.
"""
from .decorator import cross_origin
from .extension import CORS
from .version import __version__

__all__ = ['CORS', 'cross_origin']

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# Set initial level to WARN. Users must manually enable logging for
# sanic_cors to see our logging.
rootlogger = logging.getLogger(__name__)
rootlogger.addHandler(NullHandler())

if rootlogger.level == logging.NOTSET:
    rootlogger.setLevel(logging.WARN)
