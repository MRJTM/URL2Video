import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tqdm import tqdm
import chardet

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

def run_one_case():
    test_file_path='../../data/中文女频2023-24/raw_story/年代文合集/八零年代锦鲤美人（完结）.txt'
    all_lines=decode_file_path_to_lines(test_file_path)
    structure_res=structure_story(all_lines)
    dst_file_path='../../data/中文女频2023-24/structure_res/八零年代锦鲤美人（完结）.json'
    with open(dst_file_path,'w',encoding='utf-8') as f:
        json.dump(structure_res,f,ensure_ascii=False,indent=4)

def parse_test_file(fname):
    src_dict = json.loads(open(fname, 'r').read())
    src_folder_path = os.path.dirname(fname)
    base_src_name = os.path.basename(fname)
    res_folder_path = os.path.join(src_folder_path, 'story_structure_res')

    os.makedirs(res_folder_path, exist_ok=True)
    res_file_prefix = os.path.join(res_folder_path, base_src_name.replace('.json', 'structure_res'))
    pairs = []
    for story_name in tqdm(src_dict.keys()):
        pair = src_dict[story_name].copy()
        pair['story_name'] = story_name
        pairs.append(pair)
    return pairs, res_file_prefix

def do_story_structure(pairs, res_file_prefix, process_idx):
    if process_idx >= 0:
        res_file_path = res_file_prefix + '_{}.json'.format(process_idx)
    else:
        res_file_path = res_file_prefix + '.json'
    if os.path.exists(res_file_path):
        res_dict = json.loads(open(res_file_path, 'r').read())
    else:
        res_dict = {}

    success_num = 0
    decode_fail_num = 0
    char_too_less_num = 0
    total_num = 0
    skip_num = 0
    total_word_num=0
    for pair in tqdm(pairs, desc='worker {} Processing'.format(process_idx)):
        total_num += 1
        if pair['story_name'] in res_dict and os.path.exists(res_dict[pair['story_name']]['structure_res_path']):
            skip_num += 1
            continue

        raw_file_path=pair['路径']
        all_lines = decode_file_path_to_lines(raw_file_path)
        structure_res = structure_story(all_lines,pair['story_name'])
        if len(structure_res)>0:
            if len(structure_res)>=5:
                total_word_num+=sum([len(v['content']) for v in structure_res.values()])
                res_folder_path = raw_file_path.split('raw_story')[0] + 'structure_res'
                structure_file_path = os.path.join(res_folder_path, pair['story_name'] + '.json')
                json_str = json.dumps(structure_res, ensure_ascii=False, indent=4)
                with open(structure_file_path, 'w') as f:
                    f.write(json_str)
                if os.path.exists(structure_file_path):
                    success_num += 1
                    res_dict[pair['story_name']] = pair.copy()
                    res_dict[pair['story_name']]['structure_res_path'] = structure_file_path
                    if success_num % 10 == 0:
                        json_str = json.dumps(res_dict, ensure_ascii=False, indent=4)
                        with open(res_file_path, 'w') as f:
                            f.write(json_str)
                        print("\nworker {}: total:{}, skip:{}, success:{}, decode_fail:{}, char_too_less:{},total_word_num:{}".format(process_idx, total_num, skip_num,
                                                                                       success_num, decode_fail_num,char_too_less_num,total_word_num))
            else:
                if len(pair['二级类目']):
                    level_name='{}/{}/{}'.format(pair['一级类目'],pair['二级类目'],pair['story_name'])
                else:
                    level_name='{}/{}'.format(pair['一级类目'],pair['story_name'])
                print("{} 章节太少，只有{}章".format(level_name, len(structure_res)))
                char_too_less_num += 1
        else:
            decode_fail_num += 1
            if len(structure_res)>0:
                print("{} 章节太少，只有{}章".format(pair["story_name"],len(structure_res)))

    json_str = json.dumps(res_dict, ensure_ascii=False, indent=4)
    with open(res_file_path, 'w') as f:
        f.write(json_str)
    print("\nworker {}: total:{}, skip:{}, success:{}, decode_fail:{}, char_too_less:{} total_word_num:{}".format(process_idx, total_num, skip_num, success_num,
                                                                       decode_fail_num,char_too_less_num,total_word_num))
    return res_dict


if __name__ == '__main__':
    run_one_case()