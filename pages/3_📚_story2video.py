from ai_tools.text2text import *
from ai_tools.text2image import *

MODEL_NAME = st.secrets["MODEL_NAME"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
BASE_URL = st.secrets["BASE_URL"]

openai_client=OpenAI(api_key=OPENAI_API_KEY,base_url=BASE_URL)

st.set_page_config(page_title="开始创作你的视频", page_icon="📈")
st.sidebar.header("▶️URL2Video")

st.header("第一步: 小说解析",divider=True)
# 上传小说文本
uploaded_file=st.file_uploader('上传小说文本',type=["txt"])
text=""
if uploaded_file is not None:
    # 读取文件内容
    try:
        text = uploaded_file.read().decode("gbk")
    except UnicodeDecodeError:
        st.error("无法解码文件内容，请确确认文件编码。")
        text = ""

    # 创建一个滚动文本框来展示内容
    st.text_area("小说内容", value=text, height=500)  # 可以调整高度
else:
    st.info("请在上传一个.txt格式的小说文本。")

parse_stroy_fake=st.radio("fake_parse",["not fake","fake"],horizontal=True)
if st.button(label="解析小说"):
    if len(text):
        is_fake=parse_stroy_fake=="fake"
        res=parse_story(story=text[:10000],client=openai_client,model_name=MODEL_NAME,fake=is_fake)
        st.session_state['script']=res
        st.json(res)
    else:
        st.info("请上传小说")

st.header("第二步: 产生角色人像",divider=True)
model_name=st.radio("模型名",["dall-e-3"],index=0,horizontal=True)
size=st.radio("图片尺寸",["1024x1024","1024x1536"],index=0,horizontal=True)
if st.button("产生角色"):
    if 'script' in st.session_state:
        script=st.session_state['script']
        charac_keys=list(script['主要人物'].keys())
        num_img_per_row = 5
        row_num = len(charac_keys) // num_img_per_row
        if len(charac_keys) % num_img_per_row != 0:
            row_num += 1

        for content_type in ['角色','姓名','年龄','性别','长相','性格','职业','背景','特点','概述','img']:
            for i in range(row_num):
                with st.container():
                   for j,col in enumerate(st.columns(num_img_per_row)):
                       charac_key=f'人物{i*num_img_per_row+j+1}'
                       if content_type=='角色':
                           col.write("【{}】".format(charac_key))
                       elif content_type=='img':
                           img_path=text2image(script['主要人物'][charac_key]['文生图prompt'],openai_client,model_name=model_name,size=size,filename=f'charac{i*num_img_per_row+j+1}.jpg')
                           col.image(img_path)
                       else:
                           col.write("[{}]".format(content_type))
                           col.write(script['主要人物'][charac_key][content_type])

    else:
        st.info("请先完成小说解析")

st.header("第三步: 产生剧情画面",divider=True)

st.header("第四步: 产生人物TTS",divider=True)

st.header("第五步: 画面+TTS产生视频",divider=True)

st.header("第六步: 合成视频",divider=True)
