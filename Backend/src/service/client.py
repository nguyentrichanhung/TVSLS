#!/usr/bin/env python

# WS client example

import asyncio
import websockets
name = 'Test'
async def hello(n):
    uri = "ws://localhost:8888"
    async with websockets.connect(uri) as websocket:
        # name = input("What's your name? ")

        await websocket.send(n)
        print(f"> {n}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello(name))