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


async def assist_device():
    r = []
    for line in os.popen('adb devices').read().split('\n'):
        if not line.endswith('device'):
            continue
        r.append('adb://' + line.split('\t')[0])
    r.sort()
    return r


async def assist_process(device):
    r = []
    if '://' in device:
        scheme, serial, = device.split('://', 1)
        if scheme == 'adb':
            for line in os.popen(f'adb -s {serial} shell ps').read().split('\n'):
                if not line.startswith('u0_a'):
                    continue
                r.append(line.split(' ')[-1])
    r.sort()
    return r


async def assist_script(script):
    r = []
    try:
        driname = os.path.dirname(script) or '/'
        if os.path.isabs(driname):
            for filename in os.listdir(driname):
                if filename.startswith('.'):
                    continue
                filepath = os.path.join(driname, filename)
                if os.path.isdir(filepath):
                    filepath += '/'
                r.append(filepath)
    except OSError:
        pass
    return r


def assist_filter(a, v):
    return filter(lambda i: i.startswith(v) and i != v, a)


async def assist(request):
    _assist = []
    _type = request.query['type']
    _value = request.query['value']
    if _type == 'device':
        _assist.extend(assist_filter(await assist_device(), _value))
    elif _type == 'process':
        _device, = json.loads(request.query['context'])
        _assist.extend(assist_filter(await assist_process(_device), _value))
    elif _type == 'script':
        _assist.extend(assist_filter(await assist_script(_value), _value))
    return web.json_response(_assist, headers={
        'Access-Control-Allow-Origin': '*'
    })
app.router.add_get('/assist', assist)


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


web.run_app(app, port=8519)
