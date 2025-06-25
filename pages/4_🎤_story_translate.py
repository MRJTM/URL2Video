from ai_tools.text2text import *
from ai_tools.text2image import *
import chardet
def try_decode(file_data, encodings):
    for encoding in encodings:
        try:
            return file_data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


# openai_client=OpenAI(api_key=st.secrets['OPENAI_API_KEY'],base_url=st.secrets['BASE_URL'])
# MODEL_NAME = st.secrets["MODEL_NAME"]
openai_client=OpenAI(api_key=st.secrets['DEEPSEEK_API_KEY'],base_url=st.secrets['DEEPSEEK_BASE_URL'])
MODEL_NAME = st.secrets["DEEPSEEK_MODEL_NAME"]

st.set_page_config(page_title="开始翻译你的小说", page_icon="🎤")
st.sidebar.header("🎤Story_Translate")

st.header("第一步: 小说解析",divider=True)
# 上传小说文本
uploaded_file=st.file_uploader('上传小说文本',type=["txt"])
text=""
lines=[]
if uploaded_file is not None:
    # 读取文件内容
    raw_data = uploaded_file.read()
    result = chardet.detect(raw_data)
    detected_encoding = result['encoding']
    st.write("file encoding:", detected_encoding)
    # 尝试使用检测到的编码解码
    if detected_encoding is not None:
        if detected_encoding not in ['gb2312','GB2312']:
            text = raw_data.decode(detected_encoding)
        else:
            text = raw_data.decode('gbk')
        lines = text.splitlines()
        st.write("line num:", len(lines))
    else:
        # 如果检测到的编码失败，尝试其他常见编码
        encodings = ['utf-8', 'gbk', 'latin1', 'iso-8859-1']
        text = try_decode(raw_data, encodings)

        if text is not None:
            lines = text.splitlines()
            st.write("line num:", len(lines))
        else:
            st.error("无法解码文件内容，请确认文件编码。")

    st.write("line num:", len(lines))

    # 创建一个滚动文本框来展示内容
    st.text_area("小说内容", value=text, height=500)  # 可以调整高度

    # 展示小说按照章节结构化的json格式
    structure_res=structure_story(lines)
    st.json(structure_res)
    st.session_state['structure_res']=structure_res
else:
    st.info("请在上传一个.txt格式的小说文本。")

parse_stroy_fake=st.radio("fake_parse",["not fake","fake"],horizontal=True)

target_language=st.radio("目标语言",["英语","法语","日语","韩语","俄语","西班牙语"],index=0,horizontal=True)
model=st.radio("模型名",["o3-mini-2025-01-31","deepseek-chat"],index=0,horizontal=True)
if 'deepseek' in model.lower():
    openai_client=OpenAI(api_key=st.secrets['DEEPSEEK_API_KEY'],base_url=st.secrets['DEEPSEEK_BASE_URL'])
    MODEL_NAME = st.secrets["DEEPSEEK_MODEL_NAME"]
else:
    openai_client=OpenAI(api_key=st.secrets['OPENAI_API_KEY'],base_url=st.secrets['BASE_URL'])
    MODEL_NAME = st.secrets["MODEL_NAME"]
if st.button(label="翻译"):
    if st.session_state.get('structure_res') is not None:
        is_fake=parse_stroy_fake=="fake"
        # 分章节翻译
        structure_res=st.session_state['structure_res']
        translate_res={}
        # 显示进度条
        progress_bar = st.progress(0)
        for i,chapter_name in enumerate(structure_res.keys()):
            chapter_content=structure_res[chapter_name]
            res=translate_story(story=chapter_content,target_language=target_language,client=openai_client,model_name=MODEL_NAME,fake=is_fake)
            translate_res[chapter_name]={
                '原始内容':chapter_content,
                '翻译结果':res,
            }
            progress_bar.progress((i + 1) / len(structure_res))
        st.session_state['translate_res']=translate_res
        st.json(translate_res)
    else:
        st.info("请上传小说")


