import httpx
from typing import List, Union
import json
import time
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from .config import bot_config
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

async def auto_manga_translate(image: bytes) -> Message:
    print("processing...")
    # according to https://docs.ap-sh.starivercs.com/#/stariverdl_gateway/normal_manga_translate?id=%e5%90%8c%e6%ad%a5%e6%bc%ab%e7%94%bb%e7%bf%bb%e8%af%91
    data = json.dumps({
        "cache": True,
        "token": bot_config.stariver_api_token,
        "image": base64.b64encode(image).decode("utf-8")
    })
    uri = bot_config.stariver_api_endpoint + bot_config.sync_task_uri
    start_time = time.time()
    try:
        result = await post(uri, data)
    except Exception:
        return "网络异常"
    
    if result["Code"] != 0 :
        return "请求星河API错误: " + result["Message"]
    
    translated_image = result["Data"]["translated_image"]
    translated_image = base64.b64decode(translated_image)
    total_time = time.time() - start_time
    cached = result["Data"]["cached"]

    print(total_time)

    return "处理总耗时: " + str(total_time) + "s\n是否命中缓存: " + str(cached) + MessageSegment.image(translated_image)

async def manual_manga_translate(image: bytes):
    # according to https://docs.ap-sh.starivercs.com/#/stariverdl_gateway/advanced_manga_translate?id=%e6%89%8b%e5%8a%a8%e6%bc%ab%e7%94%bb%e7%bf%bb%e8%af%91
    data = json.dumps({
        "token": bot_config.stariver_api_token,
        "image": base64.b64encode(image).decode("utf-8")
    })
    uri = bot_config.stariver_api_endpoint + bot_config.advanced_manual_translate_uri
    start_time = time.time()
    try:
        result = await post(uri, data)
    except Exception:
        return "网络异常", "", False
    
    if result["Code"] != 0 :
        return "请求星河API错误: " + result["Message"], "", False
    
    inpainted_image = result["Data"]["inpainted_image"]
    inpainted_image = base64.b64decode(inpainted_image)
    inpainted_image = BytesIO(inpainted_image)
    inpainted_image = Image.open(inpainted_image)

    image_draw = ImageDraw.ImageDraw(inpainted_image)

    font_style = ImageFont.truetype("./plugins/nonebot_manga_translate/font.ttf", 25, encoding="utf-8")

    sign = 0

    for TextBlock in result["Data"]["text_block"]: 
        xyxy = TextBlock["xyxy"]
        image_draw.rectangle(((xyxy[0], xyxy[1]), (xyxy[2], xyxy[3])), fill=None, outline='blue', width=6)
        image_draw.text((xyxy[0], xyxy[1]), str(sign), (255, 0, 0), font=font_style)
        sign += 1
    
    out_buffer = BytesIO()
    inpainted_image.save(out_buffer, format='png')
    signed_result = out_buffer.getvalue()

    return result["Data"], signed_result, True
    

async def download_image(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=20)
        return resp.content
    
async def post(url, data: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=data, timeout=20)
        return resp.json()


def get_message_image(data:Union[str,dict]) -> "list":
    """
    返回一个包含消息中所有图片文件路径的list,
    Args : 
          * ``data: str`` : 消息内容, 来自event.json()  
          * ``type: Literal['file','url']``: 当``type``为``'file'``时, 返回的是文件路径, 当``type``为``'url'``时, 返回的是url  
    Return :
          * ``img_list: list`` : 包含图片绝对路径或url的list
    """
    if isinstance(data,str):
        data = json.loads(data)
    return  [message['data']['url'] for message in data['message'] if message['type'] == 'image']

def is_image(images: list) -> bool:
    return len(images) > 0

def is_single(images: list) -> bool:
    return len(images) == 1

async def check(images:list) -> bool:
    return len(images) == 0