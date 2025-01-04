# -*- coding: utf-8 -*-            
# @Author : Dony YUAN
# @Time : 2025/1/4 19:06
import asyncio

import websockets


async def echo(websocket):
    async for message in websocket:
        message = "I got your message: {}".format(message)
        await websocket.send(message)

async def main():
    async with websockets.serve(echo, "localhost", 8766):
        # await asyncio.Future()  # 与下面的语句等价
        await asyncio.get_event_loop().create_future()

# asyncio.get_event_loop().run_until_complete(websockets.serve(echo, 'localhost', 8766))
# asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    asyncio.run(main())