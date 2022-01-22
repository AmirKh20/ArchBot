#!/usr/bin/python3

from telethon import TelegramClient, events
from telethon.tl import types
from os import path, makedirs, getenv
from re import search
from dotenv import load_dotenv
load_dotenv()

api_id = int(getenv("API_ID"))
api_hash = getenv("API_HASH")
client = TelegramClient('telethon_session', api_id, api_hash)

def GetDirName(mime_type):
    if search("audio/.+", mime_type):
        return "MusicFiles"
    elif search("image/.+", mime_type):
        return "ImageFiles"
    else:
        return "Others"

@client.on(events.NewMessage)
async def DownloadHandler(update):
    message = update.message
    if message.media is None or isinstance(message.media, types.MessageMediaPhoto):
        return

    if message.media.document.size < 20971520: #We Download files with a size under 20 MB with PTB
        return

    attributes = message.media.document.attributes
    DirName = GetDirName(message.media.document.mime_type)
    for attr in attributes:
        if isinstance(attr, types.DocumentAttributeFilename):
            file_name = attr.file_name
            file_path = path.join(DirName, str(update.chat_id), file_name)
            break

    if path.exists(file_path):
        await message.reply("File Exists!")
        return

    makedirs(f"{DirName}/{update.chat_id}", exist_ok=True)
    down_message = await message.reply("Downloading...")
    await message.download_media(file_path)
    await client.edit_message(down_message, "Finished")

client.start(bot_token = getenv("BOT_TOKEN"))
client.run_until_disconnected()
