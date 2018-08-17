#!/usr/local/bin/python3
import zlib
import gzip
import requests
from flask import Flask, request, make_response, abort


def _request(req):
    url = req.url
    headers = dict(req.headers)
    for k in ('Host', 'Content-Length',):
        if k in headers:
            del headers[k]
    if req.method == 'GET':
        return requests.get(url, headers=headers)
    elif req.method == 'POST':
        data = req.data
        return requests.post(url, data=data, headers=headers)


def _response(resp):
    rv = resp.content
    status = resp.status_code
    headers = dict(resp.headers)
    ce = headers.get('Content-Encoding')
    if ce == 'deflate':
        rv = zlib.compress(rv, -1)
    elif ce == 'gzip':
        rv = gzip.compress(rv)
    for k in ('Transfer-Encoding', 'Accept-Ranges',):
        if k in headers:
            del headers[k]
    headers['Content-Length'] = len(rv)
    return make_response((rv, status, headers,))


class Server(Flask):
    # 远程代理
    def remote(self, url):
        index = url.find('/', url.index('://') + 3)
        domain = url[:index] if index >= 0 else url
        path = url[index + 1:] if index >= 0 else ''

        def decorator(function):
            @self.route('/' + path, methods=['GET', 'POST', ])
            def wrapper():
                ret = function()
                if ret is not None:
                    return ret
                index = request.url.find('/', request.url.index('://') + 3)
                request.url = domain + (request.url[index:] if index >= 0 else '')
                return _response(_request(request))
            return wrapper
        return decorator
