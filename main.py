import uvicorn
from fastapi import FastAPI
from model.InputModel import *
from service.create_automation import *

app = FastAPI()


@app.post("/dms/startAutomation")
def startAutomation(input: InputModel):
    deploy_dms(input)
    return input


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
