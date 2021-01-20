import asyncio
import io

import aiohttp
from PIL import Image
import sys, os


async def make_card(rarity, attr, assetbundleName):
    bg_url = f'https://pjsek.ai/members/cardFrame_S_{rarity}.png'
    attr_url = f'https://pjsek.ai/members/icon_attribute_{attr}.png'
    star_url = r'./modules/src/rarity_star_normal.png' #/home/ubuntu/nenerobo/modules/ # r'D:\PEI\Programing\Python\LearnPython\圖片處理\data\rarity_star_normal.png'
    character_url = f'https://assets.pjsek.ai/file/pjsekai-assets/startapp/character/member_cutout/{assetbundleName}/{"after_training" if rarity > 2 else "normal"}/thumbnail_xl.png'

    # 下載圖片
    async with aiohttp.ClientSession() as session:
        async with session.get(bg_url) as resp:
            if resp.status == 200:
                bg = io.BytesIO(await resp.read())
            else:
                return False
        async with session.get(character_url) as resp:
            if resp.status == 200:
                character = io.BytesIO(await resp.read())
            else:
                return False
        async with session.get(attr_url) as resp:
            if resp.status == 200:
                attr = io.BytesIO(await resp.read())
            else:
                return False

    bg = Image.open(bg) # 背景邊框
    character = Image.open(character) # 卡面
    attr = Image.open(attr) # 屬性
    star = Image.open(star_url) # 星星

    character_box = (int(bg.size[0]*0.9),)*2
    character = character.resize(character_box) # 調整卡面大小

    attr_resize_box = (int(attr.size[0]*0.4),)*2
    attr = attr.resize(attr_resize_box) # 調整屬性大小

    star_resize_box = (int(star.size[0]*0.33),)*2
    star = star.resize(star_resize_box) # 調整星星大小

    bg.paste(character, (8,8), character) # 貼上卡面
    bg.paste(attr, (0,0), attr) # 貼上屬性
    for i in range(rarity): # 貼上星星
        bg.paste(star, (8+i*(star.size[0]+1), bg.size[1]-31), star)

    bg.save(f'./modules/src/card/{assetbundleName}.png', 'PNG') # 轉換為 binary data，存在 buf

async def get_all_card():
        async with aiohttp.ClientSession() as session:
            card_info_url = 'https://api.pjsek.ai/database/master/cards?$select[]=id&$select[]=rarity&$select[]=attr&$select[]=assetbundleName&$limit=1000'
            async with session.get(card_info_url) as resp:
                if resp.status == 200:
                    all_card = await resp.json()
                    return all_card["data"]
                else:
                    return None

async def main():
    cards = await get_all_card()
    path=sys.path[0] # +r'/1.txt'
    for card in cards:
        if not os.path.isfile(f'{path}/card/{card["assetbundleName"]}.png'):
            print(f'Card File "{card["assetbundleName"]}.png" not exist, try to print card now.')
            await make_card(card['rarity'], card['attr'], card['assetbundleName'])
    # with open(f"{path}/last.log", 'w+') as f:
    #     f.write(last_id)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
