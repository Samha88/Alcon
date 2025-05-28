import asyncio
import re
from telethon import TelegramClient, events
from aiohttp import web

# معلومات حساب تيليجرام
api_id = 9844693
api_hash = 'b9f99569919502974aedefbda38393a5'
session_name = 'my_session'

# المستخدم المسموح له بتشغيل وإيقاف المراقبة
allowed_chat_ids = {7323006705}

# إعداد القناة والبوت
channel_username = "AlcontBotUSD"
channel_regex = r"\b[a-zA-Z0-9]{8,12}\b"
bot_username = "ichancy_alcont_usd_bot"

# تهيئة العميل
client = TelegramClient(session_name, api_id, api_hash)
monitoring_active = False

# تفعيل أو إيقاف المراقبة بأمر من المستخدم
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    if event.chat_id not in allowed_chat_ids:
        return
    await event.respond("أرسل 's' لتشغيل المراقبة، أو 'st' لإيقافها.")

@client.on(events.NewMessage)
async def command_handler(event):
    global monitoring_active
    if event.chat_id not in allowed_chat_ids:
        return

    message = event.raw_text.strip().lower()
    if message == 's':
        monitoring_active = True
        await event.respond("تم تفعيل المراقبة.")
    elif message == 'st':
        monitoring_active = False
        await event.respond("تم إيقاف المراقبة.")

# مراقبة القناة واستخراج الكود المناسب وإرساله للبوت
@client.on(events.NewMessage(chats=channel_username))
async def monitor_channel(event):
    if not monitoring_active:
        return

    matches = re.findall(channel_regex, event.raw_text)
    if not matches:
        print("ما تم العثور على أي كود.")
        return

    # إذا فيه 4 أكواد أو أكثر، خذ الرابع، غير هيك خذ الأول
    code = matches[3] if len(matches) >= 4 else matches[0]
    print(f"تم استخراج الكود: {code}")

    try:
        await client.send_message(bot_username, code)
        print(f"تم إرسال الكود للبوت مباشرة: {code}")
    except Exception as e:
        print(f"فشل إرسال الكود: {e}")

# Web server بسيط للفحص
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

async def start_all():
    await client.start()
    print("Userbot started.")
    client_loop = asyncio.create_task(client.run_until_disconnected())

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()
    print("Web server running on http://0.0.0.0:8081")
    await client_loop

if __name__ == "__main__":
    asyncio.run(start_all())
