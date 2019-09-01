#!/usr/local/bin/python3
import os
import json
import asyncio
from aiohttp import web
from .gdbws import onopen, onmessage, onclose
VUE_DIST = os.path.dirname(__file__) + '/gui/dist'
app = web.Application()
app.router.add_static('/static', VUE_DIST + '/static')


async def index(request):
    return web.FileResponse(VUE_DIST + '/index.html')
app.router.add_get('/', index)


async def websocket(request):
    token = request.cookies.get('token')
    response = web.WebSocketResponse()
    await response.prepare(request)
    emit = lambda data: asyncio.ensure_future(response.send_json(data))
    onopen(token, emit)
    try:
        async for msg in response:
            onmessage(token, emit, json.loads(msg.data))
    finally:
        onclose(token, emit)
    return response
app.router.add_get('/ws', websocket)


web.run_app(app)
