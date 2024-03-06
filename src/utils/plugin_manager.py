from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from nonebot import get_driver
from nonebot.log import logger
from nonebot.plugin import Plugin, get_loaded_plugins
from pydantic import BaseModel, field_serializer

config_path = Path("data/plugin_manager.yml")


class ManageType(IntEnum):
    BLACK = 0
    WHITE = 1


class PluginConfig(BaseModel):
    mode: int = 7
    manage_type: ManageType = ManageType.BLACK
    white_list: List[str] = []
    black_list: List[str] = []

    @field_serializer("manage_type")
    def get_eunm_value(self, v: ManageType, info) -> int:
        return v.value


class PluginManager:
    def __init__(self, path: Path = config_path):
        self.__path = path
        self.__plugin_list: Dict[str, PluginConfig] = {}
        self.__plugins: List[Plugin] = []

    def block(self, plugin_name: str, user_id: str) -> bool:
        if plugin_name not in self.__plugin_list:
            return False
        config = self.__plugin_list[plugin_name]
        manage_type = config.manage_type
        if manage_type == ManageType.BLACK and user_id not in config.black_list:
            config.black_list.append(user_id)
        if manage_type == ManageType.WHITE and user_id in config.white_list:
            config.white_list.remove(user_id)
        self.__dump()
        return True

    def unblock(self, plugin_name: str, user_id: str) -> bool:
        if plugin_name not in self.__plugin_list:
            return False
        config = self.__plugin_list[plugin_name]
        manage_type = config.manage_type
        if manage_type == ManageType.WHITE and user_id not in config.white_list:
            config.white_list.append(user_id)
        if manage_type == ManageType.BLACK and user_id in config.black_list:
            config.black_list.remove(user_id)
        self.__dump()
        return True

    def change_mode(self, plugin_name: str, mode: int) -> bool:
        if plugin_name not in self.__plugin_list:
            return False
        if not (0 <= mode <= 7):
            return False
        self.__plugin_list[plugin_name].mode = mode
        self.__dump()
        return True

    def change_manage_type(self, plugin_name: str, manage_type: ManageType) -> bool:
        if plugin_name not in self.__plugin_list:
            return False
        self.__plugin_list[plugin_name].manage_type = manage_type
        self.__dump()
        return True

    def get_config(self, plugin_name: str) -> Optional[PluginConfig]:
        return self.__plugin_list.get(plugin_name)

    def check(self, plugin_name: str, user_id: str) -> bool:
        if plugin_name not in self.__plugin_list:
            return False
        config = self.__plugin_list[plugin_name]
        if not (config.mode & 1):
            return False
        if config.manage_type == ManageType.BLACK:
            if user_id in config.black_list:
                return False
            return True
        elif config.manage_type == ManageType.WHITE:
            if user_id in config.white_list:
                return True
            return False
        return False

    def find(self, keyword: str) -> Optional[str]:
        for p in self.__plugins[::-1]:
            names = [p.name.lower()]
            if metadata := p.metadata:
                names.append(metadata.name.lower())
                unique_name = metadata.extra.get("unique_name")
                if not unique_name:
                    unique_name = (
                        p.name.replace("nonebot_plugin_", "")
                        .replace("nonebot-plugin-", "")
                        .replace("nonebot_", "")
                        .replace("nonebot-", "")
                    )
                names.append(str(unique_name).lower())
            if keyword.lower() in names:
                return p.name

    def init(self):
        raw_list: Dict[str, Any] = {}
        if self.__path.exists():
            with self.__path.open("r", encoding="utf-8") as f:
                try:
                    raw_list = yaml.safe_load(f)
                except Exception:
                    logger.warning("插件列表解析失败")
                    raise
        try:
            plugin_list = {
                name: PluginConfig.model_validate(config)
                for name, config in raw_list.items()
            }
        except Exception:
            logger.warning("插件列表解析失败")
            raise

        self.__plugins = list(get_loaded_plugins())
        for plugin in self.__plugins:
            plugin_config = PluginConfig()
            if not plugin.metadata or not plugin.matcher:
                plugin_config.mode &= 3
            self.__plugin_list[plugin.name] = plugin_config

        self.__plugin_list.update(plugin_list)
        self.__dump()

    def __dump(self):
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        plugin_list = {
            name: config.model_dump() for name, config in self.__plugin_list.items()
        }
        with self.__path.open("w", encoding="utf-8") as f:
            yaml.dump(plugin_list, f, allow_unicode=True)


plugin_manager = PluginManager()

driver = get_driver()


@driver.on_startup
def _():
    plugin_manager.init()
    logger.info("插件管理器初始化完成")
