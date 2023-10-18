import asyncio
import os

from core.kurisu import KurisuBot

if __name__ == "__main__":
    if os.name == "nt":  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(KurisuBot().start())
