import streamlit as st

st.set_page_config(
    page_title="简介",
    page_icon="👋",
)

st.write("# Video Gen By one click")

st.sidebar.success("请选择上面一个功能")

st.markdown(
    """
    ## 简介
    Video Gen By one click是一个一键视频生成的项目，可以将各类素材一键转化为视频
    #### 功能1：Url2Video
    输入一个url，我们自动帮你实现url解析到生成一个url介绍视频的全流程
    #### 功能2：story2Video
    输入一本小说，我们自动将小说的剧情进行解析，包括核心人物提取，场景和剧情解析，剧情可视化为视频的过程
    """
)