from factory import create_crawl_factory, CrawlType, SortType
from utils import logger
import settings

import aiofiles
import asyncio
import orjson


async def main() -> None:
    # 创建爬虫
    spider = create_crawl_factory(
        crawl_type=settings.crawl_type,
        sort_type=settings.sort_type,
    )
    # 获取作品集元数据
    raw_data = await spider.raw_artworks(
        query=settings.query,
        delay=settings.delay,
    )
    logger.info(f'number of {len(raw_data) = }')

    # 简单地存储为 json 文件
    async with aiofiles.open(settings.output_file, mode='wb') as f:
        await f.write(orjson.dumps(raw_data))


if __name__ == "__main__":
    asyncio.run(main())
