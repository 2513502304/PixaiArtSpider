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
    try:
        # # 获取作品集元数据
        # raw_data = await spider.raw_artworks(
        #     query=settings.query,
        #     delay=settings.delay,
        # )
        # logger.info(f'number of {len(raw_data) = }')

        # 获取作品集元数据，并通过时间段筛选
        raw_data_by_daily = await spider.raw_artworks_by_daily(
            query=settings.query,
            delay=settings.delay,
            start_day=settings.start_day,
            end_day=settings.end_day,
        )
        logger.info(f'number of {len(raw_data_by_daily) = }')

    except NotImplementedError as e:
        logger.error(f'NotImplementedError: {e}')
        return

    # 简单地存储为 json 文件
    async with aiofiles.open(settings.output_file, mode='wb') as f:
        await f.write(orjson.dumps(raw_data_by_daily))


if __name__ == "__main__":
    asyncio.run(main())
