#Port to userbot by @KeselekPermen69
#modifed by yincen to virustotal
import datetime
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from userbot.events import register
from userbot import bot, CMD_HELP

@register(outgoing=True, pattern="^.vtscan(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return 
    if not event.reply_to_msg_id:
       await event.edit("`Reply to any user message.`")
       return
    reply_message = await event.get_reply_message() 
    #if not reply_message.text:
      # await event.edit("```reply to text message```")
       #return
    chat = "@VirusTotalESPBot"
    sender = reply_message.sender
    if reply_message.sender.bot:
       await event.edit("`Reply to actual users message.`")
       return
    await event.edit("`Scanning By Virus Total`")
    async with bot.conversation(chat) as conv:
          try:     
              response = conv.wait_event(events.NewMessage(incoming=True,from_users=276396917))
              await bot.forward_messages(chat, reply_message)
              response = await response 
          except YouBlockedUserError: 
              await event.reply("`Please unblock @DrWebBot  and try again`")
              return
          if response.text.startswith("Forward"):
             await event.edit("`can you kindly disable your forward privacy settings for good?`")
          else: 
             await event.edit(f"{response.message.message}")


CMD_HELP.update({
        "Virustotal": 
        ".vtscan \
          \n reply to files for scan a file from virus scanned by Virus total.\n"
    })
