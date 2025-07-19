from core import CrawlType, SortType

# 爬虫类型
crawl_type: CrawlType = CrawlType.SEARCH

# 作品排序类型
sort_type: SortType = SortType.DAILY

# 关键字搜索，仅当 crawl_type 为 CrawlType.SEARCH 时有效
query: str = "希露非叶特"

# 爬虫延时，单位为秒，避免请求过快被服务器拒绝
delay: float = 0.5

# 起始日期，格式为 'YYYY-MM-DD'，用于筛选作品集。None 表示从第一条记录的时间开始，仅当 crawl_type 为 CrawlType.SEARCH 且 sort_type 为 SortType.DAILY 时有效
start_day: str | None = None

# 结束日期，格式为 'YYYY-MM-DD'，用于筛选作品集。None 表示到最后一条记录的时间结束，仅当 crawl_type 为 CrawlType.SEARCH 且 sort_type 为 SortType.DAILY 时有效
end_day: str | None = None

# 最大并发数
max_concurrency_num: int = 8

# TODO: 待解析原始数据并将其适配多种存储类型
# 输出文件，目前仅支持 json 格式
output_file: str = './希露非叶特.json'
