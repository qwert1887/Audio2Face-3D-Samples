# -*- coding: utf-8 -*-            
# @Author : Dony YUAN
# @Time : 2025/1/4 12:20
import os.path
from typing import Union, Optional
import threading
import uvicorn
from fastapi import FastAPI, Form, File, UploadFile
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from scripts.audio2face_3d_microservices_interaction_app.a2f_3d_utlis import mian_wrapper
from scripts.audio2face_3d_microservices_interaction_app.convert_bs_demo import normalize_bs

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

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


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
