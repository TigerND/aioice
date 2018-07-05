#!/usr/bin/env python

import argparse
import asyncio
import json
import logging

import aioice
import websockets

STUN_SERVER=('stun.vlj.lt', 3478)
TURN_SERVER=(('turn.vlj.lt', 3478), 'admin', 'admin')
#WEBSOCKET_URI = 'ws://127.0.0.1:8765'
WEBSOCKET_URI='ws://213.136.70.68:8765'

def dump_candidates(connection):
    print ('>>> CANDIDATES <<<')
    for cc in connection.local_candidates:
        print (cc)
    print ('>>> CANDIDATES <<<')

async def offer(options):
    connection = aioice.Connection(ice_controlling=True,
                                   components=options.components,
                                   stun_server=STUN_SERVER,
                                   turn_server=TURN_SERVER[0],
                                   turn_username=TURN_SERVER[1],
                                   turn_password=TURN_SERVER[2],
                                   use_ipv4=True,
                                   use_ipv6=False)
    await connection.gather_candidates()

    dump_candidates(connection)

    websocket = await websockets.connect(WEBSOCKET_URI)

    # send offer
    await websocket.send(json.dumps({
        'candidates': [c.to_sdp() for c in connection.local_candidates],
        'password': connection.local_password,
        'username': connection.local_username,
    }))

    # await answer
    message = json.loads(await websocket.recv())
    print('received answer', message)
    connection.remote_candidates = ([aioice.Candidate.from_sdp(c) for c in message['candidates']])
    connection.remote_username = message['username']
    connection.remote_password = message['password']

    await websocket.close()

    await connection.connect()
    print('connected')

    # send data
    data = b'hello'
    component = 1
    print('sending %s on component %d' % (repr(data), component))
    await connection.sendto(data, component)
    data, component = await connection.recvfrom()
    print('received %s on component %d' % (repr(data), component))

    await asyncio.sleep(5)
    await connection.close()


async def answer(options):
    connection = aioice.Connection(ice_controlling=False,
                                   components=options.components,
                                   stun_server=STUN_SERVER,
                                   turn_server=TURN_SERVER[0],
                                   turn_username=TURN_SERVER[1],
                                   turn_password=TURN_SERVER[2],
                                   use_ipv4=True,
                                   use_ipv6=False)
    await connection.gather_candidates()

    dump_candidates(connection)

    websocket = await websockets.connect(WEBSOCKET_URI)

    # await offer
    message = json.loads(await websocket.recv())
    print('received offer', message)
    connection.remote_candidates = [aioice.Candidate.from_sdp(c) for c in message['candidates']]
    connection.remote_username = message['username']
    connection.remote_password = message['password']

    # send answer
    await websocket.send(json.dumps({
        'candidates': [c.to_sdp() for c in connection.local_candidates],
        'password': connection.local_password,
        'username': connection.local_username,
    }))

    await websocket.close()

    await connection.connect()
    print('connected')

    # echo data back
    data, component = await connection.recvfrom()
    print('echoing %s on component %d' % (repr(data), component))
    await connection.sendto(data, component)

    await asyncio.sleep(5)
    await connection.close()


parser = argparse.ArgumentParser(description='ICE tester')
parser.add_argument('action', choices=['offer', 'answer'])
parser.add_argument('--components', type=int, default=1)
options = parser.parse_args()

logging.basicConfig(level=logging.DEBUG)

if options.action == 'offer':
    asyncio.get_event_loop().run_until_complete(offer(options))
else:
    asyncio.get_event_loop().run_until_complete(answer(options))
