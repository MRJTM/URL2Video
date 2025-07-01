import os
import sys
import json
from multiprocessing import Pool
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algo.algo_config import algo_configs
from algo import story_structure,story_translate,story_quality_eval
from algo import story_character_parse,story_character_rename
import random


def parse_test_file(test_file_path, algo_name, test_num=-1):
    if algo_name == "story_structure":
        pairs, res_file_prefix = story_structure.parse_test_file(test_file_path)
    elif algo_name == "story_translate":
        pairs, res_file_prefix = story_translate.parse_test_file(test_file_path, algo_configs[algo_name]['model']),
    elif algo_name == "story_quality_eval":
        pairs, res_file_prefix = story_quality_eval.parse_test_file(test_file_path, algo_configs[algo_name]['model'],
                                                                   algo_configs[algo_name]['prompt_type'])
    elif algo_name == "story_character_parse":
        pairs, res_file_prefix = story_character_parse.parse_test_file(test_file_path, algo_configs[algo_name]['model'],
                                                                   algo_configs[algo_name]['prompt_type'])
    elif algo_name == "story_character_rename":
        pairs, res_file_prefix = story_character_rename.parse_test_file(test_file_path, algo_configs[algo_name]['model'],
                                                                   algo_configs[algo_name]['prompt_type'])
    else:
        raise NotImplementedError
    pairs = pairs[:test_num] if test_num > 0 else pairs
    return pairs, res_file_prefix


def process(process_idx, pairs, res_file_prefix, algo_name):
    if algo_name == "story_structure":
        res_dict = story_structure.do_story_structure(pairs,res_file_prefix, process_idx)
    elif algo_name == "story_translate":
        res_dict = story_translate.do_story_translate(pairs, res_file_prefix, process_idx,
                                                       algo_configs[algo_name]['model'])
    elif algo_name == "story_quality_eval":
        res_dict = story_quality_eval.do_story_quality_eval(pairs, res_file_prefix, process_idx,
                                                            algo_configs[algo_name]['model'],algo_configs[algo_name]['prompt_type'])
    elif algo_name == "story_character_parse":
        res_dict = story_character_parse.do_story_character_parse(pairs, res_file_prefix, process_idx,
                                                            algo_configs[algo_name]['model'],algo_configs[algo_name]['prompt_type'])
    elif algo_name == "story_character_rename":
        res_dict = story_character_rename.do_story_character_rename(pairs, res_file_prefix, process_idx,
                                                            algo_configs[algo_name]['model'],algo_configs[algo_name]['prompt_type'])
    else:
        raise NotImplementedError

    return res_dict


if __name__ == '__main__':
    # algo_name = "story_structure"
    # algo_name = "story_translate"
    # algo_name = "story_quality_eval"
    algo_name = "story_character_parse"
    # algo_name = "story_character_rename"
    num_process = 2
    test_num = 2

    # data prepare,解读测试文件，生成pairs的list
    # test_file_path = "../../data/中文女频2023-24/story.json"
    test_file_path = "../../data/中文女频2023-24/structure_res.json"

    pairs, res_file_prefix = parse_test_file(test_file_path, algo_name, test_num)
    print("pair_num:", len(pairs))
    print("res_file_prefix:", res_file_prefix)

    # 对list进行拆解，分成若干批，进行多进程处理，每个进程写一个文件
    batch_size = len(pairs) // num_process
    batches = [pairs[i:i + batch_size] for i in range(0, len(pairs), batch_size)]
    print("batch_size for each worker:", batch_size)
    pp = Pool(num_process)
    for i in range(num_process):
        pp.apply_async(process, args=(i, batches[i], res_file_prefix, algo_name))
    pp.close()
    pp.join()

    # 每个进程产生的文件进行合并
    res_dict = {}
    for i in range(num_process):
        res_file_path = res_file_prefix + "_" + str(i) + ".json"
        if os.path.exists(res_file_path):
            with open(res_file_path, 'r') as f:
                res_dict.update(json.loads(f.read()))
    # 保存结果
    with open(res_file_prefix + ".json", 'w') as f:
        f.write(json.dumps(res_dict, ensure_ascii=False, indent=1))

    print("total pairs: {}, success pairs: {}".format(len(pairs), len(res_dict)))

    # 删除临时文件
    # for i in range(num_process):
    #     res_file_path = res_file_prefix + "_" + str(i) + ".json"
    #     if os.path.exists(res_file_path):
    #         os.remove(res_file_path)