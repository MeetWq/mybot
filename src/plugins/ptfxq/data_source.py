import re
import aiohttp
from pathlib import Path
from pytz import timezone
from bs4 import BeautifulSoup
from datetime import datetime
from nonebot.adapters.cqhttp import Message, MessageSegment

data_path = Path('data/ptfxq')
if not data_path.exists():
    data_path.mkdir(parents=True)
time_path = data_path / 'last_time.log'


async def get_msgs():
    if not time_path.exists():
        update_last_time(datetime.now())

    url = 'https://t.me/s/Ptfxq'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            result = await resp.text()
    result = BeautifulSoup(result, 'lxml')
    messages = result.find_all('div', {'class': 'tgme_widget_message'})
    last_time = get_last_time()
    new_messages = [m for m in messages if get_time(m) > last_time]
    if new_messages:
        update_last_time(get_time(new_messages[-1]))
    new_messages = [format_msg(m) for m in new_messages]
    return new_messages


def format_msg(message):
    message_photos = message.find_all('a', {'class': 'tgme_widget_message_photo_wrap'})
    photos = [re.search(r'url\([\'"](.*?)[\'"]\)', m.get('style')).group(1) for m in message_photos]

    message_texts = message.find_all('div', {'class': 'tgme_widget_message_text'})
    texts = [m.text for m in message_texts]

    message_links = message.find_all('a', {'class': 'tgme_widget_message_link_preview'})
    links = [m.text for m in message_links]

    msg = Message()
    time = get_time(message).strftime("%y/%m/%d %H:%M:%S")
    msg.append(f'PT风向旗 {time}\n')
    for photo in photos:
        msg.append(MessageSegment.image(file=photo))
    for text in texts:
        msg.append('\n' + text)
    for link in links:
        msg.append('\n\n------------------' + link)
    return msg


def get_time(message):
    time = message.find('a', {'class': 'tgme_widget_message_date'}).find('time').get('datetime')
    return datetime.fromisoformat(time).astimezone(timezone('Asia/Shanghai'))


def get_last_time():
    with time_path.open('r') as f:
        last_time = f.read().strip()
    return datetime.fromisoformat(last_time)


def update_last_time(time):
    last_time = time.astimezone(timezone('Asia/Shanghai')).isoformat()
    with time_path.open('w') as f:
        f.write(last_time)
