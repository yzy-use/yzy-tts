import asyncio
import random

from edge_tts import VoicesManager
import edge_tts


async def main():

    voices = await VoicesManager.create()
    print(voices)
    voice = voices.find(Language="zh")
    print(voice)

    for item in voice:
        keys = item.keys()
        values = item.values()
        print(values)
        # print(item["Name"])




if __name__ == "__main__":
    asyncio.run(main())