"""
解析小说文件夹，获取一个文件夹组织的demo
文件夹可能从根目录开始最多往下2层，即
根目录/一级类目/二级类目/小说名.txt
或者
根目录/一级类目/小说名.txt
输出结果按照json格式汇总
{
    "小说名":{
        "路径":"根目录/一级类目/二级类目/小说名.txt",
        "一级类目":"一级类目",
        "二级类目":"二级类目"
    }
}
"""
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_statistic_utils import *

def parse_story_folder(story_folder):
    # root folder为story_folder的上一级
    root_folder=os.path.dirname(story_folder)
    print("root_folder:",root_folder,"\n")
    story_dict={}
    file_type_count={}
    class_level1_count={}
    for root,dirs,files in os.walk(story_folder):
        for file in files:
            # 基于文件名后缀统计文件类型
            file_type = file.split('.')[-1]
            if file_type not in file_type_count:
                file_type_count[file_type] = 0
            file_type_count[file_type] += 1

            if file.endswith('.txt'):
                file_path=os.path.join(root,file)
                story_name=file[:-4]
                # 判断文件路径是否包含二级类目，因为root本身可能包含..,所以仅判断倒数第三个是否为一级类目
                tmp_root=root.replace(story_folder,'')
                if tmp_root[0]=='/':
                    tmp_root=tmp_root[1:]
                # 判断是否包含二级类目
                if len(tmp_root.split('/'))>1:
                    second_category=tmp_root.split('/')[1]
                    first_category=tmp_root.split('/')[0]
                else:
                    second_category=''
                    first_category=tmp_root.split('/')[0]

                story_dict[story_name] = {
                    "路径": file_path,
                    "一级类目": first_category,
                    "二级类目": second_category
                }
                # 基于一级类目统计文件数量
                if first_category not in class_level1_count:
                    class_level1_count[first_category]=0
                class_level1_count[first_category]+=1

    # 打印统计结果
    print_sorted_dict_with_percentage(class_level1_count,"一级类目文件数量统计","一级类目","文件数量")
    print_sorted_dict_with_percentage(file_type_count,"文件类型统计","文件类型","文件数量")

    # 保存json文件到root_folder
    dst_file_path=os.path.join(root_folder,'story.json')
    print("saved to:",dst_file_path,"\n")
    with open(dst_file_path,'w',encoding='utf-8') as f:
        json.dump(story_dict,f,ensure_ascii=False,indent=4)

    return story_dict,file_type_count

if __name__=="__main__":
    root_folder='../../data/中文女频2023-24/raw_story'
    story_dict,file_type_count=parse_story_folder(root_folder)

