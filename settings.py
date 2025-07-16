from factory import CrawlType, SortType

# 爬虫类型
crawl_type: CrawlType = CrawlType.HOME

# 作品排序类型
sort_type: SortType = SortType.RECOMMEND

# 关键字搜索，仅当 crawl_type 为 CrawlType.SEARCH 时有效
query: str = ""

# 爬虫延时，单位为秒，避免请求过快被服务器拒绝
delay: float = 0.5

# 输出文件，目前仅支持 json 格式
output_file: str = '.json'
