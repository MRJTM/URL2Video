"""
剧本生成的app界面
"""
import json
import streamlit as st

page1 = st.Page("pages/1_☁️_项目简介.py")
page2 = st.Page("pages/2_📷_url2video.py")
page3 = st.Page("pages/3_📚_story2video.py")
page4 = st.Page("pages/4_🎤_story_translate.py")

pg = st.navigation([page1, page2,page3,page4])
pg.run()