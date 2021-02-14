from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import search_song_id

music = on_command('music', aliases={'点歌', '来一首', '点一首'}, priority=15)


@music.handle()
@music.args_parser
async def _(bot: Bot, event: Event, state: T_State):
    keyword = str(event.get_message()).strip()
    if keyword:
        state['keyword'] = keyword


@music.got('keyword', prompt='你想听什么歌呢？')
async def _(bot: Bot, event: Event, state: T_State):
    keyword = state['keyword']
    song_id = await search_song_id(keyword)
    if song_id:
        await music.send(message=MessageSegment("music", {"type": "qq", "id": str(song_id)}))
    else:
        await music.finish('没有找到这首歌呢')
