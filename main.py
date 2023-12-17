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

    async def query(self):
        await asyncio.sleep(3)
        self._result = pd.DataFrame({"A": [1, 2, 3], "B": [10, 20, 30]})

    async def preprocess(self):
        await asyncio.sleep(3)
        self._result = pd.DataFrame({"A": [1, 2, 3, 4], "B": [10, 20, 30, 40]})

    async def process(self):
        yield json.dumps({"status": 0.1, "msg": "query"}) + "\n"
        await self.query()
        yield json.dumps({"status": 0.5, "msg": "preprocess"}) + "\n"
        await self.preprocess()
        yield json.dumps({"status": 1.0, "msg": "complete"})


job = Job()


@app.get("/")
async def main():
    return {"msg": "Hello World"}


@app.get("/process")
async def start_process():
    return StreamingResponse(job.process(), media_type='application/json')


@app.get("/result")
async def return_result():
    return {"result": job.result.to_json()}