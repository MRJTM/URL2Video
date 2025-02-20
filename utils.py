import streamlit as st
import os
from openai import OpenAI
from docx import Document
import json

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENAI_BASE_URL = st.secrets["BASE_URL"]
os.environ['OPENAI_API_KEY'] =OPENAI_API_KEY
os.environ['OPENAI_BASE_URL'] =OPENAI_BASE_URL

persist_directory='text_persist'
collection_name='text_collection'
# model_name="gpt-4o-mini-2024-07-18"
model_name='o1-mini-2024-09-12'

client = OpenAI(api_key=OPENAI_API_KEY,base_url=OPENAI_BASE_URL)

def load_file(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    docs = "\n".join(full_text)
    docs=docs[:40000]
    return docs

def response_generator(prompt=''):
    stream = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": 'user', "content": prompt}
        ],
        stream=True
    )
    return stream

def parse_json_response(response):
    raw_res=response
    if "```json" in raw_res and "```" in raw_res:
        res = raw_res.split("```json")[1].split("```")[0]
    else:
        res = raw_res
    res = res.replace('\n', '').replace(' ', '')
    res = json.loads(res, strict=False)
    return res
