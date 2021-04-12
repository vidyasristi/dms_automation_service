import uvicorn
from fastapi import FastAPI

from model.InputModel import InputModel, DeleteModel
from service.dms_service import deploy_dms, delete_dms
from util import log_util

app = FastAPI()
log_util.setup_custom_logger('root')


@app.post("/dms/createMigration")
def createMigration(input: InputModel):
    return deploy_dms(input)


@app.delete("/dms/deleteMigration")
def deleteMigration(deleteInput: DeleteModel):
    delete_dms(deleteInput)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
