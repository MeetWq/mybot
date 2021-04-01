from nonebot import on_notice
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, FriendRequestEvent, GroupRequestEvent


async def friend_add_rule(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, FriendRequestEvent)


friend_add = on_notice(rule=friend_add_rule, priority=14)


@friend_add.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, FriendRequestEvent):
        user_id = event.user_id
        await event.approve()
        await bot.send_private_msg(bot.config.superusers[0], message=f'{user_id} 请求加为好友，已自动通过')


async def group_add_rule(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, GroupRequestEvent)


group_add = on_notice(rule=group_add_rule, priority=14)


@group_add.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, GroupRequestEvent):
        user_id = event.user_id
        group_id = event.group_id
        if user_id in bot.config.superusers:
            await event.approve()
        else:
            await bot.send_private_msg(bot.config.superusers[0], message=f'{user_id} 邀请加入群聊 {group_id}')
            await event.reject(reason=f'邀请加群请联系 {bot.config.superusers[0]}')
