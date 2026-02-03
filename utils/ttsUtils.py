import edge_tts
import os
import hashlib
from utils import textUtils
from edge_tts import VoicesManager


# from TTS.api import TTS

def sanitize_filename(file_path, max_path_length=260):
    """
    处理文件名，确保不超过Windows系统路径长度限制（MAX_PATH = 260字符）
    
    Args:
        file_path (str): 完整文件路径
        max_path_length (int): 完整路径的最大长度，默认260字符（Windows MAX_PATH）
    
    Returns:
        str: 处理后的文件路径
    """
    # 分离目录、文件名和扩展名
    directory = os.path.dirname(file_path)
    filename_with_ext = os.path.basename(file_path)
    
    # 分离文件名和扩展名
    if '.' in filename_with_ext:
        name_part, ext = os.path.splitext(filename_with_ext)
    else:
        name_part = filename_with_ext
        ext = ''
    
    # 计算目录路径长度（加上路径分隔符）
    dir_length = len(directory) + 1 if directory else 0
    ext_length = len(ext)
    
    # 计算可用的文件名长度（留10字符的安全余量）
    available_length = max_path_length - dir_length - ext_length - 10
    # 确保至少保留一些字符
    available_length = max(available_length, 50)
    
    # 如果文件名部分不超过限制，直接返回
    if len(name_part) <= available_length:
        return file_path
    
    # 文件名过长，需要截断
    # 策略：保留前80%和后20%的内容，中间用省略号
    front_length = int(available_length * 0.8)
    back_length = available_length - front_length - 3  # 减去省略号的长度
    
    # 确保 back_length 不为负数
    if back_length < 0:
        back_length = 0
    
    # 如果可用长度太短，使用哈希值策略
    if available_length < 50:
        # 使用文件名的哈希值作为后缀
        hash_suffix = hashlib.md5(name_part.encode('utf-8')).hexdigest()[:8]
        # 保留尽可能多的原始文件名，但确保总长度不超过限制
        name_available = available_length - 9  # 减去 '_' 和哈希值的长度
        if name_available > 0:
            truncated_name = name_part[:name_available] + '_' + hash_suffix
        else:
            # 如果连哈希值都放不下，只保留哈希值
            truncated_name = hash_suffix[:available_length]
    else:
        # 保留前面和后面的部分
        front_part = name_part[:front_length]
        back_part = name_part[-back_length:] if back_length > 0 else ''
        truncated_name = front_part + '...' + back_part
    
    # 重新组合路径
    new_filename = truncated_name + ext
    new_path = os.path.join(directory, new_filename)
    
    # 双重检查：确保最终路径不超过限制
    if len(new_path) > max_path_length:
        # 如果还是太长，进一步缩短
        remaining = max_path_length - dir_length - ext_length - 1
        if remaining > 20:
            truncated_name = name_part[:remaining - 3] + '...'
        else:
            # 使用哈希值
            hash_suffix = hashlib.md5(name_part.encode('utf-8')).hexdigest()[:8]
            truncated_name = hash_suffix
        new_filename = truncated_name + ext
        new_path = os.path.join(directory, new_filename)
    
    return new_path

async def getVoices():
    voices = await VoicesManager.create()
    voice = voices.find(Language="zh")
    voice = tuple(item['ShortName'] for item in voice)
    return voice

async def generateMp3(content, voice, file_name) -> None:
    # 处理文件名，确保不超过系统限制
    file_name = sanitize_filename(file_name)
    
    chunks = textUtils.split_text_by_length(content)
    with  open(file_name, "wb") as file:
        for text in chunks:
            communicate = edge_tts.Communicate(text, voice)
            # submaker = edge_tts.SubMaker()

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                # elif chunk["type"] == "WordBoundary":
                #     submaker.feed(chunk)

        # with open(SRT_FILE, "w", encoding="utf-8") as file:
        #     file.write(submaker.get_srt())

# def generateByCoqui(content, voice, file_name) -> None:
#     # Get device
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#
#     # List available 🐸TTS models
#     print(TTS().list_models())
#
#     # Init TTS
#     tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
#
#     # Run TTS
#     # ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
#     # Text to speech list of amplitude values as output
#     wav = tts.tts(text="Hello world!", speaker_wav="my/cloning/audio.wav", language="en")
#     # Text to speech to a file
#     tts.tts_to_file(text="Hello world!", speaker_wav="my/cloning/audio.wav", language="en", file_path="output.wav")
