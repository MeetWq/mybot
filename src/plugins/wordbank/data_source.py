import re
import json
from pathlib import Path
from typing import Optional, List


OPTIONS = ['full', 'regex', 'include']
NULL_BANK = dict((option, {"0": {}}) for option in OPTIONS)


class WordBank():
    def __init__(self):
        dir_path = Path('data/wordbank')
        self.data_path = dir_path / 'bank.json'

        if self.data_path.exists():
            with self.data_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            self.__data = {key: data.get(key) or {"0": {}}
                           for key in NULL_BANK.keys()}
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            self.__data = NULL_BANK
            self.__save()

    def match(self, user_id: str, msg: str) -> Optional[List]:
        """
        匹配词条，匹配顺序：全匹配->正则匹配->模糊匹配
        :param user_id: 为'0'时是全局词库
        :param msg: 需要匹配的消息
        :return: 首先匹配成功的消息列表
        """
        for flag in range(len(OPTIONS)):
            res = self.__match(user_id, msg, flag)
            if res:
                return res

    def __match(self, user_id: str, msg: str, flag: int = 0) -> Optional[List]:
        """
        匹配词条
        :param flag: 0: 全匹配（full）（默认）
                     1: 正则匹配（regex）
                     2: 模糊匹配（include）
        """
        type = OPTIONS[flag]
        bank = dict(self.__data[type].get(user_id, {}),
                    **self.__data[type].get("0", {}))

        if flag == 0:
            return bank.get(msg, [])
        elif flag == 1:
            for key in bank:
                try:
                    if re.search(rf"{key}", msg, re.S):
                        return bank[key]
                except:
                    continue
        elif flag == 2:
            for key in bank:
                if key in msg:
                    return bank[key]

    def __save(self):
        with self.data_path.open('w', encoding='utf-8') as f:
            json.dump(self.__data, f, ensure_ascii=False, indent=4)

    def add(self, user_id: str, key: str, value: str, flag: int = 0) -> bool:
        """
        新增词条
        :param key: 触发短语
        :param value: 触发后发送的短语
        """
        type = OPTIONS[flag]

        if self.__data[type].get(user_id, {}):
            if self.__data[type][user_id].get(key, []):
                self.__data[type][user_id][key].append(value)
            else:
                self.__data[type][user_id][key] = [value]
        else:
            self.__data[type][user_id] = {key: [value]}

        self.__save()
        return True

    def remove(self, user_id: str, key: str) -> bool:
        """
        删除词条
        """
        status = False
        for type in self.__data:
            if self.__data[type].get(user_id, {}).get(key, False):
                del self.__data[type][user_id][key]
                status = True
        self.__save()
        return status

    def clear(self, user_id: str) -> bool:
        """
        清空某个对象的词库
        """
        status = False
        for type in self.__data:
            if self.__data[type].get(user_id, {}):
                del self.__data[type][user_id]
                status = True
        self.__save()
        return status

    def clear_all(self):
        """
        清空所有词库
        """
        self.__data = NULL_BANK
        self.__save()
        return True
