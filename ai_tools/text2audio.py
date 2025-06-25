from utils import *
def call_gpt_text2audio_gen(text,speech_file_name,model_name='tts',voice='echo',base_url=None,api_key=None):
    speech_folder_path= '../tmp_materials/tmp_audios'
    if not os.path.exists(speech_folder_path):
        os.makedirs(speech_folder_path)
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    response = client.audio.speech.create(
        model = model_name,
        voice = voice,
        input = text
    )
    audio_file_path=os.path.join(speech_folder_path,'{}.mp3'.format(speech_file_name))
    response.stream_to_file(audio_file_path)
    if os.path.exists(audio_file_path):
        return audio_file_path
    else:
        return None