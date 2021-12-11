import os
from nonebot import export, on_endswith, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_random_emoji, make_emoji, emojis


end_jpg = on_endswith('.jpg', priority=30)


@end_jpg.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msgs = event.get_message()
    if len(msgs) > 1:
        return
    keyword = str(msgs).strip()
    keyword = os.path.splitext(keyword)[0]
    if len(keyword) > 20:
        return
    img_url = await get_random_emoji(keyword)
    if not img_url:
        await end_jpg.finish('找不到相关的图片')
    await end_jpg.finish(MessageSegment.image(file=img_url))


emoji_parser = ArgumentParser()
emoji_parser.add_argument('-t', '--type', type=str)
emoji_parser.add_argument('text', nargs='+')

emoji = on_shell_command(
    'emoji', aliases={'表情包'}, parser=emoji_parser, priority=31)


@emoji.handle()
async def _(bot: Bot, event: Event, state: T_State):
    help_msg = 'Usage:\n  emoji -t {type} {text}，发送 "emoji list" 查看支持的表情包列表'

    args = state['args']
    if not hasattr(args, 'text'):
        await emoji.finish()

    if args.text[0] == 'list':
        message = '支持的表情包：'
        for i, e in enumerate(emojis):
            message += f"\n{i}. {'/'.join(e['names'])}，需要 {e['input_num']} 个输入"
        await emoji.finish(message)

    if not args.type:
        await emoji.finish()

    type = str(args.type)
    num = -1
    if type.isdigit() and 0 <= int(type) < len(emojis):
        num = int(type)
    else:
        for i, e in enumerate(emojis):
            if type in e['names']:
                num = i
    if num == -1:
        await emoji.finish(help_msg)

    texts = args.text
    if len(texts) != emojis[num]['input_num']:
        await emoji.finish(f"该表情包需要 {emojis[num]['input_num']} 个输入")

    msg = await make_emoji(num, texts)
    await emoji.finish(msg)
