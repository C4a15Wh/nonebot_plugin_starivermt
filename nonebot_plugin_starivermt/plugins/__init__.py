from pathlib import Path
import re

import nonebot
from nonebot import get_driver, on_command
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.params import ArgPlainText

from .utils import *
from .config import bot_config, Config

_sub_plugins = set()
_sub_plugins |= nonebot.load_plugins(
    str((Path(__file__).parent / "plugins").resolve())
)

__plugin_meta__ = PluginMetadata(
    name="漫画翻译",
    description="基于星河漫画翻译API的漫画翻译bot",
    usage=(f"auto_mt [图片]\n或回复图片"),
    config=Config,
    extra={
        "unique_name": "starivermt",
        "example": "auto_mt [图片]",
        "author": "C4a15Wh <weiminghao@stariver.org>",
        "version": "0.0.1",
    },
)

MODULE_STATUS = {
    "auto_mt": True,
    "manual_mt": True
}

auto_translate = on_command("auto_mt")
manual_translate = on_command("manual_mt")
admin = on_command("manage", rule=to_me())

@admin.got("msg", prompt="请输入要调整的模块\n当前模块: \n1. auto_mt\n2. manual_mt\n请直接输入模块名称。")
async def _(bot: Bot, event: Event, state: T_State, msg: str = ArgPlainText()):
    if not msg in ["True", "False"]:
        state["module"] = msg
        module = msg
        if not msg in MODULE_STATUS:
            await admin.finish("模块不存在!")
        
    if not event.get_user_id() in bot_config.super_user:
        await admin.finish("您不是管理员用户。")

    if msg in ["True", "False"]:
        module = state["module"]
        print(module)
        if msg == "False":
            MODULE_STATUS[module] = False
        elif msg == "True":
            MODULE_STATUS[module] = True
        else:
            await admin.finish("错误的输入值{}".format(msg))
    
        
        await admin.finish("{module}目前的状态已调整为{stat}".format(module=module, stat=str(MODULE_STATUS[module])))

    await admin.reject("{module}目前的状态为{stat}，请输入您需要调整的值: \nTrue/False".format(module=module, stat=MODULE_STATUS[module]))

@auto_translate.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if not MODULE_STATUS["auto_mt"]:
        await auto_translate.finish("自动翻译功能已被管理员关闭。")

    images = get_message_image(event.json())

    # 判断图片数量
    if not is_image(images) or not is_single(images):
        state["status"] = 0
        return
    
    image = images[0]

    state["status"] = 1
    state["image"] = ""
    
    # 下载图片
    source_image = await download_image(image)
    translated_image = await auto_manga_translate(source_image)

    await bot.send(event, translated_image)
    return

@auto_translate.got("image", prompt="图呢图呢?")
async def _(bot: Bot, event: Event, state: T_State):
    if state["status"] == 1:
        return

    images = get_message_image(event.json())

    # 判断图片数量
    if not is_image(images) or not is_single(images):
        message = MessageSegment.reply(event.message_id) + MessageSegment.text("错误: 您并未发送图片或发送了多张图片。")
        # await bot.send(event, message)
        return
    
    image = images[0]
    
    # 下载图片
    source_image = await download_image(image)
    translated_image = await auto_manga_translate(source_image)

    await bot.send(event, translated_image)
    return

@manual_translate.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if not MODULE_STATUS["manual_mt"]:
        await auto_translate.finish("手动翻译功能已被管理员关闭。")

    images = get_message_image(event.json())

    # 判断图片数量
    if not is_image(images) or not is_single(images):
        state["status"] = 0
        return
    
    image = images[0]

    state["status"] = 1
    state["image"] = ""
    
    # 下载图片
    source_image = await download_image(image)
    data, signed_image, status = await manual_manga_translate(source_image)
    if not status:
        manual_translate.finish("星河API错误: " + data)

    resp_msg = MessageSegment.image(signed_image) + "请按照图中顺序回传填充内容。"

    await bot.send(event, resp_msg)
    return

@manual_translate.got("image", prompt="图呢图呢?")
async def _(bot: Bot, event: Event, state: T_State):
    if state["status"] == 1:
        return

    images = get_message_image(event.json())

    # 判断图片数量
    if not is_image(images) or not is_single(images):
        message = MessageSegment.reply(event.message_id) + MessageSegment.text("错误: 您并未发送图片或发送了多张图片。")
        # await bot.send(event, message)
        return
    
    image = images[0]
    
    # 下载图片
    source_image = await download_image(image)
    translated_image = await auto_manga_translate(source_image)

    await bot.send(event, translated_image)
    return