import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import pandas as pd
import time


app = FastAPI()


class Job():
    def __init__(self):
        self._result = pd.DataFrame()

    @property
    def result(self):
        return self._result


job = Job()


async def generator():
    job._result = pd.DataFrame()
    for i in range(10):
        if i == 9:
            job._result = pd.DataFrame({"A": [1, 2, 3], "B": [10, 20, 30]})
        await asyncio.sleep(0.1)
        yield json.dumps({"status": 0.1*(i + 1), "msg": f"status: {i + 1}/[10]"}) + "\n"


@app.get("/")
async def main():
    return {"msg": "Hello World"}


@app.get("/status")
async def return_status():
    return StreamingResponse(generator(), media_type='application/json')


@app.get("/result")
async def return_result():
    df = job.result
    return {"result": df.to_json()}