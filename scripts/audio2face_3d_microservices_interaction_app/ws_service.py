# -*- coding: utf-8 -*-            
# @Author : Dony YUAN
# @Time : 2025/1/4 10:20
import json
import asyncio
from websockets import serve

"""
{
    "type": "initComplete",
    "data": {
        "visitId": "28709048b2df754b0e720bfcf3146460"
    }
}
"""


"""
{
    "type": "voiceChatgpt",
    "data": {
        "humanText": "你好",
        "timbre": "zh-CN-XiaozhenNeural"
    }
}
"""
"""
{
    "code": 200,
    "data": {
        "text": "stop",
        "index": 1,
        "question": "你好"
    },
    "message": "终止动作"
}
"""
"""
resp.json
"""

"""
{
    "type": "ping"
}
"""

async def echo(websocket):
    print(f"websocket: {id(websocket)}")
    async for message in websocket:
        try:
            msg_dict = json.loads(message)
            msg_type = msg_dict.get("type")
            if msg_type == "initComplete":
                visit_id = msg_dict.get("data").get("visitId")
                print(f"visit_id: {visit_id}")
            elif msg_type == "voiceChatgpt":
                question = msg_dict.get("data").get("humanText")
                timbre = msg_dict.get("data").get("timbre")
                print(question, timbre)
                resp_data = {
                    "code": 200,
                    "data": {
                        "text": "stop",
                        "index": 1,
                        "question": question
                    },
                    "message": "终止动作"
                }
                await websocket.send(json.dumps(resp_data, ensure_ascii=False))
                # send blendshape
                with open("test_v2.json", "r") as f:
                    # resp = json.load(f)
                    await websocket.send(f.read())
            elif msg_type == "ping":
                await websocket.send("pong")
        except:
            print(f"数据格式错误!-{message}")
            pass
        # await websocket.send(message)

async def main():
    host = "0.0.0.0"
    port = 8765
    async with serve(echo, host, port):
        print(f"running on ws://{host}:{port}")
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
