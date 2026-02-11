"""봇 워커 진입점"""

import asyncio

from dotenv import load_dotenv

load_dotenv()

from bot.auto_bot_worker import main  # noqa: E402

if __name__ == "__main__":
    asyncio.run(main())
