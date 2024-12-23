from typing import Annotated

from nonebot import on_command, require
from nonebot.adapters import Bot, Event, Message
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import CommandArg, Depends
from nonebot.permission import SUPERUSER, Permission
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_uninfo")

from nonebot_plugin_uninfo import Uninfo

from src.utils.plugin_manager import ManageType, plugin_manager

__plugin_meta__ = PluginMetadata(
    name="插件管理",
    description="启用/禁用插件",
    usage="启用插件/禁用插件 插件名",
    extra={
        "example": "禁用插件 setu",
        "notice": "仅管理员或超级用户可用",
    },
)


def _uninfo_role(session: Uninfo) -> bool:
    return session.scene.is_private or bool(
        session.member and session.member.role and session.member.role.level > 1
    )


PERM_EDIT = SUPERUSER | Permission(_uninfo_role)
PERM_GLOBAL = SUPERUSER


block = on_command("禁用插件", block=True, priority=11, permission=PERM_EDIT)
unblock = on_command("启用插件", block=True, priority=11, permission=PERM_EDIT)
block_gl = on_command("全局禁用插件", block=True, priority=11, permission=PERM_GLOBAL)
unblock_gl = on_command("全局启用插件", block=True, priority=11, permission=PERM_GLOBAL)
set_mode = on_command("设置插件模式", block=True, priority=11, permission=PERM_GLOBAL)


def get_user_id(uninfo: Uninfo) -> str:
    return f"{uninfo.scope}_{uninfo.self_id}_{uninfo.scene_path}"


UserId = Annotated[str, Depends(get_user_id)]


@run_preprocessor
async def _(matcher: Matcher, user_id: UserId):
    plugin = matcher.plugin_name

    if plugin and not plugin_manager.check(plugin, user_id):
        reason = f"Manager has blocked '{plugin}'"
        logger.debug(reason)
        raise IgnoredException(reason)


def IsSuperUser():
    async def dependency(bot: Bot, event: Event):
        return event.get_user_id() in bot.config.superusers

    return Depends(dependency)


@block.handle()
async def _(
    matcher: Matcher,
    user_id: UserId,
    msg: Message = CommandArg(),
    is_superuser: bool = IsSuperUser(),
):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return

    plugin_name = plugin_manager.find(keyword)
    if not plugin_name:
        await matcher.finish(f"插件 {keyword} 不存在！")

    plugin_config = plugin_manager.get_config(plugin_name)
    if not plugin_config:
        await matcher.finish(f"插件 {keyword} 不存在！")

    mode = plugin_config.mode
    if not ((mode & 2) or is_superuser):
        await matcher.finish(f"插件 {plugin_name} 已关闭编辑权限！")

    if plugin_manager.block(plugin_name, user_id):
        await matcher.finish(f"插件 {plugin_name} 禁用成功")
    else:
        await matcher.finish(f"插件 {plugin_name} 禁用失败")


@unblock.handle()
async def _(
    matcher: Matcher,
    user_id: UserId,
    msg: Message = CommandArg(),
    is_superuser: bool = IsSuperUser(),
):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return

    plugin_name = plugin_manager.find(keyword)
    if not plugin_name:
        await matcher.finish(f"插件 {keyword} 不存在！")

    plugin_config = plugin_manager.get_config(plugin_name)
    if not plugin_config:
        await matcher.finish(f"插件 {keyword} 不存在！")

    mode = plugin_config.mode
    if not ((mode & 2) or is_superuser):
        await matcher.finish(f"插件 {plugin_name} 已关闭编辑权限！")

    if plugin_manager.unblock(plugin_name, user_id):
        await matcher.finish(f"插件 {plugin_name} 启用成功")
    else:
        await matcher.finish(f"插件 {plugin_name} 启用失败")


@block_gl.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return

    plugin_name = plugin_manager.find(keyword)
    if not plugin_name:
        await matcher.finish(f"插件 {keyword} 不存在！")

    if plugin_manager.change_manage_type(plugin_name, ManageType.WHITE):
        await matcher.finish(f"插件 {plugin_name} 已设为白名单模式")
    else:
        await matcher.finish(f"插件 {plugin_name} 设置失败")


@unblock_gl.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return

    plugin_name = plugin_manager.find(keyword)
    if not plugin_name:
        await matcher.finish(f"插件 {keyword} 不存在！")

    if plugin_manager.change_manage_type(plugin_name, ManageType.BLACK):
        await matcher.finish(f"插件 {plugin_name} 已设为黑名单模式")
    else:
        await matcher.finish(f"插件 {plugin_name} 设置失败")


@set_mode.handle()
async def _(
    matcher: Matcher,
    msg: Message = CommandArg(),
):
    message = msg.extract_plain_text().strip()
    if not message:
        return
    args = message.split()
    if len(args) != 2 or not args[1].isdigit():
        await matcher.finish("参数错误！")
    keyword, mode = args
    mode = int(mode)

    plugin_name = plugin_manager.find(keyword)
    if not plugin_name:
        await matcher.finish(f"插件 {keyword} 不存在！")

    if plugin_manager.change_mode(plugin_name, mode):
        await matcher.finish(f"插件 {plugin_name} 模式已设为 {mode}")
    else:
        await matcher.finish(f"插件 {plugin_name} 设置失败")
