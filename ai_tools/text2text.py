from ai_tools.utils import *
import http.client

def text2text(prompt='',model_name=None,stream=False):
    if model_name is None:
        model_name='gpt-o3-mini'
    if model_name not in model_api_config.keys():
        valid_model_names=model_api_config.keys()
        raise ValueError(f"model_name {model_name} not in {valid_model_names}")
    api_key=model_api_config[model_name]['api_key']
    base_url=model_api_config[model_name]['base_url']
    full_model_name=model_api_config[model_name]['model_name']
    client_type=model_api_config[model_name]['client_type']
    # print("full_model_name:{},client_type:{}".format(full_model_name,client_type))
    if client_type=='openai':
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
    elif client_type=='apicore-http':
        conn = http.client.HTTPSConnection('api.apicore.ai')
        payload = json.dumps({
            "model": full_model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": stream
        })
        headers = {
            'Authorization': 'Bearer {}'.format(api_key),
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        data = res.read()
        if stream:
            return data
        else:
            try:
                res=data.decode("utf-8")
                res=json.loads(res)['choices'][0]['message']['content']
            except:
                res=""
            return res
