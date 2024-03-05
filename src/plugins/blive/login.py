import time
from io import BytesIO

from bilireq.login import Login
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import Alconna, Args, on_alconna
from nonebot_plugin_saa import Image, MessageFactory
from png import Image as PNGImage

from .auth import AuthManager
from .utils import calc_time_total

blive_check = on_alconna("blive_check", permission=SUPERUSER)
blive_login = on_alconna("blive_login", permission=SUPERUSER)
blive_logout = on_alconna(
    Alconna("blive_logout", Args["uid", int]), permission=SUPERUSER
)


@blive_check.handle()
async def _(matcher: Matcher):
    if not AuthManager.grpc_auths:
        await matcher.finish("没有缓存的登录信息")
    msgs = []
    for auth in AuthManager.grpc_auths:
        token_time = calc_time_total(auth.tokens_expired - int(time.time()))
        cookie_time = calc_time_total(auth.cookies_expired - int(time.time()))
        msg = (
            f"账号uid: {auth.uid}\n"
            f"token有效期: {token_time}\n"
            f"cookie有效期: {cookie_time}"
        )
        msgs.append(msg)
    await matcher.finish("\n----------\n".join(msgs))


@blive_login.handle()
async def _(matcher: Matcher):
    login = Login()
    qr_url = await login.get_qrcode_url()
    logger.debug(f"qrcode login url: {qr_url}")
    img: PNGImage = await login.get_qrcode(qr_url)  # type: ignore
    output = BytesIO()
    img.save(output)
    await MessageFactory(Image(output)).send()
    try:
        auth = await login.qrcode_login(interval=5)
        assert auth, "登录失败，返回数据为空"
        logger.debug(auth.data)
        AuthManager.add_auth(auth)
    except Exception as e:
        await matcher.finish(f"登录失败: {e}")
    await matcher.finish("登录成功，已将验证信息缓存至文件")


@blive_logout.handle()
async def _(matcher: Matcher, uid: int):
    if msg := AuthManager.remove_auth(uid):
        await matcher.finish(msg)
    await matcher.finish(f"账号 {uid} 已退出登录")
