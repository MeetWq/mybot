### 简介

基于 [NoneBot](https://github.com/nonebot/nonebot2) 和 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 实现的QQ机器人

### install

#### go-cqhttp

从 [release](https://github.com/Mrs4s/go-cqhttp/releases) 界面下载可执行文件，初次运行后生成 `config.hjson` 配置文件，修改相关配置

#### NoneBot

```bash
pip install nb-cli nonebot-adapter-cqhttp
```

#### Plugins

##### NoneBot 商店插件
```bash
nb plugin install nonebot_plugin_test
nb plugin install nonebot_plugin_apscheduler
nb plugin install nonebot_plugin_manager
```

##### 其他插件

- Commonly used

```bash
pip install bs4 lxml jinja2 aiohttp pillow imageio langid fuzzywuzzy python-Levenshtein
sudo apt install ffmpeg imagemagick translate-shell
```

- For plugin bilibili_live

```bash
pip install bilibili_api
```

- For plugin fortune, logo

```bash
pip install playwright
python -m playwright install
```

- For plugin pixiv

```bash
pip install pixivpy-async aiohttp_socks
```

- For plugin tts

```bash
pip install pydub
pip install tencentcloud-sdk-python
```

- For plugin tex

```bash
sudo apt install texlive-full poppler-utils
```

- For plugin wolfram

```bash
pip install wolframalpha
```

- For plugin what

```bash
pip install baike
```
