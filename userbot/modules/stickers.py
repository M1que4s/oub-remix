# Copyright (C) 2020 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for kanging stickers or making new ones. Thanks @rupansh"""

import io
import math
import asyncio
import random
import urllib.request
from os import remove
import requests
from bs4 import BeautifulSoup as bs
from PIL import Image
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import (
    DocumentAttributeFilename,
    DocumentAttributeSticker,
    InputStickerSetID,
    MessageMediaPhoto,
)

from userbot import CMD_HELP, bot
from userbot.events import register

from re import match, sub

combot_stickers_url = "https://combot.org/telegram/stickers?q="

KANGING_STR = [
    "Stealing this sticker...",
    "Using Witchery to kang this sticker...",
    "Plagiarising hehe...",
    "Inviting this sticker over to my pack...",
    "Kanging this sticker...",
    "Hey that's a nice sticker!\nMind if I kang?!..",
    "hehe me stel ur stikér\nhehe.",
    "Ay look over there (☉｡☉)!→\nWhile I kang this...",
    "Roses are red violets are blue, kanging this sticker so my pacc looks cool",
    "Imprisoning this sticker...",
    "Mr.Steal Your Sticker is stealing this sticker... ",
]

def ToBool(str):
    return str.lower() in [ "yes", "si", "true" ]

@register(outgoing=True, pattern="^.kang")
async def kang(args):
    """ For .kang command, kangs stickers or creates new ones. """
    user = await bot.get_me()
    user.username = user.first_name
    message = await args.get_reply_message()
    photo = None
    emojibypass = False
    is_anim = False
    emoji = None

    if message and message.media:
        if isinstance(message.media, MessageMediaPhoto):
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            photo = io.BytesIO()
            photo = await bot.download_media(message.photo, photo)
        elif "image" in message.media.document.mime_type.split("/"):
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            photo = io.BytesIO()
            await bot.download_file(message.media.document, photo)
            if (
                DocumentAttributeFilename(file_name="sticker.webp")
                in message.media.document.attributes
            ):
                emoji = message.media.document.attributes[1].alt
                if emoji != "":
                    emojibypass = True
        elif "tgsticker" in message.media.document.mime_type:
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            await bot.download_file(message.media.document, "AnimatedSticker.tgs")

            attributes = message.media.document.attributes
            for attribute in attributes:
                if isinstance(attribute, DocumentAttributeSticker):
                    emoji = attribute.alt

            emojibypass = True
            is_anim = True
            photo = 1
        else:
            await args.edit("`Unsupported File!`", parse_mode="md")
            return
    else:
        await args.edit("`Couldn't download sticker! Make sure you send a proper sticker/photo.`", parse_mode="md")
        return

    if photo:
        splat = args.text.split()

        if not emojibypass: emoji = "⭐️"

        pack = "Kang"
        vol = 1
        username = True
        patt = {
            "num": r'^(\d+)$',
            "text": r'([\w\-\\\{\}\[\]\"\'\~\$\@\!\¡\|\¬\¿\?\.\:\,\;\·\#\%\&\/\=\ª\º\^\`\´\+\*\¨\€\ł\ĸ\æ\«\»\¢\“\”\µ\ŋ\ß\¶\ŧ\←\↓\↑\→]+)',
            "notext": r'[^A-Za-z0-9]'
        }

        splat_len = len(splat)

        # User sends 0 argument. Example:
        # .kang
        if splat_len == 1:
            await args.edit("`Info: using all default values`", parse_mode="md")

        # User sends 1 argument. Examples:
        # .kang EMOJI
        # .kang PACK_VOL
        # .kang PACK_NAME
        # and wants:
        elif splat_len == 2:
            # to put the sticker in other pack but using the default values of emoji and vol
            if match(patt["text"], splat[1]): pack = splat[1]

            # to put the sticker in other vol but using the default values of emoji and pack
            elif match(patt["num"], splat[1]): vol = splat[1]

            # to use the default sticker and is ok using the default values of pack and vol
            else: emoji = splat[1]

        # User sends 2 argument. Examples:
        # .kang EMOJI PACK_NAME
        # .kang EMOJI PACK_VOL
        elif splat_len == 3:
            emoji = splat[1]

            if match(patt["text"], splat[2]):
                pack = splat[2]

            elif match(patt["num"], splat[2]):
                vol = splat[2]

            else:
                await args.edit(f"`Unknow argument: '{splat[2]}' @ splat[2] (position 3)`")
                return

        # User sends 3 argument. Example:
        # .kang EMOJI PACK_NAME PACK_VOL
        elif splat_len == 4:
            emoji = splat[1]
            pack = splat[2]
            vol = splat[3]

        # User sends 4 argument. Example:
        # .kang EMOJI PACK_NAME PACK_VOL USER_NAME
        elif splat_len == 5:
            emoji = splat[1]
            pack = splat[2]
            vol = splat[3]

            if ToBool(splat[4]): username = ToBool(splat[4])
            elif match(patt["text"], splat[4]): username = splat[4]
            else: username = False

        # User sends 5 argument or more. Example:
        # .kang EMOJI PACK NAME PACK_VOL USER_NAME
        elif splat_len >= 6:
            emoji = splat[1]
            pack = " ".join(splat[2:-2])
            vol = splat[-2]

            if ToBool(splat[-1]): username = ToBool(splat[-1])
            elif match(patt["text"], splat[-1]): username = splat[-1]
            else: username = False

        packname = ""
        packnick = ""
        
        if (type(username) is type(True)) and username is True:
            packname = f"{sub(patt['notext'], '_', user.username)}_{sub(patt['notext'], '_', pack)}_{vol}"
            packnick = f"{user.username} {pack} Pack Vol. {vol}"
        elif type(username) is type(""):
            packname = f"{sub(patt['notext'], '_', username)}_{sub(patt['notext'], '_', pack)}_{vol}"
            packnick = f"{username} {pack} Pack Vol. {vol}"
        else:
            packname = f"{sub(patt['notext'], '_', pack)}_{vol}"
            packnick = f"{pack} Pack Vol. {vol}"
        
        cmd = "/newpack"
        file = io.BytesIO()

        if not is_anim:
            image = await resize_photo(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            packname += "_Animated"
            packnick += " (Animated)"
            cmd = "/newanimated"

        response = urllib.request.urlopen(
            urllib.request.Request(f"http://t.me/addstickers/{packname}")
        )
        htmlstr = response.read().decode("utf8").split("\n")

        if (
            "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."
            not in htmlstr
        ):
            async with bot.conversation("Stickers") as conv:
                await conv.send_message("/addsticker")
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packname)
                x = await conv.get_response()
                while "120" in x.text:
                    vol += 1
                    
                    if (type(username) is type(True)) and username is True:
                        packname = f"{sub(patt['notext'], '_', user.username)}_{sub(patt['notext'], '_', pack)}_{vol}"
                        packnick = f"{user.username} {pack} Pack Vol. {vol}"
                    elif type(username) is type(""):
                        packname = f"{sub(patt['notext'], '_', username)}_{sub(patt['notext'], '_', pack)}_{vol}"
                        packnick = f"{username} {pack} Pack Vol. {vol}"
                    else:
                        packname = f"{sub(patt['notext'], '_', pack)}_{vol}"
                        packnick = f"{pack} Pack Vol. {vol}"
                    
                    await args.edit(
                        "`Switching to Pack "
                        + str(pack) + " Vol " + str(vol)
                        + " due to insufficient space`",
                        parse_mode="md"
                    )
                    await conv.send_message(packname)
                    x = await conv.get_response()
                    if x.text == "Invalid pack selected.":
                        await conv.send_message(cmd)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message(packnick)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        if is_anim:
                            await conv.send_file("AnimatedSticker.tgs")
                            remove("AnimatedSticker.tgs")
                        else:
                            file.seek(0)
                            await conv.send_file(file, force_document=True)
                        await conv.get_response()
                        await conv.send_message(emoji)
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response()
                            await conv.send_message(f"<{packnick}>")
                        # Ensure user doesn't get spamming notifications
                        await conv.get_response()
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message("/skip")
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message(packname)
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await args.edit(
                            f"`Sticker added in a Different Pack !\
                            \nThis Pack is Newly created!`\
                            \nYour pack can be found [here](t.me/addstickers/{packname})",
                            parse_mode="md",
                        )
                        return
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    await args.edit(
                        "`Failed to add sticker, use` @Stickers `bot to add the sticker manually.`",
                        parse_mode="md"
                    )
                    return
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/done")
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
        else:
            await args.edit("`Brewing a new Pack...`")
            async with bot.conversation("Stickers") as conv:
                await conv.send_message(cmd)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packnick)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    await args.edit(
                        "`Failed to add sticker, use` @Stickers `bot to add the sticker manually.`"
                    )
                    return
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response()
                    await conv.send_message(f"<{packnick}>")
                # Ensure user doesn't get spamming notifications
                await conv.get_response()
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message("/skip")
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message(packname)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)

        await args.edit(
            f"`Sticker kanged successfully!`\
            \nPack can be found [here](t.me/addstickers/{packname})",
            parse_mode="md",
        )
        await asyncio.sleep(7.5)
        await args.delete()


async def resize_photo(photo):
    """ Resize the given photo to 512x512 """
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    return image


@register(outgoing=True, pattern="^.stkrinfo$")
async def get_pack_info(event):
    if not event.is_reply:
        await event.edit("`I can't fetch info from nothing, can I ?!`")
        return

    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        await event.edit("`Reply to a sticker to get the pack details`")
        return

    try:
        stickerset_attr = rep_msg.document.attributes[1]
        await event.edit("`Fetching details of the sticker pack, please wait..`")
    except BaseException:
        await event.edit("`This is not a sticker. Reply to a sticker.`")
        return

    if not isinstance(stickerset_attr, DocumentAttributeSticker):
        await event.edit("`This is not a sticker. Reply to a sticker.`")
        return

    get_stickerset = await bot(
        GetStickerSetRequest(
            InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash,
            )
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)

    OUTPUT = (
        f"**Sticker Title:** `{get_stickerset.set.title}\n`"
        f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Archived:** `{get_stickerset.set.archived}`\n"
        f"**Stickers In Pack:** `{len(get_stickerset.packs)}`\n"
        f"**Emojis In Pack:**\n{' '.join(pack_emojis)}"
    )

    await event.edit(OUTPUT)

@register(outgoing=True, pattern=r"^\.stickers ?(.*)")
async def cb_sticker(event):
    split = event.pattern_match.group(1)
    if not split:
        await event.edit("`Provide some name to search for pack.`")
        return
    await event.edit("`Searching sticker packs`")
    text = requests.get(combot_stickers_url + split).text
    soup = bs(text, "lxml")
    results = soup.find_all("div", {'class': "sticker-pack__header"})
    if not results:
        await event.edit("`No results found :(.`")
        return
    reply = f"**Sticker packs found for {split} are :**"
    for pack in results:
        if pack.button:
            packtitle = (pack.find("div", "sticker-pack__title")).get_text()
            packlink = (pack.a).get('href')
            packid = (pack.button).get('data-popup')
            reply += f"\n **• ID: **`{packid}`\n [{packtitle}]({packlink})"
    await event.edit(reply)

@register(outgoing=True, pattern="^.getsticker$")
async def sticker_to_png(sticker):
    if not sticker.is_reply:
        await sticker.edit("`NULL information to fetch...`")
        return False

    img = await sticker.get_reply_message()
    if not img.document:
        await sticker.edit("`Reply to a sticker...`")
        return False

    try:
        img.document.attributes[1]
    except Exception:
        await sticker.edit("`This is not a sticker...`")
        return

    with io.BytesIO() as image:
        await sticker.client.download_media(img, image)
        image.name = "sticker.png"
        image.seek(0)
        try:
            await img.reply(file=image, force_document=True)
        except Exception:
            await sticker.edit("`Error, can't send file...`")
        else:
            await sticker.delete()
    return


CMD_HELP.update({
    "stickers": """.kang
Usage: Reply .kang to a sticker or an image to kang it to your userbot pack.

`.kang [emoji('s)]`
Usage: Works just like .kang but uses the emoji('s) you picked.

`.kang [number]`
Usage: Kang's the sticker/image to the specified pack vol but uses ⭐️ as emoji.

`.kang [name]`
Usage: Kang's the sticker/image to the specified pack name but uses ⭐️ as emoji.

`.kang [emoji('s)] [number]`
Usage: Kang's the sticker/image to the specified pack vol and uses the emoji('s) you picked.

`.kang [emoji('s)] [name]`
Usage: Kang's the sticker/image to the specified pack name and uses the emoji('s) you picked.

`.kang [emoji('s)] [name] [number]`
Usage: Kang's the sticker/image to the specified pack name, vol and uses the emoji('s) you picked.

`.kang [emoji('s)] [name] [number] [username]`
Usage: Kang's the sticker/image to the specified pack name, vol, uses the emoji('s) you picked and enable/disable put the username in the pack name.

`.stkrinfo`
Usage: Gets info about the sticker pack.

`.getsticker`
Usage: reply to a sticker to get 'PNG' file of sticker."""
})
