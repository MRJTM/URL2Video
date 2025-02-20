"""
剧本生成的app界面
"""
from utils import *
import io

if "openai_model" not in st.session_state:
    st.session_state['openai_model']="gpt-4o-mini-2024-07-18"
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# prompts

st.title("url2video工具")

st.header("Step1：解析url内容")
url = st.text_area(label='请输入url', value="http:/xxxxx")

