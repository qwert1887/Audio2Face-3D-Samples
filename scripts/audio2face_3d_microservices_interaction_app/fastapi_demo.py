# -*- coding: utf-8 -*-            
# @Author : Dony YUAN
# @Time : 2025/1/4 12:20
import os.path
import sys

sys.path.insert(0, "../../")
print(sys.path)
from typing import Union, Optional
import threading
import uvicorn
from fastapi import FastAPI, Form, File, UploadFile, Body, Request
# import requests
from timeit import default_timer as timer
import httpx
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from scripts.audio2face_3d_microservices_interaction_app.a2f_3d_utlis import mian_wrapper, main
from scripts.audio2face_3d_microservices_interaction_app.convert_bs_demo import normalize_bs, convert_bs_demo


headers = {
    "accept": "*/*",
    # "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "cookie": "fvlid=1735559536251Ea2sabj3Ckfd; Hm_lvt_d381ec2f88158113b9b76f14c497ed48=1735559536; HMACCOUNT=16729F317A92F5D6; sessionid=abcf9285-8070-4a39-86b9-3c8f9fb41419; sessionip=183.251.19.24; area=350206; che_sessionid=6E90EEF6-D8CA-4AAB-8BA5-9A0DA477462B%7C%7C2024-12-30+19%3A52%3A16.585%7C%7C0; v_no=38; visit_info_ad=6E90EEF6-D8CA-4AAB-8BA5-9A0DA477462B||42EE6CAC-8EBD-4799-847F-558CA08658F3||-1||-1||38; che_ref=0%7C0%7C0%7C0%7C2024-12-31+08%3A50%3A00.175%7C2024-12-30+19%3A52%3A16.585; listuserarea=0; KEY_LOCATION_CITY_GEO_DATE=202511; sessionvisit=60f89a41-11c2-4247-9924-2564f02de0fe; sessionvisitInfo=abcf9285-8070-4a39-86b9-3c8f9fb41419|www.che168.com|0; UC_KEY_LOCATION_CITY_GEO=%7B%22pid%22:810000,%22pname%22:%22%E9%A6%99%E6%B8%AF%22,%22cid%22:810100,%22cname%22:%22%E9%A6%99%E6%B8%AF%22,%22locationLongitude%22:0,%22locationLatitude%22:22.3193039%7D; userarea=0; Hm_lpvt_d381ec2f88158113b9b76f14c497ed48=1735723421; showNum=25; ahpvno=47; ahuuid=6E10C22A-76E0-405F-8910-2B2805F2FC58; sessionuid=abcf9285-8070-4a39-86b9-3c8f9fb41419",
    "dnt": "1",
    "pragma": "no-cache",
    "origin":"https://m.che168.com",
    "priority":"u=1, i",
    "referer":"https://m.che168.com/",
    "sec-ch-ua": "'Google Chrome';v='131', 'Chromium';v='131', 'Not_A Brand';v='24'",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "'Windows'",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}


class AudioIn(BaseModel):
    audio_url: str


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://192.168.1.107:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = timer()
    print(f"请求路径: {request.url.path}")
    response = await call_next(request)
    print(f"请求结束: {timer() - start_time}")
    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/audio/bs")
async def audio_bs(
        audio_in: AudioIn,
):
    try:
        # print(sessionid)
        # sessionid = 0 if not sessionid else int(sessionid)
        audio_url = audio_in.audio_url
        print(audio_url)
        # audio_url = "https://api.guaishouai.com/uploads/audio/434e16ff4b24cf4b8bd4bbb6f92581fb.mp3"
        # audio_url = "http://127.0.0.1:8008/"
        filename = os.path.basename(audio_url)  # 注意后缀 以及samples 16KHz
        # strip_name, name_fmt = filename.split(".")
        strip_name, name_fmt = filename, "wav"
        # if name_fmt != fmt:
        #     filename += f".{fmt}"
        # filebytes = await file.read()
        # # print(client_id)
        # print(client_id, filename)
        # print("=======")
        audio_stream = httpx.get(audio_url).content
        # print("=======22")
        # print(audio_stream)

        # print(filebytes)
        audio_local_path = os.path.join("static" , filename)
        with open(audio_local_path, "wb") as f:
            f.write(audio_stream)
            # cfg.nerfreals[sessionid].put_audio_file(filebytes)
        await main(audio_local_path, "config/config_james.yml", "0.0.0.0:52000")
        # th = threading.Thread(target=mian_wrapper, args=(audio_local_path, "config/config_james.yml", "0.0.0.0:52000"))
        # th.start()
        # th.join()
        bs_json_path = os.path.join("output_bs" , f"{strip_name}.json")
        # bs_data = normalize_bs(bs_json_path)
        bs_data, _ = convert_bs_demo(bs_json_path)
        # print(bs_data)
        # bs_data = []
        # return StreamingResponse(generate_json_stream(answer="你好，这是测试！！！", question="这是语音识别内容"), media_type="text/event-stream")
        return JSONResponse(
            {"code": 0, "msg":"success", "data": bs_data}
        )
    except Exception as e:
        return JSONResponse(
            {"code": -1, "msg": "error", "data": e}
        )

@app.post("/uploadfile/sounds")
async def uploadfile(
        client_id: Optional[str] = Form("monster_client"),
        # files: List[UploadFile] = File(...),
        file: UploadFile = File(...)
):
    try:
        # print(sessionid)
        # sessionid = 0 if not sessionid else int(sessionid)
        filename=file.filename
        content_type = file.content_type
        print(content_type)
        fmt = content_type.split("/")[1]
        if fmt == "wave":
            fmt = "wav"
        elif fmt == "octet-stream":
            fmt = "wav"  # 默认wav
        # elif fmt == "jpeg":
        #     fmt = "jpg"
        else:
            return JSONResponse({"code": -1, "msg":"error", "data": f"file format {fmt} not supported"})
        strip_name, name_fmt = filename.split(".")
        if name_fmt != fmt:
            filename += f".{fmt}"
        filebytes = await file.read()
        # print(client_id)
        print(client_id, filename)
        # print(filebytes)
        audio_local_path = os.path.join("static" , filename)
        with open(audio_local_path, "wb") as f:
            f.write(filebytes)
            # cfg.nerfreals[sessionid].put_audio_file(filebytes)
        th = threading.Thread(target=mian_wrapper, args=(audio_local_path, "config/config_james.yml", "0.0.0.0:52000"))
        th.start()
        th.join()
        bs_json_path = os.path.join("output_bs" , f"{strip_name}.json")
        bs_data = normalize_bs(bs_json_path)
        # return StreamingResponse(generate_json_stream(answer="你好，这是测试！！！", question="这是语音识别内容"), media_type="text/event-stream")
        return JSONResponse(
            {"code": 0, "msg":"success", "data": bs_data}
        )
    except Exception as e:
        return JSONResponse(
            {"code": -1, "msg": "error", "data": "" + e.args[0] + ""}
        )



if __name__ == '__main__':
    # 运行fastapi程序
    uvicorn.run(app="fastapi_demo:app", host="0.0.0.0", port=8008, reload=True)
