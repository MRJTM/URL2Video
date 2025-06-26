import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_tools.story_tools import *
from tqdm import tqdm
from openai import OpenAI

def run_one_case():
    test_file_path='tmp_materials/tmp_storys/首席混混总裁夫人.json'
    structure_res=json.loads(open(test_file_path,'r').read())
    story_content=''
    for chapter_name,chapter_res in structure_res.items():
        chapter_content=chapter_res['content']
        story_content+=chapter_content
    story_content=story_content[:200000]
    eval_res=story_quality_eval(story_content,model_name='deepseek-v3-apicore')
    print(eval_res)

def parse_test_file(fname,model_name='gpt',prompt_type='story_quality_eval'):
    src_dict = json.loads(open(fname, 'r').read())
    src_folder_path = os.path.dirname(fname)
    base_src_name = os.path.basename(fname)
    res_folder_path = os.path.join(src_folder_path, '{}_{}_tmp'.format(model_name, prompt_type))

    os.makedirs(res_folder_path, exist_ok=True)
    res_file_prefix = os.path.join(res_folder_path, '{}_{}_res'.format(model_name, prompt_type))
    pairs = []
    for story_name,v in tqdm(src_dict.items()):
        pair = v.copy()
        pair['story_name'] = story_name
        pairs.append(pair)
    return pairs, res_file_prefix

def do_story_quality_eval(pairs, res_file_prefix, process_idx, model_name='gpt', prompt_type='story_quality_eval'):
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
        if pair['story_name'] in res_dict:
            skip_num += 1
            continue
        structure_res_path = pair['structure_res_path']
        structure_res = json.loads(open(structure_res_path, 'r').read())
        content = ''
        for chapter_name, chapter_res in structure_res.items():
            chapter_content = chapter_res['content']
            content += chapter_content
        if len(content) == 0:
            fail_num += 1
            continue
        story_content = content[:200000]
        eval_res = story_quality_eval(story_content, model_name=model_name, prompt_type=prompt_type)
        if len(eval_res):
            res_dict[pair['story_name']] = pair.copy()
            res_dict[pair['story_name']]['quality_eval_res'] = eval_res
            success_num += 1
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