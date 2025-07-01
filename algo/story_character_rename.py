"""
将小说中的中文角色名替换为合适的英文名称。
"""

import os
import json
import sys
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_tools.text2text import text2text
from ai_tools.utils import parse_json_response

def rename_character(character_info={},model_name='gpt',prompt_type='rename_character'):
    prompt_path='prompts/prompt_{}.txt'.format(prompt_type)
    prompt_tmp=open(prompt_path,'r').read()
    his_charactor_str=json.dumps(character_info,ensure_ascii=False,indent=4)
    prompt=prompt_tmp.replace('aaaaa',his_charactor_str)
    res=text2text(prompt,model_name=model_name)
    res=parse_json_response(res,skip_blank=False)
    return res

def run_one_case():
    test_file_path='../../data/中文女频2023-24/deepseek-v3-apicore_story_character_parse_res/冷情总裁的退婚新娘_final.json'
    charactor_res=json.loads(open(test_file_path,'r').read())
    model_name='deepseek-v3-apicore-my'
    prompt_type='story_character_rename'
    res_folder_path='../../data/中文女频2023-24/{}_{}_res'.format(model_name,prompt_type)
    os.makedirs(res_folder_path,exist_ok=True)
    story_name=test_file_path.split('/')[-1].split('.')[0]
    res_file_prefix=res_folder_path+'/'+story_name
    print("res_file_prefix:",res_file_prefix)
    new_charactor_res=rename_character(charactor_res,model_name=model_name,prompt_type=prompt_type)
    print("new_charactor_res:",new_charactor_res)
    dst_file_path=res_file_prefix+'.json'
    with open(dst_file_path,'w') as f:
        json.dump(new_charactor_res,f,ensure_ascii=False,indent=4)

def parse_test_file(fname,model_name='gpt',prompt_type='story_character_rename'):
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

def do_story_character_rename(pairs, res_file_prefix, process_idx, model_name='gpt', prompt_type='story_character_rename'):
    if process_idx >= 0:
        res_file_path = res_file_prefix + '_{}.json'.format(process_idx)
    else:
        res_file_path = res_file_prefix + '.json'
    if os.path.exists(res_file_path):
        res_dict = json.loads(open(res_file_path, 'r').read())
    else:
        res_dict = {}
    res_folder_path=os.path.dirname(res_file_prefix.replace('tmp','res'))
    os.makedirs(res_folder_path,exist_ok=True)
    success_num = 0
    fail_num = 0
    total_num = 0
    skip_num = 0
    for pair in tqdm(pairs):
        story_name = pair['story_name']
        if story_name in res_dict:
            skip_num += 1
            continue
        try:
            raw_charactor_res_path = pair['charactor_res_path']
            raw_charactor_res = json.loads(open(raw_charactor_res_path, 'r').read())
            new_charactor_res = rename_character(raw_charactor_res, model_name=model_name, prompt_type=prompt_type)
            # 检查前后人物是否一致
            character_consistent = True
            for char_name in raw_charactor_res.keys():
                if char_name not in new_charactor_res.keys():
                    character_consistent = False
                    break
            for char_name in new_charactor_res.keys():
                if char_name not in raw_charactor_res.keys():
                    character_consistent = False
                    break
            if character_consistent:
                # 保存结果
                dst_file_path = res_folder_path + '/' + story_name + '.json'
                with open(dst_file_path, 'w') as f:
                    json.dump(new_charactor_res, f, ensure_ascii=False, indent=4)
                res_dict[story_name] = pair.copy()
                res_dict[story_name]['charactor_rename_path'] = dst_file_path
                success_num += 1
                if success_num % 3 == 0:
                    # 保存中间结果
                    json_str = json.dumps(res_dict, ensure_ascii=False, indent=4)
                    with open(res_file_path, 'w') as f:
                        f.write(json_str)
                    print("\nworker {}: total:{}, skip:{}, success:{}, fail:{}".format(process_idx, total_num, skip_num,
                                                                                       success_num, fail_num))

            else:
                fail_num += 1
        except Exception as e:
            print("process {} failed, story_name:{}, error:{}".format(process_idx, story_name, str(e)))
            fail_num += 1

    json_str = json.dumps(res_dict, ensure_ascii=False, indent=4)
    with open(res_file_path, 'w') as f:
        f.write(json_str)
    print("\nworker {}: total:{}, skip:{}, success:{}, fail:{}".format(process_idx, total_num, skip_num, success_num, fail_num))

    return success_num, fail_num, total_num, skip_num



if __name__ == '__main__':
    run_one_case()