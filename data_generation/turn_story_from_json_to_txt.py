import json
import os
import sys
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def json_to_txt(json_file_path):
    json_folder_path = os.path.dirname(json_file_path)
    json_folder_name = os.path.basename(json_folder_path)
    root_folder_path = os.path.dirname(json_folder_path)
    txt_folder_path = os.path.join(root_folder_path, json_folder_name + '_txt')
    json_file_name = os.path.basename(json_file_path)
    txt_file_name = os.path.splitext(json_file_name)[0] + '.txt'
    if not os.path.exists(txt_folder_path):
        os.makedirs(txt_folder_path)

    json_data=json.load(open(json_file_path,'r'))
    dst_file_path=os.path.join(txt_folder_path,txt_file_name)
    dst_file=open(dst_file_path,'w',encoding='utf-8')
    for chapter_name, chapter_info in json_data.items():
        if len(chapter_info['chapter_name']):
            full_chapter_name=f'\n\n{chapter_name} {chapter_info["chapter_name"]}\n'
        else:
            full_chapter_name=f'\n\n{chapter_name}\n'
        dst_file.write(full_chapter_name)
        chapter_lines=chapter_info['content'].split('\n')
        for line in chapter_lines:
            if len(line)<=2:
                continue
            if line[:2]!='\t':
                line='\t'+line
            dst_file.write(line+'\n')
    dst_file.close()

def json_to_txt_all(json_folder_path):
    json_files = [f for f in os.listdir(json_folder_path) if f.endswith('.json')]
    for json_file in tqdm(json_files):
        json_file_path = os.path.join(json_folder_path, json_file)
        json_to_txt(json_file_path)

if __name__=='__main__':
    # json_file_path='../../data/中文女频2023-24/structure_res/八零年代锦鲤美人（完结）.json'
    # json_to_txt(json_file_path)
    json_folder_path='../../data/中文女频2023-24/deepseek-v3-apicore_story_translate_res_merged'
    json_to_txt_all(json_folder_path)
