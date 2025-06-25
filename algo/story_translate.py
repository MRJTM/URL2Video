import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_tools.text2text import *
from tqdm import tqdm
from openai import OpenAI

def translate_a_chapter(content="",model='gpt'):
    lines=content.split('\n')
    paragraph=[]
    # 每1000个字为一个段落
    total_char_num=0
    translate_res=[]
    all_success=True
    valid_line_num=0
    if 'deepseek' in model:
        model_name = 'deepseek-chat'
    else:
        model_name = None

    for line in lines:
        if len(line)<=4:
            continue
        valid_line_num+=1
        paragraph.append(line)
        total_char_num+=len(line)
        if total_char_num>=1000:
            paragraph_str='\n'.join(paragraph)
            paragraph_translate_res=translate_a_paragragh(paragraph_str,model_name=model_name)

            if paragraph_translate_res=='':
                all_success=False
                break
            translate_res.append(paragraph_translate_res)
            paragraph=[]
            total_char_num=0
    if len(paragraph)>0 and all_success:
        paragraph_str = '\n'.join(paragraph)
        paragraph_translate_res = translate_a_paragragh(paragraph_str,model_name=model_name)
        if paragraph_translate_res == '':
            all_success = False
        translate_res.append(paragraph_translate_res)

    if all_success:
        translate_res_str='\n'.join(translate_res)
    else:
        translate_res_str=''

    return valid_line_num,translate_res_str
def run_one_case():
    test_file_path='tmp_materials/tmp_storys/首席混混总裁夫人.json'
    structure_res=json.loads(open(test_file_path,'r').read())
    content=structure_res['第4章']['content']
    translate_res=translate_a_chapter(content)
    print(translate_res)

def parse_test_file(fname,model_name='gpt'):
    src_dict = json.loads(open(fname, 'r').read())
    src_folder_path = os.path.dirname(fname)
    base_src_name = os.path.basename(fname)
    res_folder_path = os.path.join(src_folder_path, '{}_story_translate_res'.format(model_name))

    os.makedirs(res_folder_path, exist_ok=True)
    res_file_prefix = os.path.join(res_folder_path, base_src_name.replace('.json', '_{}_translate_res'.format(model_name)))
    pairs = []
    for story_name,v in tqdm(src_dict.items()):
        structure_res_path=v['structure_res_path']
        structure_res=json.loads(open(structure_res_path,'r').read())
        for chapter_name,chapter_res in structure_res.items():
            pair = v.copy()
            pair['story_name'] = story_name
            pair['chapter_name']=chapter_name
            pair['content']=chapter_res['content']
            pairs.append(pair)
    return pairs, res_file_prefix

def do_story_translate(pairs, res_file_prefix, process_idx, model_name='gpt'):
    if process_idx >= 0:
        res_file_path = res_file_prefix + '_{}.json'.format(process_idx)
    else:
        res_file_path = res_file_prefix + '.json'
    if os.path.exists(res_file_path):
        res_dict = json.loads(open(res_file_path, 'r').read())
    else:
        res_dict = {}

    success_num = 0
    fail_num = 0
    total_num = 0
    skip_num = 0
    for pair in tqdm(pairs, desc='worker {} Processing'.format(process_idx)):
        total_num += 1
        key='{}/{}'.format(pair['story_name'],pair['chapter_name'])
        if key in res_dict:
            skip_num += 1
            continue
        content=pair['content']
        valid_line_num,translate_res=translate_a_chapter(content,model_name)
        if len(translate_res)>0 or valid_line_num==0:
            success_num += 1
            res_dict[key] = pair.copy()
            res_dict[key]['translate_res'] = translate_res
            if success_num % 10 == 0:
                json_str = json.dumps(res_dict, ensure_ascii=False, indent=4)
                with open(res_file_path, 'w') as f:
                    f.write(json_str)
                print("\nworker {}: total:{}, skip:{}, success:{}, fail:{}".format(process_idx, total_num, skip_num,
                                                                                       success_num, fail_num))
        else:
            fail_num += 1

    json_str = json.dumps(res_dict, ensure_ascii=False, indent=4)
    with open(res_file_path, 'w') as f:
        f.write(json_str)
    print("\nworker {}: total:{}, skip:{}, success:{}, fail:{}".format(process_idx, total_num, skip_num,
                                                                           success_num, fail_num))
    return res_dict


if __name__ == '__main__':
    run_one_case()