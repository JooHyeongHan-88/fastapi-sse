import asyncio
import websockets
import streamlit as st
import json
import pandas as pd
import requests


URL = "http://127.0.0.1:8000"
URL_WS = "ws://127.0.0.1:8000"


def start_process():
    with requests.get(URL + "/process", stream=True) as r:
        for line in r.iter_lines():
            yield json.loads(line.decode("utf-8"))

def get_result():
    res = requests.get(URL + "/result")
    res = json.loads(res.text)
    res = json.loads(res["result"])
    res = pd.DataFrame(res)
    return res

async def start_process_ws():
    async with websockets.connect(URL_WS + "/process") as websocket:
        processing = True
        while processing:
            res = await websocket.recv()
            res = eval(json.loads(res))
            if 'status' in res:
                pbar.progress(res['status'], res['msg'])
            else:
                processing = False
                pbar.success("Complete")
                res = json.loads(res["result"])
                res = pd.DataFrame(res)
                st.write(res)


pbar = st.empty()


c1, c2 = st.columns(2)

if c1.button("실행 (SSE)"):
    for event in start_process():
        pbar.progress(event['status'], event['msg'])
    pbar.success("Complete")
    res = get_result()
    st.write(res)

if c2.button("실행 (WS)"):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(start_process_ws())