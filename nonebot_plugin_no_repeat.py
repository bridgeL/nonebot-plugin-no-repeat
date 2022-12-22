from time import time
from typing import Dict, List, Literal
from loguru import logger
from pydantic import BaseModel
from nonebot import get_driver
from nonebot.adapters import Bot
from nonebot.exception import MockApiException


class Config(BaseModel):
    no_repeat_mode: Literal["use", "not_use"] = "not_use"
    no_repeat_groups: List[int] = []
    no_repeat_threshold: int = 3
    no_repeat_gap: int = 20


config = Config.parse_obj(get_driver().config.dict())


class Cache(BaseModel):
    last: str = ""
    last_time: int = 0
    cnt: int = 0

    def check_gap(self):
        '''是否小于规定间隔'''
        t1 = int(time())
        t2 = self.last_time
        self.last_time = t1
        return t1 - t2 <= config.no_repeat_gap

    def check_same_msg(self, msg: str):
        '''是否与上次相同'''
        last = self.last
        self.last = msg
        return msg == last

    def add(self, msg: str):
        f1 = self.check_gap()
        f2 = self.check_same_msg(msg)
        # 小于规定间隔 且 与上次相同
        if f1 and f2:
            self.cnt += 1
        else:
            self.cnt = 1

    def check_cnt(self):
        # 达到复读标准
        return self.cnt >= config.no_repeat_threshold


groups: Dict[int, Cache] = {}


def msg_is_send_to_group(api: str, data: dict):
    if api == "send_group_msg":
        return True
    if api == "send_msg":
        return data["message_type"] == "group"
    return False


def get_group_cache(group_id: int):
    if group_id not in groups:
        groups[group_id] = Cache()
    return groups[group_id]


def group_id_is_using_no_repeat(group_id: int):
    if config.no_repeat_mode == "not_use":
        return group_id not in config.no_repeat_groups
    return group_id in config.no_repeat_groups


@Bot.on_calling_api
async def handle_api_call(bot: Bot, api: str, data: dict):
    if msg_is_send_to_group(api, data):
        group_id = data["group_id"]
        if group_id_is_using_no_repeat(group_id):
            cache = get_group_cache(group_id)
            cache.add(str(data["message"]))
            if cache.check_cnt():
                logger.warning(cache)
                logger.warning("检测到复读，疑似代码故障")
                raise MockApiException("已阻止api调用")
