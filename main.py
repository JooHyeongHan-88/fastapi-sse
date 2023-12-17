import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import json
import pandas as pd
import logging
from typing import List


logging.basicConfig(
    format='[%(levelname)s] %(asctime)s (%(name)s) :: %(message)s',
    level=logging.DEBUG,
    datefmt='%m/%d/%Y %I:%M:%S %p',
)


app = FastAPI()


# 1. SSE
class Job():
    def __init__(self):
        self._result = pd.DataFrame()

    @property
    def result(self):
        return self._result

    async def query(self):
        for i in range(10):
            logging.debug(f"query {i}")
            await asyncio.sleep(0.2)
        self._result = pd.DataFrame({"A": [1, 2, 3], "B": [10, 20, 30]})

    async def preprocess(self):
        for i in range(10):
            logging.debug(f"preprocess {i}")
            await asyncio.sleep(0.2)
        self._result = pd.concat([self.result, pd.DataFrame({"A": [4], "B": [40]})]).reset_index(drop=True)

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


# 2. WebSocket
async def query_ws():
    for i in range(10):
        logging.debug(f"query {i}")
        await asyncio.sleep(0.2)
    return pd.DataFrame({"A": [1, 2, 3], "B": [10, 20, 30]})

async def preprocess_ws(df):
    for i in range(10):
        logging.debug(f"preprocess {i}")
        await asyncio.sleep(0.2)
    return pd.concat([df, pd.DataFrame({"A": [4], "B": [40]})]).reset_index(drop=True)

@app.websocket("/process")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket.send_json(json.dumps({"status": 0.1, "msg": "query"}))
        df = await query_ws()
        await websocket.send_json(json.dumps({"status": 0.5, "msg": "preprocess"}))
        df = await preprocess_ws(df)
        await websocket.send_json(json.dumps({"status": 1.0, "msg": "complete"}))
        await websocket.send_json(json.dumps({"result": df.to_json()}))
    except WebSocketDisconnect:
        websocket.close()
        logging.info(f"Client {websocket} disconnected")