"""
剧本生成的app界面
"""

from ai_tools.utils import *
import requests
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

if "openai_model" not in st.session_state:
    st.session_state['openai_model']= MODEL_NAME
if "messages" not in st.session_state:
    st.session_state["messages"] = []


st.set_page_config(page_title="开始创作你的视频", page_icon="📈")
st.sidebar.header("▶️URL2Video")

# prompts
if "prompt_url_parse_tmp" not in st.session_state:
    st.session_state['prompt_url_parse_tmp']=open("prompts/prompt_url_parse.txt").read()
if "prompt_image_caption" not in st.session_state:
    st.session_state['prompt_image_caption']=open("prompts/prompt_img_caption.txt").read()
if "prompt_script_gen" not in st.session_state:
    st.session_state['prompt_script_gen']=open("prompts/prompt_script_gen.txt").read()
st.title("url2video工具")

st.header("Step1：解析url内容")
url = st.text_input(label="请输入url",value="https://www.ithome.com/0/813/427.htm")
if st.button(label="解析网址"):
    # 先解析网址的内容
    response = requests.get(url)
    if response.status_code == 200:
        webpage_content = response.text[:40000]
    else:
        webpage_content = "Failed"
    st.session_state["webpage_content"]=webpage_content

    # 再用大模型进行总结
    if webpage_content != "Failed":
        prompt=st.session_state['prompt_url_parse_tmp'].replace('aaaaa',webpage_content)
    else:
        prompt=st.session_state['prompt_url_parse_tmp'].replace('aaaaa',url)
    with st.chat_message("assistant"):
        # answer = st.write_stream(response_generator(prompt))
        answer = '{ "网站内容总结": "华为于2024年11月26日举办Mate品牌盛典，发布了一系列重磅产品，包括Mate 70系列、Mate X6、MatePad Pro等。发布会上介绍了Mate 70系列的设计、性能和影像规格，标榜为“史上最强大的Mate”，并首次搭载红枫原色影像等新技术。此外，还发布了WATCH ULTIMATE DESIGN手表和华为悦彰品牌的FreeBuds Pro 4耳机，展示了华为在智能科技领域的最新进展和创新。", "图片": [ "https://img.ithome.com/newsuploadfiles/2024/11/9028cf7c-0239-4bfc-810a-1a3f55c2d9a2.png?x-bce-process=image/format,f_auto", "https://img.ithome.com/newsuploadfiles/2024/11/798c9861-4ace-4f94-9db7-545e3274bb43.png?x-bce-process=image/format,f_auto", "https://img.ithome.com/newsuploadfiles/2024/11/80ed3973-8764-4add-b0ef-10a36de83d1b.jpg?x-bce-process=image/format,f_auto", "https://img.ithome.com/newsuploadfiles/2024/11/af6f4050-a924-4753-b9bb-37f606579e8a.png?x-bce-process=image/format,f_auto", "https://img.ithome.com/newsuploadfiles/2024/11/113abc0a-29b7-4ced-b54e-9551318c604a.jpg?x-bce-process=image/format,f_auto", "https://img.ithome.com/newsuploadfiles/2024/11/98df1b95-29da-4363-b54b-c9302f1f7226.jpg?x-bce-process=image/format,f_auto", "https://img.ithome.com/newsuploadfiles/2024/11/29925de5-44e0-4d02-96e5-9a244e3c31ba.png?x-bce-process=image/format,f_auto", "https://img.ithome.com/newsuploadfiles/2024/11/3555332d-e55c-4a61-87b4-8a35bc0e5923.png?x-bce-process=image/format,f_auto", "https://img.ithome.com/newsuploadfiles/2024/11/51e1cbb7-b56e-40d1-aef5-4d068d238be6.png?x-bce-process=image/format,f_auto", "https://img.ithome.com/newsuploadfiles/2024/11/468c85b3-764d-445f-afd2-29a43abb9f26.jpg?x-bce-process=image/format,f_auto" ], "视频": [] }'
        # st.write(answer)
        st.json(json.loads(answer))
        json_parsed_res = parse_json_response(answer)
    st.session_state["messages"].append(['assistant', answer])
    st.session_state["url_parse_res"] = json_parsed_res

st.header("step2: 识别图片")
if "url_parse_res" in st.session_state:
    image_urls=st.session_state["url_parse_res"]["图片"]
else:
    image_urls=[]
    st.write("请先解析网址")
valid_local_paths=[]
st.session_state["local_to_url"]={}
for img_url in image_urls:
    local_img_path=download_image(img_url)
    if local_img_path:
        # 判断图片尺寸是否合适
        img=Image.open(local_img_path)
        width, height = img.size
        if width/height>2 or height/width>2:
            continue
        valid_local_paths.append(local_img_path)
        st.session_state["local_to_url"][local_img_path]=img_url
st.write("有效图片数量：",len(valid_local_paths))
st.session_state['valid_local_paths']=valid_local_paths

# 实现一行可以左右滑动地显示所有图片
num_img_per_row=3
row_num=len(valid_local_paths)//num_img_per_row
if len(valid_local_paths)%num_img_per_row!=0:
    row_num+=1
for i in range(row_num):
    with st.container():
        for j,col in enumerate(st.columns(num_img_per_row)):
            if i*num_img_per_row+j<len(valid_local_paths):
                col.image(valid_local_paths[i*num_img_per_row+j])
            else:
                break

if st.button("解析图片内容"):
    progress_bar = st.progress(0)
    progress_gap = int(np.ceil(100/len(valid_local_paths)))
    st.session_state["image_caption_res"]={
        '图片1':'这张图片的背景是深黑色，营造出了一种宇宙的深邃感。在画面上方，有一段中文文字，内容为“华为 Mate 品牌盛典”。这说明这张图片与华为的Mate系列产品相关，可能是某个产品发布会的宣传海报。\n在下方的部分，有另一行中文文字：“2024年11月26日 14:30”，这表示盛典的具体日期和时间。\n画面的中心部分呈现出一个略微弯曲的金色弧线，这似乎是一颗行星的边缘，表面有着闪闪发光的颗粒，像是由星际尘埃组成。这个金色弧线的底部是深黑色，给人一种神秘而富有科技感的视觉效果。\n整体来看，这幅图片通过沉稳的黑色背景与闪耀的金色元素的对比，传达出了一种豪华、高端和未来感，暗示着即将到来的华为Mate系列的盛典将会是一个重要的、值得期待的事件。',
        '图片2':'这张图片展示了一款手机的后视图。手机的外观设计非常现代，背面采用了金属质感的材质，表面呈现出细腻的拉丝纹理，给人一种高档、精致的感觉。\n在手机的左上角，有一个圆形的相机模组，内部包括几个镜头。相机模组的中心是一个大镜头，周围是两个较小的镜头，设计简洁而富有科技感。相机的设计与整体手机的外观相得益彰。\n图片的背景模糊不清，但可以看到一些流动、波动的形状，这可能是视觉效果的一部分，强调了手机的现代感和动感。背景的色调较为暗淡，突出手机本身的亮眼设计。\n在图片的右下角，有一个小的水印，显示了网址“www.ithome.com”，而左下角有一个图标，可能代表了品牌或某种认证标识。\n整体来看，图片传达出一种科技前卫、未来感十足的氛围，吸引了观众的注意力，突显了这款手机的设计和科技特点。',
        '图片3':'图片展示了多个场景，传达了一种与AI相关的多功能应用。\n篮球场景：在上方的部分，几名身穿蓝色运动服的篮球运动员正在进行跳投，体现出一种动态的运动感。运动员的动作被捕捉到，显示出不同的投篮姿势，背景是一个标准的篮球场，篮筐清晰可见。\n科技交流：在右上方，有两个人在一个室内环境中互动。两人同时举起手机，似乎在进行某种技术交流。场景中的窗户透入阳光，营造了温暖的氛围。\n私密讨论：在左下方，显示一名男性与一名女性在桌子边密切交流。男性手中持有玻璃杯，似乎在享用饮品，而女性则正在关注自己的手机，两人之间的互动显得亲密且专注。\n拍摄场景：右下方显示了一位女性，手中拿着一部相机，似乎正在准备拍照。她的造型时尚，背景是一个模糊的室内环境，给人一种闲适且有意识的感觉。\n整个画面有一些文字说明，包括“AI运动轨迹”、“AI隔空传送”、“AI消息随身”和“AI降噪通话”，这些文字与场景相关，强调了AI技术在运动、通信等方面的应用。整个页面的设计现代而简洁，吸引观众的注意力。'
    }
    for i,img_path in enumerate(valid_local_paths):
        # prompt=st.session_state['prompt_image_caption']
        # img_url=st.session_state["local_to_url"][img_path]
        # img_caption=call_multi_model_gpt(prompt,img_url)
        # st.session_state["image_caption_res"][img_path]=img_caption
        # img_caption = st.session_state["image_caption_res"][i]
        # with st.chat_message("assistant"):
        #     st.write("图片{} : {}".format(i+1,img_caption))
        progress_index=min((i+1)*progress_gap,100)
        progress_bar.progress(progress_index)
    st.json(st.session_state["image_caption_res"])

st.header("Step3：生成剧本")
clip_num = st.text_input(label="请输入镜头数",value=3)
if st.button(label="生成剧本"):
    image_caption=json.dumps(st.session_state["image_caption_res"],ensure_ascii=False)
    webpage_content=st.session_state["webpage_content"]
    prompt=st.session_state['prompt_script_gen'].replace('aaaaa',webpage_content).replace('bbbbb',image_caption).replace('ccccc',clip_num)
    with st.chat_message("assistant"):
        answer = {
            "镜头1": {
                "时长": 10,
                "镜头描述": "华为 Mate 品牌盛典的开场画面，展示品牌的整体引领地位和即将发布的产品。",
                "图片来源": "生成",
                "图片描述": "一张具有宇宙深邃感的图片，上方有文字‘华为 Mate 品牌盛典’和日期时间，中心有金色弧线。",
                "旁白": "欢迎来到华为 Mate 品牌盛典！在这个令人期待的时刻，我们将揭开华为 Mate 70 系列及其强大的Mate X6的神秘面纱！"
            },
            "镜头2": {
                "时长": 15,
                "镜头描述": "突出展示华为 Mate 70 系列手机，彰显其卓越设计与技术。",
                "图片来源": "图片1",
                "图片描述": "展现了Mate 70的现代化设计，金属质感及精致的相机模组，背景模糊衬托手机的科技感。",
                "旁白": "现在我们来看看Mate 70，这款手机以其令人惊叹的设计和强大的相机技术，展现出未来科技的无限可能，让你在每个瞬间都能记录下最美的画面。"
            },
            "镜头3": {
                "时长": 12,
                "镜头描述": "展示华为的AI技术在多个应用场景中的应用，突显其智能化的能力。",
                "图片来源": "生成",
                "图片描述": "一幅融合了多重场景的画面，显示AI技术在运动、交流和拍摄中的应用，文字强调其多功能性。",
                "旁白": "华为 Mate 系列不仅是手机，更是你的生活助手。通过强大的AI技术，无论是在运动场上还是与朋友的交流中，也或是在拍照时，它都能为你提供超乎想象的智能体验！"
            }
        }
        answer=json.dumps(answer,ensure_ascii=False)
        # answer = st.write_stream(response_generator(prompt))
        json_parsed_res = parse_json_response(answer)
        st.json(json_parsed_res)
    st.session_state["messages"].append(['assistant', answer])
    st.session_state["script_gen_res"] = json_parsed_res

st.header("Step4：生成图片")
if st.button(label="生成图片"):
    image_urls={
        '镜头1':"https://filesystem.site/cdn/20250222/ix9jcmGjN1KsbbJdIunWSNw9qqX9Pb.webp",
        '镜头3':"https://filesystem.site/cdn/20250222/bHbCJT7k5EDMscXVvC4GHbJologBne.webp"
    }
    script=st.session_state["script_gen_res"]
    keys=list(script.keys())

    # 实现一行可以左右滑动地显示所有图片
    for content_type in ['镜头名','旁白','图片描述','图片']:
        num_img_per_row = 3
        row_num = len(keys) // num_img_per_row
        if len(keys) % num_img_per_row != 0:
            row_num += 1
        for i in range(row_num):
            with st.container():
                for j, col in enumerate(st.columns(num_img_per_row)):
                    if i * num_img_per_row + j < len(keys):
                        key=keys[i*num_img_per_row+j]
                        clip=script[key]
                        if content_type=='镜头名':
                            col.write('【{}】'.format(key))
                        elif content_type=='旁白':
                            col.write('[旁白]')
                            col.write(clip['旁白'])
                        elif content_type=='图片描述':
                            col.write('[图片描述]')
                            col.write(clip['图片描述'])
                        else:
                            # 生成图片
                            if clip['图片来源']=='生成':
                                # img_url=call_gpt_image_gen(v['图片描述'])
                                img_url = image_urls[key]
                                st.write("generate img for {}:{}".format(key, img_url))
                                img_path = download_image(img_url)
                            else:
                                img_index = int(script[keys[i*num_img_per_row+j]]['图片来源'].replace("图片", "")) - 1
                                img_path = valid_local_paths[img_index]
                            st.session_state['script_gen_res'][key]['图片路径'] = img_path
                            col.image(img_path)
                    else:
                        break


st.header("Step5：生成音频")
if st.button(label="生成音频"):
    script = st.session_state["script_gen_res"]
    keys = list(script.keys())

    local_audio_path={
        '镜头1':'tmp_audios/镜头1.mp3',
        '镜头2': 'tmp_audios/镜头2.mp3',
        '镜头3': 'tmp_audios/镜头3.mp3',
    }
    # 实现一行可以左右滑动地显示所有图片
    for content_type in ['镜头名', '旁白', '音频', '图片']:
        num_img_per_row = 3
        row_num = len(keys) // num_img_per_row
        if len(keys) % num_img_per_row != 0:
            row_num += 1
        for i in range(row_num):
            with st.container():
                for j, col in enumerate(st.columns(num_img_per_row)):
                    if i * num_img_per_row + j < len(keys):
                        key = keys[i * num_img_per_row + j]
                        clip = script[key]
                        if content_type == '镜头名':
                            col.write('【{}】'.format(key))
                        elif content_type == '旁白':
                            col.write('[旁白]')
                            col.write(clip['旁白'])
                        elif content_type == '音频':
                            col.write('[音频]')
                            # audio_path=call_gpt_text2audio_gen(clip['旁白'],key)
                            audio_path=local_audio_path[key]
                            if audio_path:
                                col.audio(audio_path)
                            else:
                                col.write("音频生成失败")
                            st.session_state['script_gen_res'][key]['音频路径']=audio_path
                        else:
                            col.write('[镜头画面]')
                            img_path=clip['图片路径']
                            col.image(img_path)
                    else:
                        break

st.header("Step6：合成视频")
# 对每个clip
# 先图片做裁剪到指定尺寸
# 图片按照audio的时长，扩展成对应的无声片段
# 视频+字母+audio
# 几个clip拼接起来
# 一些条件
resolution = st.radio("分辨率",['1080P','720P','540P'],horizontal=True)
ratio = st.radio("长宽比",["16:9","9:16","4:3","3:4","1:1"],horizontal=True)
width,height = compute_resolution(resolution,ratio)
# 计算实际的分辨率
if st.button(label="生成视频"):
    script = st.session_state["script_gen_res"]
    keys = list(script.keys())

    # 实现一行可以左右滑动地显示所有图片
    final_clips=[]
    for content_type in ['镜头名', '旁白', '音频','图片','视频']:
        num_img_per_row = 3
        row_num = len(keys) // num_img_per_row
        if len(keys) % num_img_per_row != 0:
            row_num += 1
        for i in range(row_num):
            with st.container():
                for j, col in enumerate(st.columns(num_img_per_row)):
                    if i * num_img_per_row + j < len(keys):
                        key = keys[i * num_img_per_row + j]
                        clip = script[key]
                        if content_type == '镜头名':
                            col.write('【{}】'.format(key))
                        elif content_type == '旁白':
                            col.write('[旁白]')
                            col.write(clip['旁白'])
                        elif content_type == '音频':
                            col.write('[音频]')
                            audio_path = clip['音频路径']
                            col.audio(audio_path)
                        elif content_type == '图片':
                            col.write('[镜头画面]')
                            img_path=clip['图片路径']
                            col.image(img_path)
                        else:
                            col.write('[视频片段]')
                            img_path=clip['图片路径']
                            # 图片按照分辨率裁剪
                            resized_img=crop_and_resize_img(img_path,width,height)
                            # 将字母按照标点符号划分，并确定每段文字持续时长
                            audio_clip = AudioFileClip(clip['音频路径'])
                            title_splits=split_subtitle(clip['旁白'],audio_clip.duration)
                            video_clips=[]
                            font_path = 'tiny_font/STXINGKA.TTF'
                            for title_part in title_splits:
                                # 图片上加上文字
                                img_with_text=render_text_on_image(title_part[0],font_path,resized_img)
                                # 图片按照audio时长进行扩展
                                image_clip = ImageClip(np.array(img_with_text), duration=title_part[2])
                                video_clips.append(image_clip)

                            # 带字幕的视频拼接
                            combined_video_clips=concatenate_videoclips(video_clips,method='compose')
                            # 加上音频
                            final_video_clip=combined_video_clips.set_audio(audio_clip)
                            # 展示最终的视频
                            if not os.path.exists('tmp_videos'):
                                os.makedirs('tmp_videos')
                            video_path = 'tmp_videos/{}.mp4'.format(key)
                            final_video_clip.write_videofile(video_path,fps=25)
                            if os.path.exists(video_path):
                                col.video(video_path)
                                final_clips.append(final_video_clip)
                            else:
                                st.write("视频生成失败")
                    else:
                        break

    # 展示最终的视频
    st.write("最终的视频")
    final_video=concatenate_videoclips(final_clips)
    video_path = 'tmp_videos/final.mp4'
    final_video.write_videofile(video_path, fps=25)
    if os.path.exists(video_path):
        st.video(video_path)
    else:
        st.write("视频合成失败")

