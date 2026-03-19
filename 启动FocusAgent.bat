@echo off
call .\focus_env\Scripts\activate
python -m streamlit run app_main.py
pause