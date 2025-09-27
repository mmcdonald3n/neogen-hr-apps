# Neogen HR Apps (Streamlit)

Seven apps behind a clean landing page:

1. Job Description Generator  
2. Job Advert Generator  
3. Interview Guide Generator  
4. Interview Question Generator  
5. Hiring Manager Toolkit  
6. Interview Feedback Collector (SQLite)  
7. Shortlisting Summary Tool

## Dev Quickstart

`ash
$ python -m venv .venv
$ .\.venv\Scripts\Activate.ps1
(.venv) $ pip install -r requirements.txt
(.venv) $ streamlit run app.py
`

Set your OpenAI key in .streamlit/secrets.toml.

Deployed via Streamlit Community Cloud: add the same secrets there.
