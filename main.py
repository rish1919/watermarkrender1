# main.py
from pyrogram import Client, filters
from pyrogram.types import Message
from config import BOT_TOKEN, OWNER_ID
from utils import load_json, save_json
from watermark import add_watermark_to_image, add_watermark_to_video
import os
import uuid

app = Client("watermarkbot", bot_token=BOT_TOKEN)

codes = load_json("codes.json", [])
claimed = load_json("claimed.json", {})

def is_owner(user_id):
    return user_id == OWNER_ID

@app.on_message(filters.command("start"))
async def start_cmd(_, m: Message):
    await m.reply("👋 Send /claimcode <your_code> to activate the bot in your channel.")

@app.on_message(filters.command("generatecode") & filters.user(OWNER_ID))
async def generate_code(_, m: Message):
    parts = m.text.split()
    if len(parts) != 2:
        return await m.reply("❌ Usage: /generatecode CODE123")
    code = parts[1]
    if code in codes:
        return await m.reply("⚠️ Code already exists.")
    codes.append(code)
    save_json("codes.json", codes)
    await m.reply(f"✅ Code `{code}` added.")

@app.on_message(filters.command("claimcode"))
async def claim_code(_, m: Message):
    parts = m.text.split()
    if len(parts) != 2:
        return await m.reply("❌ Usage: /claimcode CODE123")
    code = parts[1]
    if code not in codes:
        return await m.reply("❌ Invalid code.")
    chat_id = m.chat.id
    if str(chat_id) in claimed:
        return await m.reply("⚠️ This chat already activated.")
    codes.remove(code)
    claimed[str(chat_id)] = True
    save_json("codes.json", codes)
    save_json("claimed.json", claimed)
    await m.reply("✅ Bot activated for this channel!")

@app.on_message(filters.command("setwm") & filters.user(OWNER_ID))
async def set_watermark(_, m: Message):
    if not m.reply_to_message or not m.reply_to_message.photo:
        return await m.reply("❌ Reply to a PNG watermark image.")
    file = await m.reply_to_message.download("watermark.png")
    await m.reply("✅ Watermark image saved.")

@app.on_message(filters.command("showwm"))
async def show_watermark(_, m: Message):
    if not os.path.exists("watermark.png"):
        return await m.reply("❌ No watermark set.")
    await m.reply_photo("watermark.png", caption="🖼 Current watermark")

@app.on_message(filters.command("dltwm") & filters.user(OWNER_ID))
async def delete_watermark(_, m: Message):
    if os.path.exists("watermark.png"):
        os.remove("watermark.png")
        await m.reply("🗑 Watermark removed.")
    else:
        await m.reply("❌ No watermark to delete.")

@app.on_message(filters.channel)
async def auto_watermark(_, m: Message):
    chat_id = str(m.chat.id)
    if chat_id not in claimed:
        return

    if not os.path.exists("watermark.png"):
        return

    try:
        if m.photo:
            file_path = await m.download()
            out_path = f"w_{uuid.uuid4().hex}.jpg"
            add_watermark_to_image(file_path, "watermark.png", out_path)
            await app.send_photo(m.chat.id, photo=out_path, caption=m.caption or "")
            os.remove(file_path)
            os.remove(out_path)
        elif m.video:
            file_path = await m.download()
            out_path = f"w_{uuid.uuid4().hex}.mp4"
            add_watermark_to_video(file_path, "watermark.png", out_path)
            await app.send_video(m.chat.id, video=out_path, caption=m.caption or "")
            os.remove(file_path)
            os.remove(out_path)
    except Exception as e:
        await m.reply(f"⚠️ Error: {e}")

app.run()
