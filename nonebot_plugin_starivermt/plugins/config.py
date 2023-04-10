from pydantic import BaseModel, Extra
from nonebot import get_driver
from typing import List


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    stariver_api_token: str = ""
    stariver_api_endpoint: str = "https://dl-dev.ap-sh.starivercs.com"
    sync_task_uri: str = "/v2/manga_trans/normal/sync_task"
    async_create_uri: str = "/v2/manga_trans/normal/create_task"
    async_query_uri: str = "/v2/manga_trans/normal/query_task"
    advanced_manual_translate_uri: str = "/v2/manga_trans/advanced/manual_translate"
    advanced_rendering: str = "/v2/manga_trans/advanced/text_render"
    super_user: List[str] = []

bot_config = Config.parse_obj(get_driver().config.dict())