import edge_tts
import textUtils
import asyncio
from edge_tts import VoicesManager
import torch
# from TTS.api import TTS

async def getVoices():
    voices = await VoicesManager.create()
    voice = voices.find(Language="zh")
    voice = tuple(item['ShortName'] for item in voice)
    return voice

async def generateMp3(content, voice, file_name) -> None:
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
