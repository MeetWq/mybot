import re
from nonebot import export, on_startswith
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.log import logger

from .data_source import get_image

export = export()
export.description = '头像相关表情生成'
export.usage = 'Usage:\n  摸/撕 {qq/@user}'
export.help = export.description + '\n' + export.usage

petpet = on_startswith('摸', priority=26)
tear = on_startswith('撕', priority=26)


@petpet.handle()
@tear.handle()
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
        msg_content = re.sub(r'[摸撕]', '', msg_text).strip()
        if msg_content.isdigit():
            qq = msg_content
    logger.debug(qq)
    if qq:
        command = msg_text[0]
        types = {'摸': 'petpet', '撕': 'tear'}
        if command in types:
            type = types[command]
            logger.debug(type)
            img_path = await get_image(qq, type)
            if img_path:
                await bot.send(event=event, message=MessageSegment.image(file='file://' + img_path))
            else:
                await bot.send(event=event, message='出错了，请稍后再试')
