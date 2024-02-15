from fastapi import FastAPI, Request
import uvicorn
import requests
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import httpx
import threading
import datetime
import os

app = FastAPI()

BASE_PATH = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory="static"), name="static")
TEMPLATES = Jinja2Templates(directory="templates")


resolve_folder=Path.joinpath(BASE_PATH,"resolve_models")


def load_json():
    f = open('data.json')
    data = json.load(f)
    return data

def save_json(data):
    with open("data.json", "w") as outfile:
        json.dump(data, outfile, indent=4)
    return None


def request_task(url):
    requests.get(url)

def fire_and_forget(url):
    threading.Thread(target=request_task, args=(url, )).start()



def get_resolve_files_list():
    resolve_files_list=[]
    for file in os.listdir(resolve_folder):
        if file.endswith(".rsa"):
            resolve_files_list.append(file)
    return resolve_files_list


# @app.get("/open_resolve")
# def open_resolve():
#     response = requests.get("http://127.0.0.1:3000/open_resolve/")
#     return response.json()



# @app.get("/open_resolve_file")
# def open_resolve_file():
#     response = requests.get("http://127.0.0.1:3000/open_resolve_file/")
#     return response.json()


# @app.get("/run")
# def run():
#     response = requests.get("http://127.0.0.1:3000/run/")
#     return response.json()


@app.get("/")
def main_page(request: Request):
    
    data=load_json()
    servers=data["remote_servers"]

    
    resolve_models_list=get_resolve_files_list()

    
    return TEMPLATES.TemplateResponse(
        "main.html",
        {
            "request":request, 
            "remote_servers": servers,
            "resolve_models_list":resolve_models_list
        }
    )

@app.get("/cases")
def cases_page(request: Request):
    
    data=load_json()
    servers=data["remote_servers"]

    
    resolve_models_list=get_resolve_files_list()

    
    return TEMPLATES.TemplateResponse(
        "cases.html",
        {
            "request":request, 
            "remote_servers": servers,
            "resolve_models_list":resolve_models_list
        }
    )


@app.get("/server/{id}")
def server_page(request: Request, id):
    
    data=load_json()
    
    data["remote_servers"][int(id)]["data"]["forecast_data"]["show"]=0
    server=data["remote_servers"][int(id)]

    return TEMPLATES.TemplateResponse(
        "server.html",
        {
            "request":request, 
            "remote_server": server
        }
    )




@app.get("/server/{id}/run")
async def server_run_page(request: Request, id):
    
    data=load_json()
   
    fire_and_forget("http://127.0.0.1:3000/run")

    data["remote_servers"][int(id)]["status"]="running"
    data["remote_servers"][int(id)]["data"]["forecast_data"]["show"]=0
    data["remote_servers"][int(id)]["last_run"]=datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")

    save_json(data)

    server=data["remote_servers"][int(id)]

    return TEMPLATES.TemplateResponse(
        "server.html",
        {
            "request":request, 
            "remote_server": server
        }
    )


@app.get("/server/{id}/check_status")
def server_status_page(request: Request, id):
    
    data=load_json()
   
    result = requests.get("http://127.0.0.1:3000/check_status")
    status=result.json()["status"]

    data["remote_servers"][int(id)]["status"]=status
    data["remote_servers"][int(id)]["data"]["forecast_data"]["show"]=0

    save_json(data)

    server=data["remote_servers"][int(id)]

    return TEMPLATES.TemplateResponse(
        "server.html",
        {
            "request":request, 
            "remote_server": server
        }
    )


@app.get("/server/{id}/get_forecast_data")
def get_forecast_data_page(request: Request, id):
    
    data=load_json()
   
    forecast_data = requests.get("http://127.0.0.1:3000/get_forecast_data").json()

    data["remote_servers"][int(id)]["data"]["forecast_data"]["results"]=forecast_data["results"]    
    data["remote_servers"][int(id)]["data"]["forecast_data"]["show"]=1

    save_json(data)

    server=data["remote_servers"][int(id)]

    return TEMPLATES.TemplateResponse(
        "server.html",
        {
            "request":request, 
            "remote_server": server
        }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)