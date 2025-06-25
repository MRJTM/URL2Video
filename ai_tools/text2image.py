import os
# 增加..路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_tools.utils import *

def text2image(prompt='',client=None,base_url=None,api_key=None,model_name="gpt-image-1",size='512x512',filename="demo.png"):
    if not os.path.exists('tmp_materials/tmp_images'):
        os.makedirs('tmp_materials/tmp_images')
    res_img_path=os.path.join('tmp_materials/tmp_images', filename)
    if os.path.exists(res_img_path):
        return res_img_path

    if client is None:
        client = OpenAI(api_key=api_key,base_url=base_url)

    if model_name in ["gpt-image-1"]:
        image_response = client.images.generate(
            model=model_name,
            prompt=prompt,
            size=size,
        )
        image_base64=image_response.data[0].b64_json
        print("image_base64:", image_base64)
        image_bytes = base64.b64decode(image_base64)
        img_path=image_bytes_to_local_img(image_bytes,filename)
    elif model_name in ["dall-e-3","dall-e-2"]:
        if size not in ["1024x1024","1024x1792","1792x1024"]:
            size="1024x1024"
        image_response = client.images.generate(
            model=model_name,
            prompt=prompt,
            size="1024x1024",
        )
        image_url=image_response.data[0].url
        img_path=download_image(image_url,filename)
    else:
        img_path=None

    return img_path

def image_bytes_to_local_img(image_bytes,filename):
    local_path = os.path.join('../tmp_materials/tmp_images', filename)
    with open(local_path, "wb") as f:
        f.write(image_bytes)
    return local_path
def url_to_np_array(image_url):
    try:
        # 发送 HTTP 请求下载图片
        response = requests.get(image_url)
        response.raise_for_status()  # 确保请求成功

        # 使用 BytesIO 将下载的图片数据转换为可读的文件对象
        image_data = BytesIO(response.content)

        # 使用 PIL 打开图片
        image = Image.open(image_data)

        # 将图片转换为 NumPy 数组
        np_array = np.array(image)

        return np_array
    except Exception as e:
        print(f"Error: {e}")
        return None

# 将图片下载到本地，并返回本地路径
def download_image(image_url,img_name=None):
    # 从 URL 中提取文件名
    if img_name:
        filename = img_name
    else:
        if '?' in image_url:
            image_url = image_url.split('?')[0]
        filename = image_url.split("/")[-1]
    local_path = os.path.join('tmp_materials/tmp_images', filename)
    if not os.path.exists('tmp_materials/tmp_images'):
        os.makedirs('tmp_materials/tmp_images')
    try:
        # 下载图片
        if not os.path.exists(local_path):
            wget.download(image_url, local_path)
        return local_path
    except Exception as e:
        print(f"Error: {e}")
        try:
            cmd=f'wget {image_url} -O {local_path}'
            os.system(cmd)
            return local_path
        except Exception as e:
            return None

if __name__ == '__main__':
    OPENAI_API_KEY = "sk-L1PKva8uq22H0aU3947e5320146345E6A70d68CbCa69D02f"
    BASE_URL = "https://api.132999.xyz/v1"
    client = OpenAI(api_key=OPENAI_API_KEY,base_url=BASE_URL)

    prompt="a photo of a cat"
    img_path=text2image(prompt,client,model_name="dall-e-3", size='1024x1792')
    print(img_path)