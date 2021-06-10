from nonebot import export, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import search_song

export = export()
export.description = '点歌'
export.usage = 'Usage:\n  music/点歌 [options] {song}'
export.options = 'Options:\n  -s, --source 音乐来源，目前支持QQ音乐(qq)、网易云音乐(netease)、酷狗音乐(kugou)、咪咕音乐(migu)、B站(bilibili)'
export.help = export.description + '\n' + export.usage + '\n' + export.options

music_parser = ArgumentParser()
music_parser.add_argument('-s', '--source', default='all')
music_parser.add_argument('song', nargs='+')

music = on_shell_command('music', aliases={'点歌'}, parser=music_parser, priority=29)

sources = ['qq', 'netease', 'kugou', 'migu', 'bilibili']


@music.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'song'):
        await music.finish(export.usage)

    song = args.song
    song = ' '.join(song)
    if not song:
        await music.finish(export.usage)

    source = args.source
    if source == 'all':
        for s in sources:
            msg = await search_song(song, s)
            if msg:
                await music.send(message=msg)
                await music.finish()
        await music.finish('没有找到这首歌')
    elif source not in sources:
        await music.finish(export.options)
    else:
        msg = await search_song(song, source)
        if msg:
            await music.send(message=msg)
            await music.finish()
        await music.finish(source + '中没有找到这首歌')
