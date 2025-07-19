from abc import ABC, abstractmethod

import settings
from crawl import (CrawlType, PixaiArtHome, PixaiArtSearch, PixaiArtSpider, SortType)
from utils import logger


class Platform(ABC):
    """
    [pixai.art](https://pixai.art/zh) 平台爬虫基类
    """

    @abstractmethod
    async def start(self) -> None:
        """
        启动爬虫
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


class PixaiPlatform(Platform):
    """
    [pixai.art](https://pixai.art/zh) 平台爬虫实现
    """

    def __init__(self, crawl_type: CrawlType, sort_type: SortType):
        self.spider: PixaiArtSpider | None = None
        self.crawl_type = crawl_type
        self.sort_type = sort_type

    async def start(self) -> None:
        """
        启动爬虫
        """
        raw_artworks: list[dict] | None = None

        if self.crawl_type == CrawlType.HOME:
            self.spider: PixaiArtHome = PixaiArtHome(sort_type=self.sort_type)
            raw_artworks = await self.spider.raw_artworks(delay=settings.delay, )
        elif self.crawl_type == CrawlType.SEARCH:
            self.spider: PixaiArtSearch = PixaiArtSearch(sort_type=self.sort_type)
            if self.sort_type != SortType.DAILY:
                raw_artworks = await self.spider.raw_artworks(
                    query=settings.query,
                    delay=settings.delay,
                )
            else:
                raw_artworks = await self.spider.concurrent_raw_artworks_by_daily(
                    query=settings.query,
                    delay=settings.delay,
                    start_day=settings.start_day,
                    end_day=settings.end_day,
                    max_concurrency_num=settings.max_concurrency_num,
                )
        else:
            raise NotImplementedError(f"Unsupported crawl type: {self.crawl_type}")

        logger.info(f'number of {len(raw_artworks) = }')

        # TODO: 解析原始数据并将其适配多种存储类型
        return raw_artworks
