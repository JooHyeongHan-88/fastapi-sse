@echo off
python -m venv .venv
pip install -r requiremens.txt
./.venv/Scripts/activates
@REM uvicorn main:app --reload
@REM streamlit run main.py