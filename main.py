import asyncio

import aiofiles
import orjson
import settings
from utils import logger
from core import Platform, PixaiPlatform


async def main() -> None:
    # 创建平台爬虫
    platform = PixaiPlatform(
        crawl_type=settings.crawl_type,
        sort_type=settings.sort_type,
    )
    
    # 启动爬虫
    raw_artworks = await platform.start()

    # TODO: 解析原始数据并将其适配多种存储类型
    # 简单地存储为 json 文件
    async with aiofiles.open(settings.output_file, mode='wb') as f:
        await f.write(orjson.dumps(raw_artworks))


if __name__ == "__main__":
    asyncio.run(main())
