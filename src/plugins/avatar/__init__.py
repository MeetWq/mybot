import re
from nonebot import export, on_startswith
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.log import logger

from .data_source import get_image

export = export()
export.description = '头像相关表情生成'
export.usage = 'Usage:\n  摸/撕/丢/爬 {qq/@user/自己}'
export.help = export.description + '\n' + export.usage

petpet = on_startswith('摸', priority=26)
tear = on_startswith('撕', priority=26)
throw = on_startswith('丢', priority=26)
crawl = on_startswith('爬', priority=26)


@petpet.handle()
@tear.handle()
@throw.handle()
@crawl.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = event.get_message()
    msg_text = event.get_plaintext().strip()
    logger.debug(msg_text)
    qq = ''
    for msg_seg in msg:
        if msg_seg.type == 'at':
            qq = msg_seg.data['qq']
            break
    if not qq:
        msg_content = re.sub(r'[摸撕丢爬]', '', msg_text).strip()
        if msg_content.isdigit():
            qq = msg_content
        elif msg_content == '自己':
            qq = event.user_id
    logger.debug(qq)
    if qq:
        command = msg_text[0]
        types = {'摸': 'petpet', '撕': 'tear', '丢': 'throw', '爬': 'crawl'}
        if command in types:
            type = types[command]
            logger.debug(type)
            img_path = await get_image(qq, type)
            if img_path:
                await bot.send(event=event, message=MessageSegment.image(file='file://' + img_path))
            else:
                await bot.send(event=event, message='出错了，请稍后再试')
