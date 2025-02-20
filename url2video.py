"""
剧本生成的app界面
"""
from utils import *
import io
import requests


if "openai_model" not in st.session_state:
    st.session_state['openai_model']= MODEL_NAME
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# prompts
if "prompt_url_parse_tmp" not in st.session_state:
    st.session_state['prompt_url_parse_tmp']=open("prompts/prompt_url_parse.txt").read()

st.title("url2video工具")

st.header("Step1：解析url内容")
url = st.text_input(label="请输入url",value="http://xxxx.com")
clip_num = st.text_input(label="请输入镜头数",value=3)
if st.button(label="解析"):
    # 先解析网址的内容
    response = requests.get(url)
    if response.status_code == 200:
        webpage_content = response.text[:40000]
    else:
        webpage_content = "Failed"

    # 再用大模型进行总结
    if webpage_content != "Failed":
        prompt=st.session_state['prompt_url_parse_tmp'].replace('aaaaa',webpage_content).replace('bbbbb',clip_num)
    else:
        prompt=st.session_state['prompt_url_parse_tmp'].replace('aaaaa',url).replace('bbbbb',clip_num)
    with st.chat_message("assistant"):
        answer = st.write_stream(response_generator(prompt))
        json_parsed_res = parse_json_response(answer)
    st.session_state["messages"].append(['assistant', answer])
    st.session_state["url_parse_res"] = json_parsed_res
