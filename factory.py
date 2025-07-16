from enum import Enum, auto

from crawl import PixaiArt, PixaiArtHome, PixaiArtSearch, SortType


class CrawlType(Enum):
    """
    [pixai.art](https://pixai.art/zh) 爬虫类型
    """
    HOME = auto()  # 主页
    SEARCH = auto()  # 关键字搜索


def create_crawl_factory(crawl_type: CrawlType, sort_type: SortType) -> PixaiArt:
    """
    [pixai.art](https://pixai.art/zh) 爬虫工厂
    """
    if crawl_type == CrawlType.HOME:
        return PixaiArtHome(sort_type=sort_type)
    elif crawl_type == CrawlType.SEARCH:
        return PixaiArtSearch(sort_type=sort_type)
    else:
        raise NotImplementedError(f"Unsupported crawl type: {crawl_type}")
