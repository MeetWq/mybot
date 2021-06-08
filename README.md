### 简介

基于 [NoneBot](https://github.com/nonebot/nonebot2) 和 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 实现的QQ机器人

实现了一些乱七八糟的功能

![](https://pic.imgdb.cn/item/60bf677f844ef46bb2829a7c.jpg)


### install

#### go-cqhttp

从 [release](https://github.com/Mrs4s/go-cqhttp/releases) 界面下载可执行文件，初次运行后生成 `config.yml` 配置文件，修改相关配置

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
nb plugin install nonebot_plugin_alias
nb plugin install nonebot_plugin_withdraw
```

##### 其他插件

```bash
pip install -r requirements.txt
python -m playwright install
sudo apt install ffmpeg imagemagick translate-shell
sudo apt install texlive-full poppler-utils
```
