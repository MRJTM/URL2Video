import os
import json
import sys
import time
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_tools.text2text import text2text

def translate_a_paragragh(story="",character_info="",target_language='英语',model_name=None,fake=False):
    fake_res={
        "英语":""
    }
    if fake:
        return fake_res.get(target_language,'')
    prompt_path= 'prompts/prompt_story_translate.txt'
    prompt_tmp=open(prompt_path).read()
    prompt=prompt_tmp.replace('aaaaa',story).replace('bbbbb',character_info).replace('ccccc',target_language)
    raw_res=text2text(prompt,model_name=model_name)
    if '翻译结果:' in raw_res:
        res=raw_res.split("翻译结果:")[-1]
    elif '翻译结果：' in raw_res:
        res=raw_res.split("翻译结果：")[-1]
    elif '翻译结果为:' in raw_res:
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

def translate_a_chapter(content="",character_info="",model_name='gpt-o3-mini'):
    lines=content.split('\n')
    paragraph=[]
    # 每1000个字为一个段落
    total_char_num=0
    translate_res=[]
    all_success=True
    valid_line_num=0

    for line in lines:
        if len(line)<=4:
            continue
        valid_line_num+=1
        paragraph.append(line)
        total_char_num+=len(line)
        if total_char_num>=1000:
            paragraph_str="\n".join(paragraph)
            paragraph_translate_res=translate_a_paragragh(paragraph_str,character_info=character_info,model_name=model_name)

            if paragraph_translate_res=='':
                all_success=False
                break
            translate_res.append(paragraph_translate_res)
            paragraph=[]
            total_char_num=0
    if len(paragraph)>0 and all_success:
        paragraph_str = "\n".join(paragraph)
        paragraph_translate_res = translate_a_paragragh(paragraph_str,character_info=character_info,model_name=model_name)
        if paragraph_translate_res == '':
            all_success = False
        translate_res.append(paragraph_translate_res)

    if all_success:
        translate_res_str="\n".join(translate_res)
    else:
        translate_res_str=""

    return valid_line_num,translate_res_str
def run_one_case():
    test_file_path='../../../data/test_case/story_20250606/structure_res/大雪无痕.json'
    structure_res=json.loads(open(test_file_path,'r').read())
    content=structure_res['第1章']['content']
    character_info_path='../../../data/test_case/story_20250606/deepseek-v3-apicore_story_character_rename_res/大雪无痕.json'
    character_info=json.loads(open(character_info_path,'r').read())
    character_info_str=json.dumps(character_info,ensure_ascii=False)
    model_name='gemini-2.5-flash-lite-my'
    # model_name='deepseek-v3-apicore-my'
    start_time=time.time()
    translate_res=translate_a_chapter(content,character_info_str,model_name=model_name)
    end_time=time.time()
    print('time cost:{}'.format(end_time-start_time))
    print(translate_res)

def parse_test_file(fname,model_name='gpt',prompt_type='story_translate'):
    src_dict = json.loads(open(fname, 'r').read())
    src_folder_path = os.path.dirname(fname)
    base_src_name = os.path.basename(fname)
    res_folder_path = os.path.join(src_folder_path, '{}_{}_tmp'.format(model_name,prompt_type))

    os.makedirs(res_folder_path, exist_ok=True)
    res_file_prefix = os.path.join(res_folder_path, base_src_name.replace('.json', '_{}_{}'.format(model_name,prompt_type)))
    pairs = []
    for story_name,v in tqdm(src_dict.items()):
        structure_res_path=v['structure_res_path']
        character_rename_path=os.path.join(src_folder_path,'deepseek-v3-apicore_story_character_rename_res/{}.json'.format(story_name))
        if not os.path.exists(character_rename_path):
            continue
        structure_res=json.loads(open(structure_res_path,'r').read())
        for chapter_name,chapter_res in structure_res.items():
            pair = v.copy()
            pair['story_name'] = story_name
            pair['chapter_name']=chapter_name
            pair['content']=chapter_res['content']
            character_rename_res=json.loads(open(character_rename_path,'r').read())
            character_rename_res_str=json.dumps(character_rename_res,ensure_ascii=False)
            pair['character_rename_res']=character_rename_res_str
            pairs.append(pair)
    return pairs, res_file_prefix

def do_story_translate(pairs, res_file_prefix, process_idx, model_name='gpt',prompt_type='story_translate'):
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
        character_rename_res=pair['character_rename_res']
        valid_line_num,translate_res=translate_a_chapter(content,character_rename_res,model_name)
        if len(translate_res)>0 or valid_line_num==0:
            success_num += 1
            res_dict[key] = {'translate_res':translate_res}
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