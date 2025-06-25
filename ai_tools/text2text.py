from ai_tools.utils import *

def text2text(prompt='',model_name=None,stream=False):
    if model_name is None:
        model_name='gpt-o3-mini'
    if model_name not in model_api_config.keys():
        valid_model_names=model_api_config.keys()
        raise ValueError(f"model_name {model_name} not in {valid_model_names}")
    api_key=model_api_config[model_name]['api_key']
    base_url=model_api_config[model_name]['base_url']
    full_model_name=model_api_config[model_name]['model_name']
    client = OpenAI(api_key=api_key,base_url=base_url)

    res = client.chat.completions.create(
        model= full_model_name,
        messages=[
            {"role": 'user', "content": prompt}
        ],
        stream= stream
    )
    if stream:
        return res
    else:
        try:
            res=res.choices[0].message.content
        except:
            res=""
        return res
