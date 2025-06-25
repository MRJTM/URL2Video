from ai_tools.utils import *
import chardet

OPENAI_API_KEY = "sk-L1PKva8uq22H0aU3947e5320146345E6A70d68CbCa69D02f"
OPENAI_BASE_URL = "https://api.132999.xyz/v1"
OPENAI_MODEL_NAME = "o3-mini-2025-01-31"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = "sk-21f4c3de12b7462b9352a6e778832857"
DEEPSEEK_MODEL_NAME = "deepseek-chat"
def text2text(prompt='',client=None,base_url=None,api_key=None,model_name=None,stream=False):
    if model_name is None:
        model_name=''
    if 'deepseek' in model_name:
        if api_key is None:
            api_key=DEEPSEEK_API_KEY
        if base_url is None:
            base_url=DEEPSEEK_BASE_URL
    else:
        if api_key is None:
            api_key=OPENAI_API_KEY
        if base_url is None:
            base_url=OPENAI_BASE_URL


    if client is None:
        client = OpenAI(api_key=api_key,base_url=base_url)

    res = client.chat.completions.create(
        model= model_name,
        messages=[
            {"role": 'user', "content": prompt}
        ],
        stream= stream
    )
    if stream:
        return res
    else:
        try:
            res=res.choices[0].message.content
        except:
            res=""
        return res

def parse_story(story="",client=None,model_name=None,fake=False):
    if fake:
        fake_res={"主要人物":{"人物1":{"姓名":"白兰·杰索","年龄":12,"性别":"男","长相":"白色短发，紫色狭长狐眼，婴儿肥面颊，笑眯眯如狐狸","性格":"聪慧冷静、自信淡定，偶尔顽皮好奇，内心渴望真实情感","职业":"立海大附属中学一年级学生，网球社新生","背景":"日意混血，孤儿，继承遗产，原为平行世界高智商“世界之柱”","特点":"拥有大空火焰与六种属性火焰，金手指体质，游戏视人生","概述":"自小天赋卓越，因游戏般的世界观被囚小岛，后穿越成为12岁网球少年，以火焰与网球为桥梁探索人情","文生图prompt":"full-bodyportraitofa12-year-oldJapanese-Italianmixedboywithshortmessywhitehair,narrowvioletfox-likeeyes,roundyouthfulcheeks,wearinggreenschooluniformandtennisgear,holdingatennisracketwithfaintflameauraaroundhisarm,expressioncleverandplayful,anime-style,highdetail"},"人物2":{"姓名":"切原赤也","年龄":12,"性别":"男","长相":"黑色海带头发，清澈湖绿色眼睛，身材瘦削却充满活力","性格":"热血嚣张、直率冲动，但纯真真诚，重情义","职业":"立海大附属中学一年级学生，网球社新生","背景":"小有名气的小学网球选手，“神奈川恶魔”之称，弃格斗专攻网球","特点":"天赋惊人，专注即燃“红眼状态”，单细胞却极具感染力","概述":"从网球杂志中见过冠军照立志考入立海大附中，凭毅力与天赋一路过关斩将，渴望成为第一","文生图prompt":"full-bodyportraitofa12-year-oldJapaneseboywithshortblackhairinaseaweedstyle,brightlake-greeneyes,leanathleticbuild,wearingyellowtennisclubuniform,holdingracketreadytoserve,expressionfierceandenthusiastic,anime-style,highdetail"},"人物3":{"姓名":"幸村精市","年龄":14,"性别":"男","长相":"银蓝色蜷发，蓝紫色柔美眼眸，脸上常带温柔微笑","性格":"温和坚定、感性富领导力，对后辈关怀备至","职业":"立海大附属中学网球社部长（高二或高三）","背景":"“三巨头”之一，网球社灵魂人物，以实力与德行著称","特点":"能看透球路本质，技术全面且策略多变","概述":"网球社的领袖，温柔中带威严，激励新人成长，是白兰与切原心中的榜样","文生图prompt":"full-bodyportraitofa14-year-oldJapaneseboywithcurlysilver-bluehair,softblue-violeteyes,slenderyetathleticbuild,wearingwhiteandyellowtennisclubuniformwitharmband,standingconfidentlywithracket,expressiongentlebutauthoritative,anime-style,highdetail"},"人物4":{"姓名":"真田弦一郎","年龄":15,"性别":"男","长相":"深红色微卷短发，高挑身材，眼神锐利","性格":"严肃苛刻、好胜心强，口头禅“太松懈了”","职业":"立海大附属中学网球社副部长（三年级正选）","背景":"“三巨头”之一，以严格训练闻名","特点":"打法稳健，注重细节，善于鼓舞队友","概述":"网球社中坚力量，以严格要求和高标准推动全队进步","文生图prompt":"full-bodyportraitofa15-year-oldJapaneseboywithdeepredtousledhair,tallathleticframe,intenseeyes,wearingteamtracksuitovertennisgear,holdingracketatrest,expressionseriousandcommanding,anime-style,highdetail"},"人物5":{"姓名":"柳莲二","年龄":15,"性别":"男","长相":"深紫色短发，戴眼镜，面容斯文","性格":"冷静理智、数据导向，话不多却一针见血","职业":"立海大附属中学网球社正选（三年级）","背景":"“三巨头”之一，负责数据分析与战术设计","特点":"擅长战术布置与记录，站在旁边笔记如山","概述":"以精密计算和战术眼光支撑团队，是队伍的智囊角色","文生图prompt":"full-bodyportraitofa15-year-oldJapaneseboywithshortdarkpurplehairandroundglasses,slimbuild,wearingwhitetennisuniformwithclipboardinhand,calmexpressionanalyzingdata,anime-style,highdetail"}},"精彩情节":[{"镜头1":{"人物行为":{"白兰·杰索":{"行为":"赤脚站在荒凉小岛沙滩，抬手遮阳，神情安然","对话":"“游戏失败了，就当重新开始吧……”"}},"场景":"荒岛孤岛沙滩，烈日当空，海风微拂","事件":"被囚十年后的白兰平静自省，却因世界意识召回少年身体","背景音乐":"神秘空灵的氛围电子音，若隐若现的合成弦乐旋律，营造时空错位感"}},{"镜头2":{"人物行为":{"白兰·杰索":{"行为":"醒来梳理白发，在镜前惊见少年身形，手指抚过镜面","对话":"“原来……我回到十二岁了？”"}},"场景":"整洁“新手村”般的公寓卧室，床尾网球包静置","事件":"白兰探索新身份，发现网球少年人设并激动购买装备","背景音乐":"轻快的钢琴与吉他节奏交织，带着初探新世界的明朗好奇"}},{"镜头3":{"人物行为":{"切原赤也":{"行为":"翻墙入校门矮墙，一跃而上，放声宣誓","对话":"“从今天起，我也是立海大附中一年级，要拿下全国第一的网球社！”"},"路人学长":{"行为":"侧目观看，表情惊讶","对话":"“你跑到那儿干嘛？快下来！”"}},"场景":"校门前人潮，清晨薄雾中光线柔和","事件":"切原首秀嚣张登场，惊动老师与学长，引出与白兰的对比","背景音乐":"节奏明快的摇滚鼓点，突显少年的热血与冲动"}},{"镜头4":{"人物行为":{"白兰·杰索":{"行为":"取下负重，用大空火焰加持发球，球速破210km/h","对话":"“就让我看看，这火焰与网球的极限吧！”"},"幸村精市":{"行为":"稳步后退，以柔和微笑回击所有来球","对话":"“精彩的发球，让我也发挥给你看吧。”"}},"场景":"立海网球场中心场，观众席灯光映照","事件":"白兰对阵部长幸村，火焰加成与精准回球交锋，最终0-3落败","背景音乐":"紧张激昂的管弦乐交响，节拍逐步攀升，比赛高潮迭起"}},{"镜头5":{"人物行为":{"白兰·杰索":{"行为":"提着整箱棉花糖夜归，遇见迷路切原，戏谑邀约同行","对话":"“切原同学这么晚不回家？跟我一起走吧，我家就近。”"},"切原赤也":{"行为":"抹乱发型，眼含感激地跟随","对话":"“你买了这么多糖？小赤也也要尝一颗么？”"}},"场景":"夜晚街头，路灯下超市与游戏厅门口的静谧街道","事件":"两位新人成为朋友，互通游戏与梦想，共享棉花糖与网球情谊","背景音乐":"温暖治愈的原声吉他独奏，带着甜蜜与友情的轻柔律动"}}]}
        return fake_res
    prompt_path= 'prompts/prompt_story_parse.txt'
    prompt_tmp=open(prompt_path).read()
    prompt=prompt_tmp.replace('aaaaa',story)
    raw_res=text2text(prompt,client,model_name=model_name)
    json_res=parse_json_response(raw_res)
    return json_res

# 阿拉伯数字转化为中文数字，支持1-9999
def num2chinese(num):
    if num < 1 or num > 9999:
        return "输入的数字超出范围"
    # 定义数字和单位的对应关系
    num_to_chinese = {
        1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九',
        10: '十', 20: '二十', 30: '三十', 40: '四十', 50: '五十', 60: '六十', 70: '七十', 80: '八十', 90: '九十',
        100: '百', 200: '两百', 300: '三百', 400: '四百', 500: '五百', 600: '六百', 700: '七百', 800: '八百', 900: '九百',
        1000: '千'
    }
    # 处理千位
    if num >= 1000:
        thousand = num // 1000
        remainder = num % 1000
        if remainder == 0:
            return num_to_chinese[thousand] + num_to_chinese[1000]
        else:
            return num_to_chinese[thousand] + num_to_chinese[1000] + num2chinese(remainder)
    elif num >= 100:
        hundred = num // 100
        remainder = num % 100
        if remainder == 0:
            return num_to_chinese[hundred] + num_to_chinese[100]
        else:
            return num_to_chinese[hundred] + num_to_chinese[100] + num2chinese(remainder)
    elif num >= 10:
        ten = num // 10
        remainder = num % 10
        if remainder == 0:
            return num_to_chinese[ten * 10]
        else:
            return num_to_chinese[ten * 10] + num_to_chinese[remainder]
    else:
        return num_to_chinese[num]

def try_decode(file_data, encodings):
    for encoding in encodings:
        try:
            return file_data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None
def decode_file_to_lines(raw_data):
    result = chardet.detect(raw_data)
    detected_encoding = result['encoding']
    # 尝试使用检测到的编码解码
    try:
        if detected_encoding is not None:
            if detected_encoding in ['gb2312', 'GB2312']:
                text = raw_data.decode('gb2312',errors='ignore')
            else:
                text = raw_data.decode(detected_encoding)
            lines = text.splitlines()
        else:
            # 如果检测到的编码失败，尝试其他常见编码
            encodings = ['utf-8', 'gbk', 'latin1', 'iso-8859-1']
            text = try_decode(raw_data, encodings)

            if text is not None:
                lines = text.splitlines()
            else:
                lines = []
    except Exception as e:
        print("文件解码失败: file encoding:{}, error:{}".format(detected_encoding, e))
        lines=[]
    return lines

def decode_file_path_to_lines(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    return decode_file_to_lines(raw_data)
# 将小说文本转化为按照章节划分的结构化json格式

def get_chapter_name(paragragh=[]):
    if len(paragragh)==0:
        return ""
    if len(paragragh[0]) < 20:
        chapter_name = paragragh[0]
        chapter_name = chapter_name.strip()
        if len(chapter_name) and chapter_name[0] in ['.', '。', ' ','·','、','*','-','：']:
            chapter_name = chapter_name[1:]
    else:
        chapter_name = ""
    return chapter_name
def structure_story(story_lines=[],story_name=''):
    structure_res={}
    # 章节名字
    chapter_index = 1
    paragragh=[]
    for line in story_lines:
        if len(line)<2:
            continue
        # 收集可能得章节名
        c_names=[f"第{chapter_index}章",f"第 {chapter_index} 章", f"Chapter{chapter_index}",f"Chapter {chapter_index}",
                 f"chapter{chapter_index}",f"chapter {chapter_index}","chapter {:0>3d}".format(chapter_index),
                 f"第[{chapter_index}]章",f"第 [{chapter_index}] 章",f"第{{{chapter_index}}}章",f"{chapter_index} ",
                 "第{:0>2d}章".format(chapter_index),f"{story_name}{chapter_index}",f"{chapter_index}.",
                 f"{chapter_index} ",f"{chapter_index}\n","第{:0>2d}节".format(chapter_index),
                 f"({chapter_index})"," {:0>3d}".format(chapter_index)]
        chinese_name=num2chinese(chapter_index)
        if chinese_name!="输入的数字超出范围":
            c_names.extend([f"第{chinese_name}章",f"第 {chinese_name} 章",f"{chinese_name} ",f"{chinese_name}、",
                            f"叙事{chinese_name}",f"{story_name}{chinese_name}",f"{chinese_name} ",f"{chinese_name}\n",
                            f"第{chinese_name}节",f"第{chinese_name}页"])
        # 特殊的章节符号
        c_names.extend(['☆、'])

        line_has_c_name=False
        for c_name in c_names:
            if line_has_c_name:
                break
            if c_name in line:
                line_has_c_name=True
                chapter_index+=1
                # 可能第几章混在一行的内容里了，需要将章节名前面的内容作为段落，后面的内容作为新的章节
                parts=line.split(c_name)
                if len(parts)==2:
                    if len(parts[0]):
                        paragragh.append(parts[0])
                    # 将lines合并成一个字符串
                    if len(paragragh):
                        chapter_name=get_chapter_name(paragragh)
                        if len(chapter_name):
                            paragragh=paragragh[1:]

                        paragragh_str="\n".join(paragragh)
                        structure_res[f"第{chapter_index-2}章"]={
                            'chapter_name':chapter_name,
                            'content':paragragh_str
                        }
                        paragragh=[]
                    if len(parts[1]):
                        paragragh.append(parts[1])
        if not line_has_c_name:
            paragragh.append(line)
    if len(paragragh):
        chapter_name = get_chapter_name(paragragh)
        if len(chapter_name):
            paragragh = paragragh[1:]
        # 将lines合并成一个字符串
        paragragh_str="\n".join(paragragh)
        structure_res[f"第{chapter_index-1}章"]={
            'chapter_name':chapter_name,
            'content':paragragh_str
        }
    return structure_res


def translate_a_paragragh(story="",target_language='英语',client=None,model_name=None,fake=False):
    fake_res={
        "英语":""
    }
    if fake:
        return fake_res.get(target_language,'')
    prompt_path= 'prompts/prompt_story_translate.txt'
    prompt_tmp=open(prompt_path).read()
    prompt=prompt_tmp.replace('aaaaa',story).replace('bbbbb',target_language)
    raw_res=text2text(prompt,client,model_name=model_name)
    if '翻译结果为:' in raw_res:
        res=raw_res.split("翻译结果为:")[-1]
    elif '翻译结果为：' in raw_res:
        res=raw_res.split("翻译结果为：")[-1]
    elif '翻译结果为' in raw_res:
        res=raw_res.split("翻译结果为")[-1]
    elif 'Translation result:' in raw_res:
        res=raw_res.split("Translation result:")[-1]
    elif 'Translation result：' in raw_res:
        res=raw_res.split("Translation result：")[-1]
    else:
        res=raw_res
    return res

