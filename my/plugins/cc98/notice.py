# import nonebot
# import re
# import time
# from nonebot import scheduler
#
# from .users import default_user
#
#
# class Users:
#     def __init__(self, nickname, qq):
#         self.nickname = nickname
#         self.qq = qq
#
# users = [Users('W.Q', 1875806843), Users('BrightHammer', 1214312182)]
#
# new_topics_id = []
#
# @scheduler.scheduled_job('interval', id='notice', minutes=5, misfire_grace_time=60)
# async def notice():
#     bot = nonebot.get_bot()
#     # board_id = 744
#     # topics = default_user.api.board_topic(board_id, from_=0, size=10)
#
#     try:
#         topics = default_user.api.topic_new(from_=0, size=20)
#     except Exception:
#         return
#
#     new_topics = []
#     # time_now = time.time()
#     for topic in topics:
#         # time_str = re.split('[.+]', topic['time'])[0]
#         # time_topic = time.mktime(time.strptime(time_str, "%Y-%m-%dT%H:%M:%S"))
#         # if time_now - time_topic < 300:
#         #     new_topics.append(topic)
#         if topic['id'] not in new_topics_id:
#             new_topics.append(topic)
#             new_topics_id.append(topic['id'])
#             if len(new_topics_id) > 40:
#                 new_topics_id.pop(0)
#
#     wealth_topics = []  # 98 米
#     bonus_topics = []   # NHD 魔力值
#     grab_topics = []    # 抢楼
#     for topic in new_topics:
#         title = topic['title']
#
#         try:
#             post = default_user.api.topic_post(topic['id'], from_=0, size=1)[0]
#         except Exception:
#             return
#
#         content = post['content']
#
#         if '发米' in title or '送米' in title or '散米' in title or \
#             ('财富值' in title and ('散' in title or '送' in title or '发' in title)):
#             wealth_topics.append(topic)
#
#         if ('魔力值' in title and
#             ('散' in title or '送' in title or '发' in title or '领' in title or '撒' in title)) \
#                 or '散魔' in title:
#             bonus_topics.append(topic)
#         elif '散魔力值' in content or '送魔力值' in content or '发魔力值' in content or '散魔' in content:
#             bonus_topics.append(topic)
#
#         if '抢楼' in title or '盖楼' in title:
#             grab_topics.append(topic)
#
#     for topic in wealth_topics:
#         topic_time = re.split('[T.+]', topic['time'])
#         topic_time = '[' + topic_time[0].replace('-', '/') + ' ' + topic_time[1] + ']'
#         msg = '98米提醒：\n'
#         msg += topic['title'] + '\n'
#         msg += topic_time + '\n'
#         msg += 'https://www.cc98.org/topic/' + str(topic['id'])
#         for user in users:
#             await bot.send_private_msg(user_id=user.qq, message=msg)
#
#     for topic in bonus_topics:
#         topic_time = re.split('[T.+]', topic['time'])
#         topic_time = '[' + topic_time[0].replace('-', '/') + ' ' + topic_time[1] + ']'
#         msg = '散魔力值提醒：\n'
#         msg += topic['title'] + '\n'
#         msg += topic_time + '\n'
#         msg += 'https://www.cc98.org/topic/' + str(topic['id'])
#         for user in users:
#             await bot.send_private_msg(user_id=user.qq, message=msg)
#
#     for topic in grab_topics:
#         topic_time = re.split('[T.+]', topic['time'])
#         topic_time = '[' + topic_time[0].replace('-', '/') + ' ' + topic_time[1] + ']'
#         msg = '抢楼提醒：\n'
#         msg += topic['title'] + '\n'
#         msg += topic_time + '\n'
#         msg += 'https://www.cc98.org/topic/' + str(topic['id'])
#         for user in users:
#             await bot.send_private_msg(user_id=user.qq, message=msg)
