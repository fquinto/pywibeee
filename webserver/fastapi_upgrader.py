#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AUTHOR    | DATE       | VERSION | COMMENTS
# F.Quinto  | 2020-11-05 | 0.0.0   | First draft
# F.Quinto  | 2021-06-28 | 0.0.1   | Improve login
# F.Quinto  | 2021-07-01 | 0.0.2   | New functions
# F.Quinto  | 2021-07-12 | 0.0.3   | Clean files and get ersions
# F.Quinto  | 2021-07-14 | 0.0.4   | Files download
# F.Quinto  | 2021-07-15 | 0.0.5   | First release?


"""FastAPI using upgrader."""

# fastapi_upgrader.py
# pip install python-multipart
# uvicorn fastapi_upgrader:app
# uvicorn fastapi_upgrader:app --reload

# pip install fastapi uvicorn pyjwt --upgrade
# pip freeze > requirements.txt
# pip install -r requirements.txt


__version__ = "0.0.5"


from fastapi import (
    FastAPI, Form, Request, File, UploadFile,
    WebSocket, HTTPException, Security, Depends, Response, status)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

from starlette.responses import RedirectResponse, Response, JSONResponse

from pydantic import BaseModel
from typing import List, Tuple, Optional, Any
import random
import uvicorn
import shutil
# from upgrader import Upgrader

# from auth import Auth
# from plc import PLC
# from localFunctions import localFunctions
import json
import logging
import logging.config
import logging.handlers
logger = logging.getLogger("easyVIEW")


# DEVELOPMENT
app = FastAPI()
# PRODUCTION
# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# mount static folder to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 template instance for returning webpage via template engine
templates = Jinja2Templates(directory="templates")


# auth_handler = Auth()
security = HTTPBearer()
# plc = PLC()
# lf = localFunctions()


# Pydantic data model class
class Item(BaseModel):
    # language: str
    language = 'english'


# Pydantic data model class
class AuthModel(BaseModel):
    username: str
    password: str


# test_session = SessionCookie(
#     name="session",
#     secret_key="helloworld",
#     backend=InMemoryBackend(),
#     data_model=AuthModel,
#     scheme_name="Test Cookies",
#     auto_error=False
# )


class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)


manager = ConnectionManager()


def checkLoginUser(request=None):
    response = None
    # res = auth_handler.decode_save_token()
    messageval = res['detail']
    if not res['username']:
        # auth_handler.delete_token()
        if request:
            response = templates.TemplateResponse(
                "login.html",
                {"request": request,
                 "message": messageval}
            )
        else:
            response = RedirectResponse(
                url="/",
                status_code=status.HTTP_303_SEE_OTHER)
    return response


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_text()
        await manager.broadcast(f"Client {client_id}: {data}")


@app.post("/updatepackage")
async def updatepackage(pkg: UploadFile = File(...)):
    aux = checkLoginUser()
    if aux:
        return aux
    a = pkg.filename
    b = a[-4:len(a)]  # .zip
    c = a[:len(a)-4]
    if b == '.zip' and pkg.content_type == 'application/zip':
        with open(pkg.filename, "wb") as buffer:
            shutil.copyfileobj(pkg.file, buffer)
        # r = lf.processFile(a)
        result = json.loads(r)
        return {"filename": pkg.filename, "status": result['message']}
    elif b == '.ZIP' and pkg.content_type == 'application/zip':
        return {"filename": pkg.filename,
                "status": f'Please rename {a} to {c}.zip and try again!'}
    else:
        return {"filename": pkg.filename, "status": 'Error'}


# Upload multiple files:
# https://levelup.gitconnected.com/how-to-save-uploaded-files-in-fastapi-90786851f1d3
# https://fastapi.tiangolo.com/tutorial/request-forms-and-files/

# /home/fquinto/TRABAJO/subversion/isp/trunk/middleware_os/upgrader/real_python.png
# curl -X POST -F 'image=@./real_python.png' http://127.0.0.1:8000/image

# http://127.0.0.1:8000/
# hello world, GET method, return string


# http://127.0.0.1:8000/random-number
# random number, GET method, return string
# @app.get('/random-number', response_class=PlainTextResponse)
# async def random_number():
#     return str(random.randrange(100))


# http://127.0.0.1:8000/alpha?text=hola
# check isAlpha, GET method, query parameter, return JSON
# @app.get('/alpha')
# async def alpha(text: str):
#     result = {'text': text, 'is_alpha': text.isalpha()}
#     return result


# # create new user, POST method, form fields, return JSON
# @app.post('/create-user')
# async def create_user(id: str = Form(...), name: str = Form(...)):
#     # code for authentication, validation, update database
#     data = {'id': id, 'name': name}
#     result = {'status_code': '0', 'status_message': 'Success', 'data': data}
#     return result


# Input FORM data
@app.post('/auth')
# async def auth_user(username: str = Form(...), password: str = Form(...)):
async def auth_user(request: Request):
    da = await request.form()
    da = jsonable_encoder(da)
    password = da['password']
    username = da['username']
    # c = plc.canLogin(password)
    # if c:
    #     auth_handler.encode_save_token(username)
    # else:
    #     auth_handler.delete_token()
    result = RedirectResponse(
        url="/main",
        status_code=status.HTTP_303_SEE_OTHER)
    return result


@app.get("/logout")
async def route_logout_and_remove_token():
    response = RedirectResponse(url="/")
    # auth_handler.delete_token()
    return response


# update language, PUT method, JSON input, return string
@app.put('/update-language', response_class=PlainTextResponse)
async def update_language(item: Item):
    language = item.language
    return "Successfully updated language to %s" % (language)


# http://127.0.0.1:8000/
# serve webpage, GET method, return HTML
@app.get('/main', response_class=HTMLResponse)
async def get_mainwebpage(request: Request):
    # res = auth_handler.decode_save_token()
    messageval = res['detail']
    dispmsg = ('' != messageval) and (messageval is not None)
    typmsg = 'secondary'
    if res['username']:
        nombre = res['username']
        # lf.set_nombre(nombre)
        # r = lf.findFilesAssets()
        files_in_assets = json.loads(r)
        response = templates.TemplateResponse(
            "index.html",
            {"request": request,
             "message": messageval,
             "dispmsg": dispmsg,
             "typmsg": typmsg,
             "nombre": nombre,
             "files_in_assets": files_in_assets,
             "version": __version__}
        )
    else:
        # auth_handler.delete_token()
        response = templates.TemplateResponse(
            "login.html",
            {"request": request,
             "message": messageval}
        )
    return response


# serve webpage, GET method, return HTML
@app.get('/', response_class=HTMLResponse)
async def get_loginwebpage(request: Request):
    # res = auth_handler.decode_save_token()
    if res['username']:
        response = RedirectResponse(
            url="/main",
            status_code=status.HTTP_303_SEE_OTHER)
    else:
        response = templates.TemplateResponse(
            "login.html",
            {"request": request,
             "message": ''}
        )
    return response


@app.get('/chat', response_class=HTMLResponse)
async def get_chat(request: Request):
    return templates.TemplateResponse("client.html", {"request": request})


# file response, GET method, return file as attachment
@app.get('/get-language-file/{language}')
async def get_language_file(language: str):
    file_name = "%s.json" % (language)
    file_path = "./static/language/" + file_name
    return FileResponse(
        path=file_path,
        headers={
            "Content-Disposition": "attachment;"
            f"filename={file_name}"
        }
    )


@app.get('/getevlogs')
async def getevlogs(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    tipo = 'ev'
    # r = lf.getlogsLocal(tipo)
    result = json.loads(r)
    if result['rc'] != 0:
        men = result['message']
        # nombre = lf.get_nombre()
        typmsg = 'danger'
        return templates.TemplateResponse(
            "index.html",
            {"request": request,
             "message": men,
             "dispmsg": True,
             "typmsg": typmsg,
             "nombre": nombre,
             "version": __version__}
        )
    else:
        file_path = result['ruta']
        fichero = result['fichero']
        return FileResponse(
            path=file_path,
            headers={
                "Content-Disposition": "attachment;"
                f"filename={fichero}"
            }
        )


@app.get('/getoslogs')
async def getoslogs(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    tipo = 'os'
    # r = lf.getlogsLocal(tipo)
    result = json.loads(r)
    if result['rc'] != 0:
        men = result['message']
        # nombre = lf.get_nombre()
        typmsg = 'danger'
        return templates.TemplateResponse(
            "index.html",
            {"request": request,
             "message": men,
             "dispmsg": True,
             "typmsg": typmsg,
             "nombre": nombre,
             "version": __version__}
        )
    else:
        file_path = result['ruta']
        fichero = result['fichero']
        return FileResponse(
            path=file_path,
            headers={
                "Content-Disposition": "attachment;"
                f"filename={fichero}"
            }
        )


@app.post("/getevdata", response_class=HTMLResponse)
async def getevdata(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    da = await request.form()
    da = jsonable_encoder(da)
    sn = da['sn']
    # r = lf.getevdata(sn)
    result = json.loads(r)
    if result['rc'] != 0:
        men = result['message']
        # nombre = lf.get_nombre()
        typmsg = 'danger'
        return templates.TemplateResponse(
            "index.html",
            {"request": request,
             "message": men,
             "dispmsg": True,
             "typmsg": typmsg,
             "nombre": nombre,
             "version": __version__}
        )
    else:
        file_path = result['ruta']
        fichero = result['fichero']
        return FileResponse(
            path=file_path,
            headers={
                "Content-Disposition": "attachment;"
                f"filename={fichero}"
            }
        )


@app.post("/setevversion", response_class=HTMLResponse)
async def setevversion(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    da = await request.form()
    da = jsonable_encoder(da)
    version = da['version']
    # r = lf.set_version(version)
    result = json.loads(r)
    if result['rc'] != 0:
        men = result['message']
        typmsg = 'danger'
    else:
        ver = result['version']
        rev = result['revision']
        men = f'ver:{ver} rev:{rev}'
        typmsg = 'success'
    # nombre = lf.get_nombre()
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
            "message": men,
            "dispmsg": True,
            "typmsg": typmsg,
            "nombre": nombre,
            "version": __version__}
    )


# @app.get("/deploy", response_class=PlainTextResponse)
@app.get("/deploy", response_class=HTMLResponse)
async def deploy(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    # messageval = lf.deployFunction()
    # nombre = lf.get_nombre()
    typmsg = 'secondary'
    return templates.TemplateResponse(
       "index.html",
       {"request": request,
        "message": messageval,
        "dispmsg": True,
        "typmsg": typmsg,
        "nombre": nombre,
        "version": __version__}
    )


@app.get('/getdb')
async def getdb(request: Request):
    aux = checkLoginUser()
    if aux:
        return aux
    # r = lf.getDBLocal()
    result = json.loads(r)
    if result['rc'] != 0:
        men = result['message']
        # nombre = lf.get_nombre()
        typmsg = 'danger'
        return templates.TemplateResponse(
            "index.html",
            {"request": request,
             "message": men,
             "dispmsg": True,
             "typmsg": typmsg,
             "nombre": nombre,
             "version": __version__}
        )
    else:
        file_path = result['ruta']
        fichero = result['fichero']
        return FileResponse(
            path=file_path,
            headers={
                "Content-Disposition": "attachment;"
                f"filename={fichero}"
            }
        )


@app.get('/getVersionFromDB')
async def getVersionFromDB(request: Request):
    aux = checkLoginUser()
    if aux:
        return aux
    # r = lf.getVersionFromDB()
    result = json.loads(r)
    if result['rc'] != 0:
        men = result['message']
        typmsg = 'danger'
    else:
        ver = result['version']
        rev = result['revision']
        men = f'ver:{ver} rev:{rev}'
        typmsg = 'info'
    dispmsg = ('' != men) and (men is not None)
    # nombre = lf.get_nombre()
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": men,
         "dispmsg": dispmsg,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get("/getVersionFromCurrent", response_class=HTMLResponse)
async def getVersionFromCurrent(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    # r = lf.getVersionFromCurrent()
    result = json.loads(r)
    if result['rc'] != 0:
        men = result['message']
        typmsg = 'danger'
    else:
        ver = result['version']
        rev = result['revision']
        men = f'ver:{ver} rev:{rev}'
        typmsg = 'info'
    dispmsg = ('' != men) and (men is not None)
    # nombre = lf.get_nombre()
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": men,
         "dispmsg": dispmsg,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get('/cleanfiles')
async def cleanfiles(request: Request):
    import os
    import glob
    aux = checkLoginUser(request)
    if aux:
        return aux
    typmsg = 'success'
    # all ZIP files
    files = glob.glob('./**/*.zip', recursive=True)
    for f in files:
        try:
            # print(f'deleting {f}...')
            os.remove(f)
        except OSError:
            typmsg = 'danger'
    # Inside assets
    files = glob.glob('./assets/**/*', recursive=True)
    for f in files:
        try:
            # print(f'deleting {f}...')
            os.remove(f)
        except OSError:
            typmsg = 'danger'
    # nombre = lf.get_nombre()
    # Aquí falla, pero no es crítico
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": 'Done!',
         "dispmsg": True,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get('/installrequirements')
async def installrequirements(request: Request):
    # result = lf.installrequirements()
    # nombre = lf.get_nombre()
    typmsg = 'secondary'
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": result,
         "dispmsg": True,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get('/testfx')
async def testfx(request: Request):
    # result = lf.findOldVersionDb('EV000505r1642')
    # nombre = lf.get_nombre()
    typmsg = 'secondary'
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": result,
         "dispmsg": True,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get('/setuppermisos')
async def setuppermisos(request: Request):
    aux = checkLoginUser()
    if aux:
        return aux
    # r = lf.setupPermisos()
    result = json.loads(r)
    if result['rc'] != 0:
        men = result['message']
        typmsg = 'danger'
    else:
        men = result['message']
        typmsg = 'info'
    dispmsg = ('' != men) and (men is not None)
    # nombre = lf.get_nombre()
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": men,
         "dispmsg": dispmsg,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


# Input FORM data
@app.post('/prepareversion')
async def prepareversion(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    da = await request.form()
    da = jsonable_encoder(da)
    version = da['version']
    revision = da['revision']
    optionsincl = da['optionsincl']
    # file_path = lf.prepareversion(version, revision, optionsincl)
    file_name = f"{version}r{revision}.zip"
    if file_path:
        return FileResponse(
            path=file_path,
            headers={
                "Content-Disposition": "attachment;"
                f"filename={file_name}"
            }
        )
    else:
        # nombre = lf.get_nombre()
        typmsg = 'danger'
        return templates.TemplateResponse(
            "index.html",
            {"request": request,
             "message": 'Error found!',
             "dispmsg": True,
             "typmsg": typmsg,
             "nombre": nombre,
             "version": __version__}
        )


@app.get("/exportsvn", response_class=HTMLResponse)
async def exportsvn(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    # messageval = lf.exportsvn()
    # nombre = lf.get_nombre()
    typmsg = 'secondary'
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": messageval,
         "dispmsg": True,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get("/composerinstall", response_class=HTMLResponse)
async def composerinstall(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    # messageval = lf.composerinstall()
    # nombre = lf.get_nombre()
    typmsg = 'secondary'
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": messageval,
         "dispmsg": True,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get("/zipversion", response_class=HTMLResponse)
async def zipversion(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    # messageval = lf.zipversion()
    # nombre = lf.get_nombre()
    typmsg = 'secondary'
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": messageval,
         "dispmsg": True,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get("/oldvertocurrent", response_class=HTMLResponse)
async def oldvertocurrent(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    # r = lf.oldvertocurrent()
    result = json.loads(r)
    messageval = result['message']
    if result['rc'] != 0:
        typmsg = 'danger'
    else:
        typmsg = 'secondary'
    # nombre = lf.get_nombre()
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": messageval,
         "dispmsg": True,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get("/checkmd5", response_class=HTMLResponse)
async def checkmd5(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    # r = lf.checkmd5()
    result = json.loads(r)
    messageval = result['message']
    if result['rc'] != 0:
        typmsg = 'danger'
    else:
        typmsg = 'success'
    # nombre = lf.get_nombre()
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": messageval,
         "dispmsg": True,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get("/createmd5file", response_class=HTMLResponse)
async def createmd5file(request: Request):
    aux = checkLoginUser(request)
    if aux:
        return aux
    # messageval = lf.createmd5file()
    # nombre = lf.get_nombre()
    typmsg = 'secondary'
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
         "message": messageval,
         "dispmsg": True,
         "typmsg": typmsg,
         "nombre": nombre,
         "version": __version__}
    )


@app.get("/getfilemd5", response_class=HTMLResponse)
async def getfilemd5(request: Request, idfile: str):
    aux = checkLoginUser(request)
    if aux:
        return aux
    md5hash = idfile
    # r = lf.getfilemd5(md5hash)
    result = json.loads(r)
    if result['rc'] != 0:
        men = result['message']
        # nombre = lf.get_nombre()
        typmsg = 'danger'
        return templates.TemplateResponse(
            "index.html",
            {"request": request,
             "message": men,
             "dispmsg": True,
             "typmsg": typmsg,
             "nombre": nombre,
             "version": __version__}
        )
    else:
        file_path = result['ruta']
        fichero = result['fichero']
        return FileResponse(
            path=file_path,
            headers={
                "Content-Disposition": "attachment;"
                f"filename={fichero}"
            }
        )


if __name__ == '__main__':
    import os
    LOGGER_LEVEL = logging.DEBUG
    script_dir = os.path.dirname(__file__)
    rel_path = "./logs/"
    abs_file_path = os.path.join(script_dir, rel_path)
    class_name = (os.path.basename(__file__)[:-3])
    logfilename = (abs_file_path + class_name + '.log')

    formato_log = ('[%(asctime)s] python.%(levelname)s: %(module)s.py ' +
                   '%(processName)-10s %(funcName)s %(message)s')
    logFormatter = logging.Formatter(formato_log, datefmt='%Y-%m-%d %H:%M:%S')
    # Create the Logger
    handler = logging.handlers.TimedRotatingFileHandler(logfilename,
                                                        when="midnight",
                                                        interval=1)
    handler.setFormatter(logFormatter)
    logger = logging.getLogger("easyVIEW")
    logger.addHandler(handler)
    logger.setLevel(LOGGER_LEVEL)
    logger.info(f"LOG INIT {class_name} {__version__}")
    uvicorn.run(
        'fastapi_upgrader:app',
        host='0.0.0.0',
        port=8600,
        reload=True,
        debug=True
    )
    logger.info(f"LOG END {class_name} {__version__}")

# uvicorn fastapi_upgrader:app --host 0.0.0.0 --port 8000 --reload  --ws auto
# uvicorn fastapi_upgrader:app --reload
