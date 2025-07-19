import asyncio
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum, auto

import httpx
import numpy as np
import pandas as pd
from fake_useragent import UserAgent
from lxml import etree
from utils import logger


class CrawlType(Enum):
    """
    [pixai.art](https://pixai.art/zh) 爬虫类型
    """
    HOME = auto()  # 主页
    SEARCH = auto()  # 关键字搜索


class SortType(Enum):
    """
    [pixai.art](https://pixai.art/zh) 作品排序类型
    
    主页中可使用的排序类型有：
    1. 推荐
    2. 热门
    3. 每日排名
    4. 关注
    5. 最受欢迎
    6. 最新的
    
    关键字搜索中可使用的排序类型有：
    1. 热门
    2. 每日排名
    3. 最受欢迎
    4. 最新的
    """
    RECOMMEND = 'recommend-v1'  # 推荐
    TRENDING = 'trending1'  # 热门
    DAILY = 'daily_ranking_dedup'  # 每日排名
    FOLLOWING = 'following_news'  # 关注
    MOST_LIKE = '-markInfo.likedCount'  # 最受欢迎
    LATEST = 'latest'  # 最新的


class PixaiArtSpider(ABC):
    """
    [pixai.art](https://pixai.art/zh) 爬虫
    """

    def __init__(self):
        self.host = 'https://api.pixai.art'
        self.headers = {
            'User-Agent': UserAgent().random,
            'Referer': 'https://pixai.art',
            'Content-Type': 'application/json',
        }
        self.client = httpx.AsyncClient(headers=self.headers, base_url=self.host, timeout=30.0)

    @abstractmethod
    async def raw_artworks(
        self,
        query: str = '',
        delay: float = 0.5,
    ) -> list[dict]:
        """
        获取作品集元数据
        
        Args:
            query (str, optional): 关键字搜索参数. Defaults to ''.
            delay (float, optional): 爬虫延时，单位为秒，避免请求过快被服务器拒绝. Defaults to 0.5.
            
        Returns:
            list[dict]: 作品集元数据
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    async def raw_artworks_by_daily(
        self,
        query: str = '',
        delay: float = 0.5,
        start_day: str | None = None,
        end_day: str | None = None,
    ) -> list[dict]:
        """
        获取作品集元数据，并通过时间段筛选

        Args:
            query (str, optional): 关键字搜索参数. Defaults to ''.
            delay (float, optional): 爬虫延时，单位为秒，避免请求过快被服务器拒绝. Defaults to 0.5.
            start_day (str, optional): 起始日期，格式为 'YYYY-MM-DD'，用于筛选作品集. Defaults to None，默认从第一条记录的时间开始.
            end_day (str, optional): 结束日期，格式为 'YYYY-MM-DD'，用于筛选作品集. Defaults to None，默认到最后一条记录的时间结束.

        Returns:
            list[dict]: 作品集元数据
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


class PixaiArtHome(PixaiArtSpider):
    """
    [pixai.art](https://pixai.art/zh) 主页爬虫
    """

    def __init__(self, sort_type: SortType = SortType.RECOMMEND):
        """
        初始化主页爬虫

        Args:
            sort_type (SortType, optional): 作品排序类型. Defaults to SortType.RECOMMEND.
        """
        super().__init__()

        self.sort_type: SortType = sort_type
        available_sort_types = [SortType.RECOMMEND, SortType.TRENDING, SortType.DAILY, SortType.FOLLOWING, SortType.MOST_LIKE, SortType.LATEST]
        if self.sort_type not in available_sort_types:
            raise ValueError(f"Invalid sort type: {self.sort_type}, must be one of {available_sort_types}")

    async def raw_artworks(
        self,
        query: str = '',
        delay: float = 0.5,
    ) -> list[dict]:
        """
        获取主页作品集元数据
        
        Args:
            query (str, optional): 未使用，按惯例放在此处以保持 API 一致性. Defaults to ''.
            delay (float, optional): 爬虫延时，单位为秒，避免请求过快被服务器拒绝. Defaults to 0.5.
        
        Returns:
            list[dict]: 作品集元数据
            
        Return json format:
        ```json
        {
            "data": {
                "artworks": {
                    "edges": [
                        {
                            "node": {
                                "__typename": "Artwork",
                                "id": "1901533558655728173",
                                "title": "kochou shinobu",
                                "authorId": "1877188271357745024",
                                "prompts": "a fantasy illustration of a woman standing on a grassy field with water features, 1girl, kochou shinobu, demon slayer uniform, butterfly hair ornament, hair ornament, solo, weapon, japanese clothes, sword, haori, black hair, purple hair, purple eyes, pants,tokiame,project sekai; soft; pastel; colorful; detailed; details; masterpiece; high quality; best quality; ultra details; amazing; stunning; illustration,748cmstyle,tokiame,Foreshortening, (blurry background:0.8)",
                                "createdAt": "2025-07-14T16:25:46.441Z",
                                "updatedAt": "2025-07-14T16:25:47.191Z",
                                "mediaId": "611233887955687392",
                                "media": {
                                    "id": "611233887955687392",
                                    "type": "IMAGE",
                                    "width": 1344,
                                    "height": 896,
                                    "urls": [
                                        {
                                            "variant": "PUBLIC",
                                            "url": "https://images-ng.pixai.art/images/orig/c448a3f0-ebc1-4a74-9de2-e35549b6017e"
                                        },
                                        {
                                            "variant": "THUMBNAIL",
                                            "url": "https://images-ng.pixai.art/images/thumb/c448a3f0-ebc1-4a74-9de2-e35549b6017e"
                                        },
                                        {
                                            "variant": "STILL_THUMBNAIL",
                                            "url": "https://images-ng.pixai.art/images/stillThumb/c448a3f0-ebc1-4a74-9de2-e35549b6017e"
                                        }
                                    ],
                                    "imageType": "webp",
                                    "fileUrl": null,
                                    "duration": null,
                                    "thumbnailUrl": null,
                                    "hlsUrl": null,
                                    "size": null,
                                    "flag": {
                                        "shouldBlur": false
                                    }
                                },
                                "videoMediaId": null,
                                "hidePrompts": false,
                                "isPrivate": false,
                                "isNsfw": false,
                                "isSensitive": false,
                                "extra": {
                                    "isMinors": false,
                                    "isWarned": false,
                                    "isSexyPic": false,
                                    "cpKeywords": [],
                                    "isRealistic": false,
                                    "isSensitive": false,
                                    "imageBlurHash": "UBCi{x4.IS?bw6IU9Z-qx]IoV_%L01xa?HM_",
                                    "suggestedTags": [
                                        "kimetsu_no_yaiba",
                                        "kochou_shinobu",
                                        "anime_style",
                                        "1girl",
                                        "breasts",
                                        "long_sleeves",
                                        "looking_at_viewer",
                                        "parted_bangs",
                                        "sidelocks",
                                        "solo",
                                        "standing",
                                        "hair_ornament",
                                        "holding",
                                        "short_hair",
                                        "full_body",
                                        "holding_sword",
                                        "holding_weapon",
                                        "sword",
                                        "weapon",
                                        "medium_breasts",
                                        "purple_eyes",
                                        "outdoors",
                                        "purple_hair",
                                        "water",
                                        "black_hair",
                                        "parted_lips",
                                        "animal_print",
                                        "buttons",
                                        "from_above",
                                        "wide_sleeves",
                                        "gradient_hair",
                                        "multicolored_hair",
                                        "walking",
                                        "katana",
                                        "jacket",
                                        "forehead",
                                        "wading",
                                        "belt",
                                        "grass",
                                        "sandals",
                                        "pants",
                                        "bug",
                                        "forest",
                                        "nature",
                                        "japanese_clothes",
                                        "ripples",
                                        "tabi",
                                        "walking_on_liquid",
                                        "dual_wielding",
                                        "rock",
                                        "black_jacket",
                                        "white_belt",
                                        "scabbard",
                                        "sheath",
                                        "bamboo",
                                        "buckle",
                                        "belt_buckle",
                                        "reflection",
                                        "stream",
                                        "butterfly",
                                        "two-tone_hair",
                                        "black_pants",
                                        "zouri",
                                        "standing_on_liquid",
                                        "unsheathed",
                                        "holding_sheath",
                                        "puffy_pants",
                                        "pink_butterfly",
                                        "blue_butterfly",
                                        "haori",
                                        "butterfly_hair_ornament",
                                        "updo",
                                        "military_jacket",
                                        "wisteria",
                                        "white_butterfly",
                                        "butterfly_print",
                                        "hakama_pants",
                                        "pond",
                                        "purple_butterfly",
                                        "demon_slayer_uniform"
                                    ],
                                    "moderationMachine": "Mon Jul 14 2025 16:25:47 GMT+0000 (Coordinated Universal Time)",
                                    "sensitiveKeywords": [
                                        "12 years",
                                        "14 years",
                                        "5-year-old",
                                        "age 13",
                                        "anal",
                                        "ass",
                                        "asshole",
                                        "baby",
                                        "bondage",
                                        "boobs",
                                        "breast",
                                        "breasts",
                                        "bust",
                                        "diaper",
                                        "doggy style",
                                        "ejaculation",
                                        "elementary school",
                                        "fellatio",
                                        "futanari",
                                        "hentai",
                                        "horror",
                                        "incest",
                                        "inguinal",
                                        "juvenile",
                                        "little girl",
                                        "loli",
                                        "milf",
                                        "moaning",
                                        "naked",
                                        "nipples",
                                        "nsfw",
                                        "nude",
                                        "panties",
                                        "panty",
                                        "penis",
                                        "pussy",
                                        "seductive",
                                        "see through",
                                        "sex",
                                        "shota",
                                        "sideboob",
                                        "smut",
                                        "spread legs",
                                        "tied up",
                                        "tits",
                                        "topless"
                                    ],
                                    "censorSensitiveFlag": "PASS"
                                },
                                "type": "DEFAULT",
                                "paidCredit": null,
                                "aesScore": null,
                                "feedMetadata": {
                                    "retrieverId": "ops_boosted_artwork"
                                },
                                "flag": {
                                    "status": "END",
                                    "isSensitive": false,
                                    "isMinors": false,
                                    "isRealistic": false,
                                    "isFlagged": false,
                                    "isSexyPic": false,
                                    "isSexyText": false,
                                    "shouldBlur": false,
                                    "isWarned": false,
                                    "isAppealable": false
                                },
                                "likedCount": 43,
                                "liked": false,
                                "commentCount": 0,
                                "author": {
                                    "id": "1877188271357745024",
                                    "email": null,
                                    "emailVerified": null,
                                    "username": "jochen09",
                                    "displayName": "Bluemiee",
                                    "createdAt": "2025-05-08T12:06:17.364Z",
                                    "updatedAt": null,
                                    "avatarMediaId": "606517133563366068",
                                    "membership": {
                                        "membershipId": "membership-plus",
                                        "tier": 2
                                    },
                                    "deleteAfter": null,
                                    "isAdmin": false,
                                    "aprilFoolsDayProfile": null,
                                    "springEventProfile": null,
                                    "summerEvent2025Profile": null
                                },
                                "manga": null
                            },
                            "cursor": "gqJpZNcAGmOasmQoui2lc2NvcmUX"
                        },
                    ...
                    ],
                    "pageInfo": {
                        "hasNextPage": true,
                        "hasPreviousPage": false,
                        "endCursor": "gqJpZNcAGmKtegjsmMylc2NvcmUu",
                        "startCursor": "gqJpZNcAGmOasmQoui2lc2NvcmUX"
                    }
                }
            }
        }
        ```
        """
        url = '/graphql'
        params = {
            'operation': 'listArtworks',
        }
        #!Note: post 表单不能同时提供 first 和 last 参数，否则引发以下异常
        """
        !provide first and last args:
        {'errors': [{'message': 'Not support both first and last provided.',
        'locations': [{'line': 3, 'column': 3}],
        'path': ['artworks'],
        'extensions': {'code': 'INVALID_PAGINATION_INPUT',
            'exception': {'message': 'Not support both first and last provided.'}}}],
        'data': None}
        """
        #!Note: 浏览器控制台中，除 SortType.LATEST 默认使用的为 before 和 last 参数外，其他排序类型默认使用的是 after 和 first 参数
        #!但经测试，除 SortType.RECOMMEND 和 SortType.DAILY 不能使用 before 和 last 参数外，其他排序类型均可使用 before 和 last 参数，并且所有 SortType 均可使用 after 和 first 参数，其中 after 和 first 为一固定的参数组合，before 和 last 为一固定的参数组合
        #!必须严格遵循不同排序类型的 post 表单参数，否则引发以下异常
        """
        !SortType.RECOMMEND with wrong args:
        {'errors': [{'message': 'recommendation feed does not support negative sequence',
        'locations': [{'line': 3, 'column': 3}],
        'path': ['artworks'],
        'extensions': {'code': 'Bad Request',
            'status': 400,
            'message': 'recommendation feed does not support negative sequence',
            'exception': {'code': 40000000,
            'name': 'BAD_REQUEST',
            'expose': True,
            'statusCode': 400,
            'status': 400}}}],
        'data': None}
        
        !SortType.DAILY with wrong args:
        {'errors': [{'message': 'daily ranking dedup feed must be forward',
        'locations': [{'line': 3, 'column': 3}],
        'path': ['artworks'],
        'extensions': {'code': 'Bad Request',
            'status': 400,
            'message': 'daily ranking dedup feed must be forward',
            'exception': {'code': 40000000,
            'name': 'BAD_REQUEST',
            'expose': True,
            'statusCode': 400,
            'status': 400}}}],
        'data': None}
        """
        json_data = {
            'query':
            '\n    query listArtworks($before: String, $after: String, $first: Int, $last: Int, $orderBy: String, $isNsfw: Boolean, $tag: String, $q: String, $relevantArtworkId: ID, $keyword: String, $text: String, $hidePrompts: Boolean, $isSafeSearch: Boolean, $feed: String, $authorId: ID, $challenge: Int, $archived: Boolean, $isPrivate: Boolean, $i2vPro: Boolean, $animatedBaseArtworkId: ID, $modelId: ID, $modelVersionId: ID, $loraId: ID, $loraVersionId: ID, $workflowId: ID, $workflowVersionId: ID, $time: DateRange, $type: ArtworkType, $types: [ArtworkType], $rankMediaType: RankMediaType, $worldId: ID, $characterId: ID) {\n  artworks(\n    before: $before\n    after: $after\n    first: $first\n    last: $last\n    orderBy: $orderBy\n    isNsfw: $isNsfw\n    tag: $tag\n    q: $q\n    relevantArtworkId: $relevantArtworkId\n    keyword: $keyword\n    text: $text\n    hidePrompts: $hidePrompts\n    isSafeSearch: $isSafeSearch\n    feed: $feed\n    authorId: $authorId\n    challenge: $challenge\n    archived: $archived\n    isPrivate: $isPrivate\n    i2vPro: $i2vPro\n    animatedBaseArtworkId: $animatedBaseArtworkId\n    modelId: $modelId\n    modelVersionId: $modelVersionId\n    loraId: $loraId\n    loraVersionId: $loraVersionId\n    worldId: $worldId\n    characterId: $characterId\n    workflowId: $workflowId\n    workflowVersionId: $workflowVersionId\n    time: $time\n    type: $type\n    types: $types\n    rankMediaType: $rankMediaType\n  ) {\n    edges {\n      node {\n        ...ArtworkWithMangaPreview\n      }\n      cursor\n    }\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      endCursor\n      startCursor\n    }\n  }\n}\n    \n    fragment ArtworkWithMangaPreview on Artwork {\n  ...ArtworkPreview\n  manga {\n    ...MangaBase\n    likedCount\n    liked\n    chapter(index: 0) {\n      ...MangaChapterBase\n    }\n  }\n}\n    \n\n    fragment ArtworkPreview on Artwork {\n  ...ArtworkBase\n  likedCount\n  liked\n  commentCount\n  author {\n    ...UserBase\n  }\n  flag {\n    ...ModerationFlagDetail\n  }\n}\n    \n\n    fragment ArtworkBase on Artwork {\n  __typename\n  id\n  title\n  authorId\n  prompts\n  createdAt\n  updatedAt\n  mediaId\n  media {\n    ...MediaBase\n  }\n  videoMediaId\n  hidePrompts\n  isPrivate\n  isNsfw\n  isSensitive\n  extra\n  type\n  paidCredit\n  aesScore\n  flag {\n    ...ModerationFlagDetail\n  }\n}\n    \n\n    fragment MediaBase on Media {\n  id\n  type\n  width\n  height\n  urls {\n    variant\n    url\n  }\n  imageType\n  fileUrl\n  duration\n  thumbnailUrl\n  hlsUrl\n  size\n  flag {\n    ...ModerationFlagPreview\n  }\n}\n    \n\n    fragment ModerationFlagPreview on ModerationFlag {\n  shouldBlur\n}\n    \n\n    fragment ModerationFlagDetail on ModerationFlag {\n  status\n  isSensitive\n  isMinors\n  isRealistic\n  isFlagged\n  isSexyPic\n  isSexyText\n  shouldBlur\n  isWarned\n  isAppealable\n}\n    \n\n    fragment UserBase on User {\n  id\n  email\n  emailVerified\n  username\n  displayName\n  createdAt\n  updatedAt\n  avatarMediaId\n  membership {\n    membershipId\n    tier\n  }\n  deleteAfter\n  isAdmin\n  aprilFoolsDayProfile: profile(key: "aprilFoolsDay2025")\n  springEventProfile: profile(key: "springEvent2025")\n}\n    \n\n    fragment MangaBase on Manga {\n  __typename\n  id\n  authorId\n  title\n  description\n  coverMediaId\n  coverMedia {\n    ...MediaBase\n  }\n  isNsfw\n  isPrivate\n  isArchived\n  type\n  extra\n  createdAt\n  updatedAt\n  artworkId\n}\n    \n\n    fragment MangaChapterBase on MangaChapter {\n  id\n  mangaId\n  order\n  title\n  coverMediaId\n  coverMedia {\n    ...MediaBase\n  }\n  originalData\n  content\n  createdAt\n  updatedAt\n}\n    ',
            'variables': {
                'after': '',
                'feed': self.sort_type.value,
                'first': 24,
                'isSafeSearch': True,
            },
        }
        response = await self.client.post(url=url, params=params, json=json_data)

        # 作品集
        artworks = response.json()['data']['artworks']

        # 主体数据
        edges: list[dict] = artworks['edges']
        # 分页信息
        pageInfo: dict = artworks['pageInfo']

        # 判断是否存在下一页，并获取 endCursor 作为请求下一页的 json 表单参数
        hasNextPage = pageInfo['hasNextPage']
        hasPreviousPage = pageInfo['hasPreviousPage']
        endCursor = pageInfo['endCursor']
        startCursor = pageInfo['startCursor']
        while hasNextPage:
            # 避免请求过快被服务器拒绝
            time.sleep(delay)

            # 发起下一次请求
            json_data['variables']['after'] = endCursor
            response = await self.client.post(url=url, params=params, json=json_data)
            artworks = response.json()['data']['artworks']

            # 累加作品集数据
            edges.extend(artworks['edges'])

            # 更新分页信息
            pageInfo = artworks['pageInfo']

            hasNextPage = pageInfo['hasNextPage']
            hasPreviousPage = pageInfo['hasPreviousPage']
            endCursor = pageInfo['endCursor']
            startCursor = pageInfo['startCursor']

        return edges

    async def raw_artworks_by_daily(
        self,
        query: str = '',
        delay: float = 0.5,
        start_day: str | None = None,
        end_day: str | None = None,
    ) -> list[dict]:
        """
        获取作品集元数据，并通过时间段筛选

        Args:
            query (str, optional): 关键字搜索参数. Defaults to ''.
            delay (float, optional): 爬虫延时，单位为秒，避免请求过快被服务器拒绝. Defaults to 0.5.
            start_day (str, optional): 起始日期，格式为 'YYYY-MM-DD'，用于筛选作品集. Defaults to None，默认从第一条记录的时间开始.
            end_day (str, optional): 结束日期，格式为 'YYYY-MM-DD'，用于筛选作品集. Defaults to None，默认到最后一条记录的时间结束.

        Returns:
            list[dict]: 作品集元数据
        """
        raise NotImplementedError("Home crawler does not support date filtering. Use PixaiArtSearch for keyword search with date filtering.")


class PixaiArtSearch(PixaiArtSpider):
    """
    [pixai.art](https://pixai.art/zh/search) 关键字搜索爬虫
    """

    def __init__(self, sort_type: SortType = SortType.TRENDING):
        """
        初始化关键字搜索爬虫

        Args:
            sort_type (SortType, optional): 作品排序类型. Defaults to SortType.TRENDING.

        Raises:
            ValueError: 若 sort_type 不属于 [SortType.TRENDING, SortType.DAILY, SortType.MOST_LIKE, SortType.LATEST] 中的任意一个.
        """
        super().__init__()

        self.sort_type: SortType = sort_type
        available_sort_types = [SortType.TRENDING, SortType.DAILY, SortType.MOST_LIKE, SortType.LATEST]
        if self.sort_type not in available_sort_types:
            raise ValueError(f"Invalid sort type: {self.sort_type}, must be one of {available_sort_types}")

    async def raw_artworks(
        self,
        query: str = '',
        delay: float = 0.5,
    ) -> list[dict]:
        """
        获取关键字搜索作品集元数据
        
        Args:
            query (str, optional): 关键字搜索参数. Defaults to ''.
            delay (float, optional): 爬虫延时，单位为秒，避免请求过快被服务器拒绝. Defaults to 0.5.
            
        Returns:
            list[dict]: 作品集元数据
            
        Return json format:
        ```json
        {
            "data": {
                "artworks": {
                    "edges": [
                        {
                            "node": {
                                "__typename": "Artwork",
                                "id": "1901784967489555911",
                                "title": "芙羽ここね",
                                "authorId": "1901360620515316626",
                                "prompts": "ultra-detailed, masterpiece, best quality, detailed, highly detailed, ultra detailed, high resolution, ultra details, details face, beautiful details eyes, detailed eyes, details eyes, detailed face, 1girl, solo, weight gain, chubby, soft belly, muffin top, oversized, overweight, majestic quality, unrealistic proportions, big belly, obese, full belly, morbidly obese, gigantic hips, gigantic ass, expansion, busty, huge booty, extra thicc, large booty, massive booty, milf, wide hips, thick thighs, gigantic breasts, cleavage, alternate breast size, developing gigantic breasts, oversized gigantic breasts, bottomheavy, huge breasts, massive thighs, gigantic butt, standing on one leg, leg up, contrapposto, looking at viewer, fuwa kokone, blue hair, medium hair, green eyes, penetration gesture, naughty face, school uniform, white shirt, long sleeves, red necktie, blue skirt, sleeves rolled up, sweater around waist, school bag on shoulder, trees in schoolyard",
                                "createdAt": "2025-07-15T09:04:46.979Z",
                                "updatedAt": "2025-07-15T09:04:48.350Z",
                                "mediaId": "611485013762142319",
                                "media": {
                                    "id": "611485013762142319",
                                    "type": "IMAGE",
                                    "width": 768,
                                    "height": 1280,
                                    "urls": [
                                        {
                                            "variant": "PUBLIC",
                                            "url": "https://images-ng.pixai.art/images/orig/20c48e32-43d2-455b-b684-873f62f2ed42"
                                        },
                                        {
                                            "variant": "THUMBNAIL",
                                            "url": "https://images-ng.pixai.art/images/thumb/20c48e32-43d2-455b-b684-873f62f2ed42"
                                        },
                                        {
                                            "variant": "STILL_THUMBNAIL",
                                            "url": "https://images-ng.pixai.art/images/stillThumb/20c48e32-43d2-455b-b684-873f62f2ed42"
                                        }
                                    ],
                                    "imageType": "webp",
                                    "fileUrl": null,
                                    "duration": null,
                                    "thumbnailUrl": null,
                                    "hlsUrl": null,
                                    "size": null,
                                    "flag": {
                                        "shouldBlur": false
                                    }
                                },
                                "videoMediaId": null,
                                "hidePrompts": false,
                                "isPrivate": false,
                                "isNsfw": false,
                                "isSensitive": false,
                                "extra": {
                                    "isMinors": false,
                                    "isWarned": false,
                                    "isSexyPic": false,
                                    "cpKeywords": [],
                                    "isRealistic": false,
                                    "isSensitive": false,
                                    "imageBlurHash": "USK1gwtQ55%g0|oLsjIo9XWVt6aK4-X8-oWC",
                                    "suggestedTags": [
                                        "anime_style",
                                        "1girl",
                                        "blush",
                                        "breasts",
                                        "looking_at_viewer",
                                        "school_uniform",
                                        "shirt",
                                        "smile",
                                        "solo",
                                        "standing",
                                        "thighs",
                                        "ahoge",
                                        "hair_ornament",
                                        "short_hair",
                                        "skirt",
                                        "green_eyes",
                                        "outdoors",
                                        "shoes",
                                        "bag",
                                        "bush",
                                        "day",
                                        "pleated_skirt",
                                        "school_bag",
                                        "tree",
                                        "sky",
                                        "white_shirt",
                                        "collared_shirt",
                                        "miniskirt",
                                        "navel",
                                        "socks",
                                        "black_socks",
                                        "kneehighs",
                                        "brown_footwear",
                                        "loafers",
                                        "necktie",
                                        "blue_skirt",
                                        "hairclip",
                                        "black_footwear",
                                        "blue_socks",
                                        "cleavage",
                                        "sweater",
                                        "grin",
                                        "huge_breasts",
                                        "partially_unbuttoned",
                                        "red_necktie",
                                        "standing_on_one_leg",
                                        "brown_cardigan",
                                        "cardigan",
                                        "foot_out_of_frame",
                                        "thick_thighs",
                                        "plump",
                                        "fat",
                                        "bag_charm",
                                        "charm_(object)",
                                        "shoulder_bag",
                                        "between_breasts",
                                        "loose_necktie",
                                        "park",
                                        "clothes_around_waist",
                                        "ok_sign",
                                        "sweater_around_waist",
                                        "handjob_gesture",
                                        "fellatio_gesture",
                                        "cardigan_around_waist"
                                    ],
                                    "naturalPrompts": "ultra-detailed, masterpiece, best quality, detailed, highly detailed, ultra detailed, \nhigh resolution, ultra details, details face,\nbeautiful details eyes, detailed eyes, \ndetails eyes, detailed face,\n\n1girl, solo,\n\nWeight gain, chubby, soft belly, muffin top, oversized,(overweight), masterpiece, detailed, highly detailed, ultra detailed, high resolution, best quality, majestic quality, unrealistic proportions, big belly, obese , full belly, big belly, (unrealistic proportions),Morbidly obese, gigantic hips , gigantic ass , expansion, \nbusty , huge booty, extra thicc, large booty, massive booty, milf, wide hips, thick thighs, \ngigantic_breasts, cleavage, Alternate breast size, developing gigantic breasts, gigantic breasts, oversized gigantic breasts, bottomheavy, huge breasts, massive thighs, gigantic butt, gigantic hips, \n\nstanding on one leg, leg up, contrapposto, looking at viewer,\n\nFuwa Kokone, blue hair, medium hair, green eyes, \n\npenetration gesture, naughty face, \n\nschool uniform, white shirt, long sleeves, red necktie, blue skirt, sleeves rolled up, sweater around waist,スクールバッグを肩に担ぐ、\n木の並ぶ学校の校庭、\n\n\n",
                                    "moderationMachine": "Tue Jul 15 2025 09:04:48 GMT+0000 (Coordinated Universal Time)",
                                    "sensitiveKeywords": [
                                        "breast",
                                        "breasts",
                                        "bust",
                                        "child",
                                        "deep throat",
                                        "futanari",
                                        "gigantic ass",
                                        "gigantic breasts",
                                        "gigantic butt",
                                        "horror",
                                        "huge booty",
                                        "huge breasts",
                                        "large booty",
                                        "loli",
                                        "milf",
                                        "moaning",
                                        "nsfw",
                                        "nude",
                                        "penetration",
                                        "seductive",
                                        "sex",
                                        "small girl",
                                        "spread legs",
                                        "topless"
                                    ],
                                    "censorSensitiveFlag": "PASS"
                                },
                                "type": "DEFAULT",
                                "paidCredit": null,
                                "aesScore": null,
                                "feedMetadata": null,
                                "flag": {
                                    "status": "END",
                                    "isSensitive": false,
                                    "isMinors": false,
                                    "isRealistic": false,
                                    "isFlagged": false,
                                    "isSexyPic": false,
                                    "isSexyText": false,
                                    "shouldBlur": false,
                                    "isWarned": false,
                                    "isAppealable": false
                                },
                                "likedCount": 4,
                                "liked": false,
                                "commentCount": 0,
                                "author": {
                                    "id": "1901360620515316626",
                                    "email": null,
                                    "emailVerified": null,
                                    "username": "hoimiso",
                                    "displayName": "ホイミソ2",
                                    "createdAt": "2025-07-14T04:58:34.503Z",
                                    "updatedAt": null,
                                    "avatarMediaId": "",
                                    "membership": null,
                                    "deleteAfter": null,
                                    "isAdmin": false,
                                    "aprilFoolsDayProfile": null,
                                    "springEventProfile": null,
                                    "summerEvent2025Profile": null
                                },
                                "manga": null
                            },
                            "cursor": "gqJpZNcAGmR/WhJkjcekc29ydJLLQGdMBMBZIQSzMTkwMTc4NDk2NzQ4OTU1NTkxMQ=="
                        },
                    ...
                    ],
                    "pageInfo": {
                        "hasNextPage": false,
                        "hasPreviousPage": true,
                        "endCursor": "gqJpZNcAGmVARcJLN8Ckc29ydJLLQHGRhfBvaUSzMTkwMTk5NzA4NTk5MDUzMzA1Ng==",
                        "startCursor": "gqJpZNcAGmR/WhJkjcekc29ydJLLQGdMBMBZIQSzMTkwMTc4NDk2NzQ4OTU1NTkxMQ=="
                    }
                }
            }
        }
        ```
        """
        url = '/graphql'
        params = {
            'operation': 'listArtworks',
        }
        #!Note: post 表单不能同时提供 first 和 last 参数，否则引发以下异常
        """
        !provide first and last args:
        {'errors': [{'message': 'Not support both first and last provided.',
        'locations': [{'line': 3, 'column': 3}],
        'path': ['artworks'],
        'extensions': {'code': 'INVALID_PAGINATION_INPUT',
            'exception': {'message': 'Not support both first and last provided.'}}}],
        'data': None}
        """
        #!Note: 浏览器控制台中，SortType.TRENDING 与 SortType.LATEST 默认使用的为 before 和 last 参数，SortType.DAILY 与 SortType.MOST_LIKE 默认使用的是 after 和 first 参数
        #!但经测试，所有 SortType 均可使用 before 和 last 参数，after 和 first 参数，其中 after 和 first 为一固定的参数组合，before 和 last 为一固定的参数组合
        json_data = {
            'query':
            '\n    query listArtworks($before: String, $after: String, $first: Int, $last: Int, $orderBy: String, $isNsfw: Boolean, $tag: String, $q: String, $relevantArtworkId: ID, $keyword: String, $text: String, $hidePrompts: Boolean, $isSafeSearch: Boolean, $feed: String, $authorId: ID, $challenge: Int, $archived: Boolean, $isPrivate: Boolean, $i2vPro: Boolean, $animatedBaseArtworkId: ID, $modelId: ID, $modelVersionId: ID, $loraId: ID, $loraVersionId: ID, $workflowId: ID, $workflowVersionId: ID, $time: DateRange, $type: ArtworkType, $types: [ArtworkType], $rankMediaType: RankMediaType, $worldId: ID, $characterId: ID) {\n  artworks(\n    before: $before\n    after: $after\n    first: $first\n    last: $last\n    orderBy: $orderBy\n    isNsfw: $isNsfw\n    tag: $tag\n    q: $q\n    relevantArtworkId: $relevantArtworkId\n    keyword: $keyword\n    text: $text\n    hidePrompts: $hidePrompts\n    isSafeSearch: $isSafeSearch\n    feed: $feed\n    authorId: $authorId\n    challenge: $challenge\n    archived: $archived\n    isPrivate: $isPrivate\n    i2vPro: $i2vPro\n    animatedBaseArtworkId: $animatedBaseArtworkId\n    modelId: $modelId\n    modelVersionId: $modelVersionId\n    loraId: $loraId\n    loraVersionId: $loraVersionId\n    worldId: $worldId\n    characterId: $characterId\n    workflowId: $workflowId\n    workflowVersionId: $workflowVersionId\n    time: $time\n    type: $type\n    types: $types\n    rankMediaType: $rankMediaType\n  ) {\n    edges {\n      node {\n        ...ArtworkWithMangaPreview\n      }\n      cursor\n    }\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      endCursor\n      startCursor\n    }\n  }\n}\n    \n    fragment ArtworkWithMangaPreview on Artwork {\n  ...ArtworkPreview\n  manga {\n    ...MangaBase\n    likedCount\n    liked\n    chapter(index: 0) {\n      ...MangaChapterBase\n    }\n  }\n}\n    \n\n    fragment ArtworkPreview on Artwork {\n  ...ArtworkBase\n  likedCount\n  liked\n  commentCount\n  author {\n    ...UserBase\n  }\n  flag {\n    ...ModerationFlagDetail\n  }\n}\n    \n\n    fragment ArtworkBase on Artwork {\n  __typename\n  id\n  title\n  authorId\n  prompts\n  createdAt\n  updatedAt\n  mediaId\n  media {\n    ...MediaBase\n  }\n  videoMediaId\n  hidePrompts\n  isPrivate\n  isNsfw\n  isSensitive\n  extra\n  type\n  paidCredit\n  aesScore\n  flag {\n    ...ModerationFlagDetail\n  }\n}\n    \n\n    fragment MediaBase on Media {\n  id\n  type\n  width\n  height\n  urls {\n    variant\n    url\n  }\n  imageType\n  fileUrl\n  duration\n  thumbnailUrl\n  hlsUrl\n  size\n  flag {\n    ...ModerationFlagPreview\n  }\n}\n    \n\n    fragment ModerationFlagPreview on ModerationFlag {\n  shouldBlur\n}\n    \n\n    fragment ModerationFlagDetail on ModerationFlag {\n  status\n  isSensitive\n  isMinors\n  isRealistic\n  isFlagged\n  isSexyPic\n  isSexyText\n  shouldBlur\n  isWarned\n  isAppealable\n}\n    \n\n    fragment UserBase on User {\n  id\n  email\n  emailVerified\n  username\n  displayName\n  createdAt\n  updatedAt\n  avatarMediaId\n  membership {\n    membershipId\n    tier\n  }\n  deleteAfter\n  isAdmin\n  aprilFoolsDayProfile: profile(key: "aprilFoolsDay2025")\n  springEventProfile: profile(key: "springEvent2025")\n}\n    \n\n    fragment MangaBase on Manga {\n  __typename\n  id\n  authorId\n  title\n  description\n  coverMediaId\n  coverMedia {\n    ...MediaBase\n  }\n  isNsfw\n  isPrivate\n  isArchived\n  type\n  extra\n  createdAt\n  updatedAt\n  artworkId\n}\n    \n\n    fragment MangaChapterBase on MangaChapter {\n  id\n  mangaId\n  order\n  title\n  coverMediaId\n  coverMedia {\n    ...MediaBase\n  }\n  originalData\n  content\n  createdAt\n  updatedAt\n}\n    ',
            'variables': {
                'after': '',
                'first': 24,
                'isSafeSearch': True,
                'q': query,
            },
        }
        if self.sort_type == SortType.TRENDING:
            json_data['variables']['feed'] = SortType.TRENDING.value
        elif self.sort_type == SortType.DAILY:
            json_data['variables']['orderBy'] = SortType.MOST_LIKE.value
            # 获取当前时间
            current_time = datetime.now()
            # 获取 7 天前的时间
            last_week_time = current_time - timedelta(days=7)
            # 'time': {  # 注意：gt 和 lt 的值必须是 ISO 8601 格式的字符串，且必须包含毫秒部分
            #     'gt': '2025-07-08T16:00:00.000Z',
            #     'lt': '2025-07-16T16:00:00.000Z',
            # },
            # 将时间转换为 ISO 8601 格式的字符串，固定毫秒部分为 .000
            current_time_iso = current_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            last_week_time_iso = last_week_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            json_data['variables']['time'] = {
                'gt': last_week_time_iso,
                'lt': current_time_iso,
            }
        elif self.sort_type == SortType.MOST_LIKE:
            json_data['variables']['orderBy'] = SortType.MOST_LIKE.value
        elif self.sort_type == SortType.LATEST:
            json_data['variables']['feed'] = SortType.LATEST.value
        response = await self.client.post(url=url, params=params, json=json_data)

        # 作品集
        artworks = response.json()['data']['artworks']

        # 主体数据
        edges: list[dict] = artworks['edges']
        # 分页信息
        pageInfo: dict = artworks['pageInfo']

        # 判断是否存在下一页，并获取 endCursor 作为请求下一页的 json 表单参数
        hasNextPage = pageInfo['hasNextPage']
        hasPreviousPage = pageInfo['hasPreviousPage']
        endCursor = pageInfo['endCursor']
        startCursor = pageInfo['startCursor']
        while hasNextPage:
            # 避免请求过快被服务器拒绝
            time.sleep(delay)

            # 发起下一次请求
            json_data['variables']['after'] = endCursor
            response = await self.client.post(url=url, params=params, json=json_data)
            artworks = response.json()['data']['artworks']

            # 累加作品集数据
            edges.extend(artworks['edges'])

            # 更新分页信息
            pageInfo = artworks['pageInfo']

            hasNextPage = pageInfo['hasNextPage']
            hasPreviousPage = pageInfo['hasPreviousPage']
            endCursor = pageInfo['endCursor']
            startCursor = pageInfo['startCursor']

        return edges

    async def raw_artworks_by_daily(
        self,
        query: str = '',
        delay: float = 0.5,
        start_day: str | None = None,
        end_day: str | None = None,
    ) -> list[dict]:
        """
        获取作品集元数据，并通过时间段筛选

        Args:
            query (str, optional): 关键字搜索参数. Defaults to ''.
            delay (float, optional): 爬虫延时，单位为秒，避免请求过快被服务器拒绝. Defaults to 0.5.
            start_day (str, optional): 起始日期，格式为 'YYYY-MM-DD'，用于筛选作品集. Defaults to None，默认从第一条记录的时间开始.
            end_day (str, optional): 结束日期，格式为 'YYYY-MM-DD'，用于筛选作品集. Defaults to None，默认到最后一条记录的时间结束.

        Returns:
            list[dict]: 作品集元数据
            
        Return json format please see `raw_artworks` method.
        """
        url = '/graphql'
        params = {
            'operation': 'listArtworks',
        }
        #!Note: post 表单不能同时提供 first 和 last 参数，否则引发以下异常
        """
        !provide first and last args:
        {'errors': [{'message': 'Not support both first and last provided.',
        'locations': [{'line': 3, 'column': 3}],
        'path': ['artworks'],
        'extensions': {'code': 'INVALID_PAGINATION_INPUT',
            'exception': {'message': 'Not support both first and last provided.'}}}],
        'data': None}
        """
        #!Note: 浏览器控制台中，SortType.TRENDING 与 SortType.LATEST 默认使用的为 before 和 last 参数，SortType.DAILY 与 SortType.MOST_LIKE 默认使用的是 after 和 first 参数
        #!但经测试，所有 SortType 均可使用 before 和 last 参数，after 和 first 参数，其中 after 和 first 为一固定的参数组合，before 和 last 为一固定的参数组合
        json_data = {
            'query':
            '\n    query listArtworks($before: String, $after: String, $first: Int, $last: Int, $orderBy: String, $isNsfw: Boolean, $tag: String, $q: String, $relevantArtworkId: ID, $keyword: String, $text: String, $hidePrompts: Boolean, $isSafeSearch: Boolean, $feed: String, $authorId: ID, $challenge: Int, $archived: Boolean, $isPrivate: Boolean, $i2vPro: Boolean, $animatedBaseArtworkId: ID, $modelId: ID, $modelVersionId: ID, $loraId: ID, $loraVersionId: ID, $workflowId: ID, $workflowVersionId: ID, $time: DateRange, $type: ArtworkType, $types: [ArtworkType], $rankMediaType: RankMediaType, $worldId: ID, $characterId: ID) {\n  artworks(\n    before: $before\n    after: $after\n    first: $first\n    last: $last\n    orderBy: $orderBy\n    isNsfw: $isNsfw\n    tag: $tag\n    q: $q\n    relevantArtworkId: $relevantArtworkId\n    keyword: $keyword\n    text: $text\n    hidePrompts: $hidePrompts\n    isSafeSearch: $isSafeSearch\n    feed: $feed\n    authorId: $authorId\n    challenge: $challenge\n    archived: $archived\n    isPrivate: $isPrivate\n    i2vPro: $i2vPro\n    animatedBaseArtworkId: $animatedBaseArtworkId\n    modelId: $modelId\n    modelVersionId: $modelVersionId\n    loraId: $loraId\n    loraVersionId: $loraVersionId\n    worldId: $worldId\n    characterId: $characterId\n    workflowId: $workflowId\n    workflowVersionId: $workflowVersionId\n    time: $time\n    type: $type\n    types: $types\n    rankMediaType: $rankMediaType\n  ) {\n    edges {\n      node {\n        ...ArtworkWithMangaPreview\n      }\n      cursor\n    }\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      endCursor\n      startCursor\n    }\n  }\n}\n    \n    fragment ArtworkWithMangaPreview on Artwork {\n  ...ArtworkPreview\n  manga {\n    ...MangaBase\n    likedCount\n    liked\n    chapter(index: 0) {\n      ...MangaChapterBase\n    }\n  }\n}\n    \n\n    fragment ArtworkPreview on Artwork {\n  ...ArtworkBase\n  likedCount\n  liked\n  commentCount\n  author {\n    ...UserBase\n  }\n  flag {\n    ...ModerationFlagDetail\n  }\n}\n    \n\n    fragment ArtworkBase on Artwork {\n  __typename\n  id\n  title\n  authorId\n  prompts\n  createdAt\n  updatedAt\n  mediaId\n  media {\n    ...MediaBase\n  }\n  videoMediaId\n  hidePrompts\n  isPrivate\n  isNsfw\n  isSensitive\n  extra\n  type\n  paidCredit\n  aesScore\n  flag {\n    ...ModerationFlagDetail\n  }\n}\n    \n\n    fragment MediaBase on Media {\n  id\n  type\n  width\n  height\n  urls {\n    variant\n    url\n  }\n  imageType\n  fileUrl\n  duration\n  thumbnailUrl\n  hlsUrl\n  size\n  flag {\n    ...ModerationFlagPreview\n  }\n}\n    \n\n    fragment ModerationFlagPreview on ModerationFlag {\n  shouldBlur\n}\n    \n\n    fragment ModerationFlagDetail on ModerationFlag {\n  status\n  isSensitive\n  isMinors\n  isRealistic\n  isFlagged\n  isSexyPic\n  isSexyText\n  shouldBlur\n  isWarned\n  isAppealable\n}\n    \n\n    fragment UserBase on User {\n  id\n  email\n  emailVerified\n  username\n  displayName\n  createdAt\n  updatedAt\n  avatarMediaId\n  membership {\n    membershipId\n    tier\n  }\n  deleteAfter\n  isAdmin\n  aprilFoolsDayProfile: profile(key: "aprilFoolsDay2025")\n  springEventProfile: profile(key: "springEvent2025")\n}\n    \n\n    fragment MangaBase on Manga {\n  __typename\n  id\n  authorId\n  title\n  description\n  coverMediaId\n  coverMedia {\n    ...MediaBase\n  }\n  isNsfw\n  isPrivate\n  isArchived\n  type\n  extra\n  createdAt\n  updatedAt\n  artworkId\n}\n    \n\n    fragment MangaChapterBase on MangaChapter {\n  id\n  mangaId\n  order\n  title\n  coverMediaId\n  coverMedia {\n    ...MediaBase\n  }\n  originalData\n  content\n  createdAt\n  updatedAt\n}\n    ',
            'variables': {
                'after': '',
                'first': 24,
                'isSafeSearch': True,
                'q': query,
            },
        }
        # 采用关键字搜索的每日排名策略，但将时间跨度从原先 API 默认的一周更改至用户指定的时间段
        json_data['variables']['orderBy'] = SortType.MOST_LIKE.value
        # 获取指定时间段的作品集
        start_day: datetime = datetime.strptime(start_day, '%Y-%m-%d') if start_day is not None else datetime(2022, 1, 1)  # 网站上线时间（粗略）
        end_day: datetime = datetime.strptime(end_day, '%Y-%m-%d') if end_day is not None else datetime.now()  # 当前时间
        if start_day > end_day:
            raise ValueError("start_day must be earlier than end_day")
        # 'time': {  # 注意：gt 和 lt 的值必须是 ISO 8601 格式的字符串，且必须包含毫秒部分
        #     'gt': '2025-07-08T16:00:00.000Z',
        #     'lt': '2025-07-16T16:00:00.000Z',
        # },
        # 将时间转换为 ISO 8601 格式的字符串，固定毫秒部分为 .000
        start_day_iso = start_day.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end_day_iso = end_day.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        json_data['variables']['time'] = {
            'gt': start_day_iso,
            'lt': end_day_iso,
        }
        response = await self.client.post(url=url, params=params, json=json_data)

        # 作品集
        artworks = response.json()['data']['artworks']

        # 主体数据
        edges: list[dict] = artworks['edges']
        # 分页信息
        pageInfo: dict = artworks['pageInfo']

        # 判断是否存在下一页，并获取 endCursor 作为请求下一页的 json 表单参数
        hasNextPage = pageInfo['hasNextPage']
        hasPreviousPage = pageInfo['hasPreviousPage']
        endCursor = pageInfo['endCursor']
        startCursor = pageInfo['startCursor']
        while hasNextPage:
            # 避免请求过快被服务器拒绝
            time.sleep(delay)

            # 发起下一次请求
            json_data['variables']['after'] = endCursor
            response = await self.client.post(url=url, params=params, json=json_data)
            artworks = response.json()['data']['artworks']

            # 累加作品集数据
            edges.extend(artworks['edges'])

            # 更新分页信息
            pageInfo = artworks['pageInfo']

            hasNextPage = pageInfo['hasNextPage']
            hasPreviousPage = pageInfo['hasPreviousPage']
            endCursor = pageInfo['endCursor']
            startCursor = pageInfo['startCursor']

        return edges

    async def concurrent_raw_artworks_by_daily(
        self,
        query: str = '',
        delay: float = 0.5,
        start_day: str | None = None,
        end_day: str | None = None,
        max_concurrency_num: int = 8,
    ) -> list[dict]:
        """
        与 `raw_artworks_by_daily` 方法相同，但采用对时间片切分以及批量并发的方式获取作品集元数据

        Args:
            query (str, optional): 关键字搜索参数. Defaults to ''.
            delay (float, optional): 爬虫延时，单位为秒，避免请求过快被服务器拒绝. Defaults to 0.5.
            start_day (str, optional): 起始日期，格式为 'YYYY-MM-DD'，用于筛选作品集. Defaults to None，默认从第一条记录的时间开始.
            end_day (str, optional): 结束日期，格式为 'YYYY-MM-DD'，用于筛选作品集. Defaults to None，默认到最后一条记录的时间结束.
            max_concurrency_num (int, optional): 最大并发数. Defaults to 8.

        Returns:
            list[dict]: 作品集元数据
            
        Return json format please see `raw_artworks` method.
        """
        # 获取指定时间段的作品集
        start_day: datetime = datetime.strptime(start_day, '%Y-%m-%d') if start_day is not None else datetime(2022, 1, 1)  # 网站上线时间（粗略）
        end_day: datetime = datetime.strptime(end_day, '%Y-%m-%d') if end_day is not None else datetime.now()  # 当前时间
        if start_day > end_day:
            raise ValueError("start_day must be earlier than end_day")
        # 按照并发数量进行时间片切分
        time_slices: list[tuple[datetime, datetime]] = []  # 时间片序列
        time_step = (end_day - start_day) / max_concurrency_num  # 时间片步长
        current_start = start_day
        while current_start < end_day:
            current_end = current_start + time_step
            time_slices.append((current_start, current_end))
            current_start = current_end
        # 并发获取每个时间片的作品集元数据
        tasks = [
            self.raw_artworks_by_daily(
                query=query,
                delay=delay,
                start_day=current_start.strftime('%Y-%m-%d'),
                end_day=current_end.strftime('%Y-%m-%d'),
            ) for current_start, current_end in time_slices
        ]
        results: list[list[dict]] = await asyncio.gather(*tasks)
        return [item for result in results for item in result]
