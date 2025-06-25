import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_tools.story_tools import *
from tqdm import tqdm

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