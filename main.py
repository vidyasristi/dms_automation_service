import uvicorn
from fastapi import FastAPI

from model.InputModel import InputModel
from service.dms_service import deploy_dms
from util import log

app = FastAPI()
log.setup_custom_logger('root')


@app.post("/dms/startMigration")
def startAutomation(input: InputModel):
    deploy_dms(input)
    return input


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
