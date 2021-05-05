### 简介

基于 [Mirai](https://github.com/mamoe/mirai) 和 [NoneBot](https://github.com/nonebot/nonebot2) 实现的QQ机器人

### install

#### Mirai

- 安装 [MCL](https://github.com/iTXTech/mirai-console-loader) (Mirai Console Loader)

- 安装 [onebot-mirai](https://github.com/yyuueexxiinngg/onebot-kotlin) 插件，并配置账号、端口

- 启动 MCL，若需要滑块验证可用 [此处](https://github.com/project-mirai/mirai-login-solver-selenium) 的解决方案

- 配置自动登录、登录协议等，具体参考 [mirai-console](https://github.com/mamoe/mirai-console) 的文档

#### NoneBot

```bash
pip install nb-cli nonebot-adapter-cqhttp nonebot-adapter-mirai
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
pip bs4 lxml aiohttp
pip install fuzzywuzzy python-Levenshtein
pip install pillow
sudo apt install imagemagick
```

- For plugin avatar

```bash
pip install imageio
```

- For plugin bilibili_live

```bash
pip install bilibili_api
```

- For plugin fortune, logo, text

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
pip install pydub langid
pip install tencentcloud-sdk-python

sudo apt install ffmpeg nodejs npm
sudo npm install wx-voice --save
sudo npm install wx-voice -g
sudo wx-voice compile
```

- For plugin tex

```bash
sudo apt install texlive-full poppler-utils
```

- For plugin what

```bash
pip install baike wikipedia
```
