import streamlit as st
import json
import pandas as pd

import requests


URL = "http://127.0.0.1:8000"


def get_status():
    with requests.get(URL + "/status", stream=True) as r:
        for line in r.iter_lines():
            yield json.loads(line.decode("utf-8"))

def get_result():
    res = requests.get(URL + "/result")
    res = json.loads(res.text)
    res = json.loads(res["result"])
    res = pd.DataFrame(res)
    return res


pbar = st.empty()


if st.button("실행"):
    for event in get_status():
        pbar.progress(event['status'], event['msg'])
    pbar.progress(1.0, "완료")
    pbar.success("Complete")
    res = get_result()
    st.write(res)