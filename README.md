#### 简介

基于 [Nonebot](https://github.com/nonebot/nonebot) 和 [酷Q](https://cqp.cc/) 的QQ机器人

主要功能是 cc98 和 nhd 自动签到信息的发送
以及基于 [cc98api](https://github.com/zjuchenyuan/cc98api) 实现的 cc98快速看帖功能

机器人QQ号为 `1846731675` ，欢迎骚扰


#### 安装
安装 miniconda
```bash
conda install requests python-Levenshtein ujson
pip install nonebot
pip install "nonebot[scheduler]"
pip install fuzzywuzzy aiocache msgpack
pip install -U cos-python-sdk-v5
pip install aiohttp
```