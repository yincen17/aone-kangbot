import datetime
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from userbot import bot, CMD_HELP
from userbot.events import register

@register(outgoing=True, pattern="^.q(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return 
    if not event.reply_to_msg_id:
       await event.edit("```balasa ke pesan siapa saja .```")
       return
    reply_message = await event.get_reply_message() 
    if not reply_message.text:
       await event.edit("```balasa ke pesan text``")
       return
    chat = "@QuotLyBot"
    sender = reply_message.sender
    if reply_message.sender.bot:
       await event.edit("```balas ke pesan orang.```")
       return
    await event.edit("```Menkonversi menjadi Quote```")
    async with bot.conversation(chat) as conv:
          try:     
              response = conv.wait_event(events.NewMessage(incoming=True,from_users=1031952739))
              await bot.forward_messages(chat, reply_message)
              response = await response 
          except YouBlockedUserError: 
              await event.reply("```buka blokir @QuotLyBot dan coba lagi```")
              return
          if response.text.startswith("Hi!"):
             await event.edit("```anjenk di private akunya! ```")
          else: 
             await event.delete()   
             await bot.forward_messages(event.chat_id, response.message)

CMD_HELP.update({
        "quotly": 
        ".q \
          \nUsage: Enhance ur text to sticker.\n"
    })
