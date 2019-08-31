#!/usr/local/bin/python3
import os
import json
import asyncio
from aiohttp import web
from .gdbws import onopen, onmessage, onclose
app = web.Application()
app.router.add_static('/static', os.path.dirname(__file__) + '/static')


def add_get(path):
    def decorator(afunc):
        app.router.add_get(path, afunc)
        return afunc
    return decorator


def add_post(path):
    def decorator(afunc):
        app.router.add_post(path, afunc)
        return afunc
    return decorator


@add_get('/')
async def redirect(request):
    return web.HTTPFound('/static/index.html')


@add_get('/ws')
async def websocket(request):
    token = request.cookies.get('token')
    response = web.WebSocketResponse()
    await response.prepare(request)
    emit = lambda data: asyncio.ensure_future(response.send_json(data))
    onopen(token, emit)
    try:
        async for msg in websocket:
            onmessage(token, emit, json.loads(msg.data))
    finally:
        onclose(token, emit)
    return response


web.run_app(app)
