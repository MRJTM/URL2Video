from ai_tools.utils import *

def call_multi_model_gpt(prompt,image):
    if image.startswith("http"):
        image_url=image
    else:
        image_url=f"data:image/jpeg;base64,{image}"
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            },
        ],
    )
    try:
        res=completion.choices[0].message.content
    except:
        res=""
    return res

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
