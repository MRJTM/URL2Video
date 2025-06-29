import os
import json
import sys
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_tools.text2text import text2text
from ai_tools.utils import parse_json_response

def get_charactor(story_content,history_charactor={},model_name='gpt',prompt_type='charactor_parse'):
    prompt_path='prompts/prompt_{}.txt'.format(prompt_type)
    prompt_tmp=open(prompt_path,'r').read()
    his_charactor_str=json.dumps(history_charactor,ensure_ascii=False,indent=4)
    prompt=prompt_tmp.replace('aaaaa',story_content).replace('bbbbb',his_charactor_str)
    res=text2text(prompt,model_name=model_name)
    charactor_res=parse_json_response(res)
    return charactor_res

def get_charactor_for_a_story(res_file_prefix,structure_res,model_name='gpt',prompt_type='charactor_parse',debug=False):
    story_content = ''
    charactor_res = {}
    part=1
    all_success=True
    process_chapter_num=0
    for chapter_name, chapter_res in structure_res.items():
        chapter_content = chapter_res['content']
        story_content += chapter_content
        process_chapter_num+=1
        if len(story_content) > 60000 or process_chapter_num==len(structure_res):
            if debug:
                print("processing part:{}".format(part))
                print("before process character_num:{}, character_names:{}".format(len(charactor_res),list(charactor_res.keys())))

            # 保存中间结果
            dst_file_path=res_file_prefix+'_part_{}.json'.format(part)
            if os.path.exists(dst_file_path):
                charactor_res = json.loads(open(dst_file_path, 'r').read())
            else:
                new_charactor_res = get_charactor(story_content, charactor_res, model_name=model_name,
                                            prompt_type=prompt_type)
                if len(new_charactor_res):
                    charactor_res.update(new_charactor_res)
                    json_str = json.dumps(charactor_res, ensure_ascii=False, indent=4)
                    with open(dst_file_path, 'w') as f:
                        f.write(json_str)
                else:
                    print("update charactor failed，after process character_num:{},character_names:{}".format(len(new_charactor_res),
                                                                                     list(new_charactor_res.keys())))
                    break

            part+=1
            story_content = ''

            if debug:
                print("after process character_num:{},character_names:{}".format(len(charactor_res),list(charactor_res.keys())))
    # 保存最终结果
    if all_success and len(charactor_res):
        dst_file_path = res_file_prefix + '_final.json'
        json_str = json.dumps(charactor_res, ensure_ascii=False, indent=4)
        with open(dst_file_path, 'w') as f:
            f.write(json_str)

    return all_success,charactor_res

def run_one_case():
    # test_file_path='tmp_materials/tmp_storys/首席混混总裁夫人.json'
    test_file_path='../../data/中文女频2023-24/structure_res/八零年代锦鲤美人（完结）.json'
    structure_res=json.loads(open(test_file_path,'r').read())
    model_name='deepseek-v3-apicore-my'
    prompt_type='story_character_parse'
    res_folder_path='../../data/中文女频2023-24/{}_{}_res'.format(model_name,prompt_type)
    os.makedirs(res_folder_path,exist_ok=True)
    story_name=test_file_path.split('/')[-1].split('.')[0]
    res_file_prefix=res_folder_path+'/'+story_name
    print("res_file_prefix:",res_file_prefix)
    all_success,charactor_res=get_charactor_for_a_story(res_file_prefix,structure_res,model_name=model_name,
                                                        prompt_type=prompt_type,debug=True)
    print("all_success:",all_success)
    print("charactor_res:",charactor_res)

def parse_test_file(fname,model_name='gpt',prompt_type='story_character_parse'):
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

def do_story_character_parse(pairs, res_file_prefix, process_idx, model_name='gpt', prompt_type='story_character_parse'):
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
    for pair in tqdm(pairs, desc='worker {} Processing'.format(process_idx)):
        total_num += 1
        if pair['story_name'] in res_dict:
            skip_num += 1
            continue
        structure_res_path = pair['structure_res_path']
        structure_res = json.loads(open(structure_res_path, 'r').read())
        res_prefix=res_folder_path+'/'+pair['story_name']
        all_success, charactor_res = get_charactor_for_a_story(res_prefix, structure_res, model_name=model_name,
                                                              prompt_type=prompt_type, debug=False)
        if all_success:
            pair['charactor_res_path'] = res_prefix + '_final.json'
            success_num += 1
            if success_num % 3 == 0:
                json_str = json.dumps(res_dict, ensure_ascii=False, indent=4)
                with open(res_file_path, 'w') as f:
                    f.write(json_str)
                print("\nworker {}: total:{}, skip:{}, success:{}, fail:{}".format(process_idx, total_num, skip_num,success_num, fail_num))
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