import os
import logging
import asyncio
import time
import sys
import subprocess
import pkg_resources
import json

# --- VPS DEPEDENCY AUTO-INSTALLER ---
def install_dependencies():
    requirements_content = """python-telegram-bot==21.5
instagrapi==2.1.1
python-dotenv==1.0.1
"""
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)
    
    required = {'python-telegram-bot', 'instagrapi', 'python-dotenv'}
    mapping = {
        'python-telegram-bot': 'python-telegram-bot',
        'instagrapi': 'instagrapi',
        'python-dotenv': 'python-dotenv'
    }
    
    try:
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = [mapping[r] for r in required if r.lower() not in installed]
    except Exception:
        missing = list(required)

    if missing:
        print(f"Missing dependencies found: {missing}. Installing...")
        python = sys.executable
        try:
            subprocess.check_call([python, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("Dependencies installed successfully.")
        except Exception as e:
            print(f"Error installing dependencies: {e}")

if __name__ != '__main__': 
    install_dependencies()

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
    ConversationHandler,
)
from instagrapi import Client

# Load environment variables
load_dotenv()

# Hardcoded token for personal VPS
TELEGRAM_TOKEN = "8571782559:AAH6TH796Lcr0VuJwNW5eBlZhysP64SdBPQ"

# Default Raid Templates
DEFAULT_TEMPLATES = [
    "🔥 𝐔𝐋𝐓𝐑𝐀 𝐇𝐘𝐏𝐄𝐑 𝐑𝐀𝐈𝐃 🔥\n\n🎯 Target: {target}\n⚡ Status: BOMBING\n\n💀 Get Rekt!",
    "━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀ𝐫 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {target} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━",
    "{target} 𝙀𝙆 𝙂𝘾 𝙎𝙀 𝙁𝘼𝐑𝘼𝐑 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝙆𝙄 𝘾𝐇𝙐𝙏𝙏 𝙁𝘼𝘼𝐃𝙐𝙐  𝘼𝙄𝙎𝙀 𝘽𝙉𝙀𝙂𝘼 ‍𝙎𝙋𝙈𝙍𝙍𝙍______________________/❤️‍🔥👑",
    "________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝐈𝐓𝐀𝐍𝐈 𝙆𝐇𝐎𝐏𝐃𝐀 {target}⚡⚡ 𝙆𝐈 𝙈𝘼 𝙆𝘼 𝙆𝘼𝐋𝐀 𝘽𝐇𝙊𝙎𝐃𝘼࿐",
    "{target} 𝗛𝗔𝗪𝗔𝗕𝗔𝗭𝗜 𝗖𝗛𝗛𝗢𝗗 𝗔𝗨𝗥 𝙇𝙐𝑵𝑫 𝘾𝙃𝙐𝙎 🥶➿🩵 𝙈𝘼𝑫𝘼𝑹𝑪𝑯𝑶𝑫 {target} 𝐎ʏ𝐄 𝐌ᴀᴅᴀʀᴄʜ⭕𝐃 𝐊ᴇ 𝐋ᴀᴅ𝐊𝐄 𝐁ᴀ𝐍ᴀ𝐔 𝐓ᴜʜ𝐄 𝐒ᴘ△ᴍ𝐌𝐞𝐑 🤢🔥",
    "━━━━━━━━━━━━━\n🔥🔥 𝐔𝐋𝐓𝐑𝐀 𝐇𝐘𝐏𝐄𝐑 𝐑𝐀𝐈𝐃 🔥🔥🔥\n━━━━━━━━━━━━━\n\n🎯 𝐓𝐀𝐑𝐆𝐄𝐓: {target}\n💀 𝐒𝐓𝐀𝐓𝐔𝐒: 𝐃𝐄𝐒𝐓𝐑𝐎𝐘𝐈𝐍𝐆\n\n⚡ 𝐒𝐏𝐄𝐄𝐃: 𝐌𝐀𝐗𝐈𝐌𝐔𝐌\n🔥 𝐌𝐄𝐒𝐒𝐀𝐆𝐄: 𝐆𝐄𝐓 𝐅𝐔𝐂𝐊𝐄𝐃\n\n👊 𝐏𝐎𝐖𝐄𝐑𝐄𝐃 𝐁𝐘 𝐇𝐘𝐏𝐄𝐑 𝐁𝐎𝐓 𝟐.𝟎\n━━━━━━━━━━━━━"
]

# Persistent User Templates storage
TEMPLATES_FILE = "user_templates.json"
SESSIONS_FILE = "user_sessions.json"

def load_json_file(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading {filename}: {e}")
    return {}

def save_json_file(filename, data):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logging.error(f"Error saving {filename}: {e}")

# Global memory state
user_templates = load_json_file(TEMPLATES_FILE)
# Persistent session storage (metadata only)
persisted_sessions = load_json_file(SESSIONS_FILE)

# Runtime memory (non-persistent handles)
user_clients = {} # user_id -> list of { 'client': Client, 'username': str, 'session_id': str }
active_workers = {}

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Conversation states
SESSION_ID, RAID_ACCOUNT, RAID_URL, RAID_THREADS, RAID_TEMPLATE_SELECT, RAID_TARGET, RAID_DELAY = range(7)
ADD_TEMPLATE_STATE = 8
DELETE_TEMPLATE_STATE = 9

def get_user_templates(user_id):
    u_id = str(user_id)
    if u_id not in user_templates:
        user_templates[u_id] = DEFAULT_TEMPLATES.copy()
        save_json_file(TEMPLATES_FILE, user_templates)
    return user_templates[u_id]

async def check_and_terminate_previous(update: Update, context: ContextTypes.DEFAULT_TYPE, cmd_name: str):
    if context.user_data.get('current_cmd'):
        old_cmd = context.user_data['current_cmd']
        if old_cmd != cmd_name:
            await update.message.reply_text(f"⚠️ 𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 ({old_cmd}) 𝐭𝐞𝐫𝐦𝐢𝐧𝐚𝐭𝐞𝐝. 🛑")
    context.user_data['current_cmd'] = cmd_name

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "start")
    user_id = update.effective_user.id
    
    # Auto-restore sessions for the user if not in memory but in persisted storage
    u_id = str(user_id)
    if user_id not in user_clients and u_id in persisted_sessions:
        for sess_info in persisted_sessions[u_id]:
            cl = Client()
            try:
                await asyncio.to_thread(cl.login_by_sessionid, sess_info['session_id'])
                if user_id not in user_clients:
                    user_clients[user_id] = []
                user_clients[user_id].append({
                    'client': cl,
                    'username': sess_info['username'],
                    'session_id': sess_info['session_id']
                })
            except:
                continue

    welcome_text = (
        "✨ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐓𝐇𝐄 𝐔𝐋𝐓𝐑𝐀 𝐇𝐘𝐏𝐄𝐑 𝐁𝐎𝐓 𝐁𝐘 𝐃𝐄𝐕 ⚡ ⚡\n\n"
        "🔒 𝐘𝐨𝐮𝐫 𝐝𝐚𝐭𝐚 𝐢𝐬 𝐩𝐫𝐢𝐯𝐚𝐭𝐞 - 𝐨𝐧𝐥𝐲 𝐘𝐎𝐔 𝐜𝐚𝐧 𝐬𝐞𝐞 𝐲𝐨𝐮𝐫 𝐚𝐜𝐜𝐨𝐮𝐧𝐭𝐬! 🛡️\n"
        "👥 𝐓𝐡𝐞 𝐛𝐨𝐭 𝐬𝐮𝐩𝐩𝐨𝐫𝐭𝐬 𝟏𝟎𝟎+ 𝐜𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐮𝐬𝐞𝐫𝐬 𝐰𝐢𝐭𝐡 𝐢𝐬𝐨𝐥𝐚𝐭𝐞𝐝 𝐝𝐚𝐭𝐚. ⚡\n\n"
        "👉 𝐓𝐲𝐩𝐞 /help 𝐭𝐨 𝐬𝐞𝐞 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬 📜"
    )
    await update.message.reply_text(welcome_text)
    context.user_data['current_cmd'] = None
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "help")
    help_text = (
        "💎 𝐔𝐋𝐓𝐑𝐀 𝐇𝐘𝐏𝐄𝐑 𝟐.𝟎 💎\n"
        "👤 (@god_olds)\n\n"
        "🔑 /login — 𝐀𝐝𝐝 𝐚 𝐧𝐞𝐰 𝐬𝐞𝐬𝐬𝐢𝐨𝐧 𝐝𝐢𝐫𝐞𝐜𝐭𝐥𝐲\n"
        "🚀 /raid — 𝐒𝐭𝐚𝐫𝐭 𝐚 𝐡𝐢𝐠𝐡-𝐬𝐩𝐞𝐞𝐝 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐫𝐚𝐢𝐝\n"
        "📊 /status — 𝐂𝐡𝐞𝐜𝐤 𝐚𝐜𝐭𝐢𝐯𝐞 𝐫𝐚𝐢𝐝 𝐩𝐫𝐨𝐠𝐫𝐞𝐬𝐬\n"
        "👥 /accounts — 𝐌𝐚𝐧𝐚𝐠𝐞 𝐲𝐨𝐮𝐫 𝐥𝐨𝐠𝐠𝐞𝐝-𝐢𝐧 𝐚𝐜𝐜𝐨𝐮𝐧𝐭𝐬\n"
        "📜 /templates — 𝐋𝐢𝐬𝐭 𝐲𝐨𝐮𝐫 𝐫𝐚𝐢𝐝 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞𝐬\n"
        "➕ /addtemplate — 𝐀𝐝𝐝 𝐚 𝐧𝐞𝐰 𝐜𝐮𝐬𝐭𝐨𝐦 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞\n"
        "➖ /deltemplate — 𝐃𝐞𝐥𝐞𝐭𝐞 𝐚 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞\n"
        "❓ /help — 𝐒𝐡𝐨𝐰 𝐭𝐡𝐢𝐬 𝐠𝐮𝐢𝐝𝐞\n"
        "📡 /ping — 𝐓𝐞𝐬𝐭 𝐛𝐨𝐭 𝐫𝐞𝐬𝐩𝐨𝐧𝐬𝐞 𝐭𝐢𝐦𝐞\n\n"
        "🛑 /stop — 𝐊𝐢𝐥𝐥 𝐚𝐥𝐥 𝐚𝐜𝐭𝐢𝐯𝐞 𝐫𝐚𝐢𝐝𝐬 𝐢𝐧𝐬𝐭𝐚𝐧𝐭𝐥𝐲\n\n"
        "💡 𝐓𝐢𝐩: 𝐔𝐬𝐞 /stop 𝐢𝐟 𝐲𝐨𝐮 𝐠𝐞𝐭 𝐫𝐚𝐭𝐞 𝐥𝐢𝐦𝐢𝐭𝐞𝐝! ⚡"
    )
    await update.message.reply_text(help_text)
    context.user_data['current_cmd'] = None
    return ConversationHandler.END

async def templates_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "templates")
    user_id = update.effective_user.id
    templates = get_user_templates(user_id)
    text = "📜 𝐘𝐎𝐔𝐑 𝐑𝐀𝐈𝐃 𝐓𝐄𝐌𝐏𝐋𝐀𝐓𝐄𝐒:\n\n"
    for i, t in enumerate(templates, 1):
        content = t.replace("{target}", "TARGET_NAME")
        text += f"━━━━━━━━━━━━━━━━━━━━\n"
        text += f"𝐓𝐄𝐌𝐏𝐋𝐀𝐓𝐄 {i}:\n\n{content}\n"
    text += f"━━━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(text)
    context.user_data['current_cmd'] = None

async def add_template_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "addtemplate")
    await update.message.reply_text("➕ 𝐒𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐧𝐞𝐰 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐭𝐞𝐱𝐭.\n\n💡 𝐔𝐬𝐞 {target} 𝐰𝐡𝐞𝐫𝐞 𝐲𝐨𝐮 𝐰𝐚𝐧𝐭 𝐭𝐡𝐞 𝐭𝐚𝐫𝐠𝐞𝐭 𝐧𝐚𝐦𝐞 𝐭𝐨 𝐚𝐩𝐩𝐞𝐚𝐫.")
    return ADD_TEMPLATE_STATE

async def add_template_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    template_text = update.message.text
    if user_id not in user_templates:
        user_templates[user_id] = DEFAULT_TEMPLATES.copy()
    user_templates[user_id].append(template_text)
    save_json_file(TEMPLATES_FILE, user_templates)
    await update.message.reply_text("✅ 𝐍𝐞𝐰 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐚𝐝𝐝𝐞𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲! 🚀")
    context.user_data['current_cmd'] = None
    return ConversationHandler.END

async def del_template_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "deltemplate")
    user_id = update.effective_user.id
    templates = get_user_templates(user_id)
    text = "➖ 𝐒𝐞𝐥𝐞𝐜𝐭 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐧𝐮𝐦𝐛𝐞𝐫 𝐭𝐨 𝐝𝐞𝐥𝐞𝐭𝐞:\n\n"
    for i, t in enumerate(templates, 1):
        preview = t[:30].replace('\n', ' ')
        text += f"{i}. {preview}...\n"
    await update.message.reply_text(text)
    return DELETE_TEMPLATE_STATE

async def del_template_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        idx = int(update.message.text) - 1
        if 0 <= idx < len(user_templates[user_id]):
            user_templates[user_id].pop(idx)
            save_json_file(TEMPLATES_FILE, user_templates)
            await update.message.reply_text("✅ 𝐓𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐝𝐞𝐥𝐞𝐭𝐞𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲! 🗑️")
        else:
            await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫. 🔄")
    except:
        await update.message.reply_text("❌ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐞𝐧𝐭𝐞𝐫 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫. 🔢")
    context.user_data['current_cmd'] = None
    return ConversationHandler.END

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "ping")
    start_time = time.time()
    msg = await update.message.reply_text("📡 𝐏𝐢𝐧𝐠𝐢𝐧𝐠...")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    await msg.edit_text(f"🏓 𝐏𝐨𝐧𝐠! 📡 𝐋𝐚𝐭𝐞𝐧𝐜𝐲: {latency}𝐦𝐬 ⚡")
    context.user_data['current_cmd'] = None

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "status")
    user_id = update.effective_user.id
    workers = active_workers.get(user_id, [])
    active_count = len([w for w in workers if not w.done()])
    await update.message.reply_text(f"📊 𝐘𝐨𝐮𝐫 𝐚𝐜𝐭𝐢𝐯𝐞 𝐰𝐨𝐫𝐤𝐞𝐫𝐬: {active_count} 🚀")
    context.user_data['current_cmd'] = None

async def accounts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "accounts")
    user_id = update.effective_user.id
    accounts = user_clients.get(user_id, [])
    if not accounts:
        await update.message.reply_text("👥 𝐍𝐨 𝐚𝐜𝐜𝐨𝐮𝐧𝐭𝐬 𝐥𝐨𝐠𝐠𝐞𝐝 𝐢𝐧. ❌")
        return
    text = "👥 𝐘𝐨𝐮𝐫 𝐥𝐨𝐠𝐠𝐞𝐝-𝐢𝐧 𝐚𝐜𝐜𝐨𝐮𝐧𝐭𝐬:\n"
    for i, acc in enumerate(accounts, 1):
        text += f"{i}. 👤 {acc['username']}\n"
    await update.message.reply_text(text)
    context.user_data['current_cmd'] = None

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "stop")
    user_id = update.effective_user.id
    workers = active_workers.get(user_id, [])
    stopped_count = 0
    for task in workers:
        if not task.done():
            task.cancel()
            stopped_count += 1
    active_workers[user_id] = []
    await update.message.reply_text(f"🛑 𝐒𝐭𝐨𝐩𝐩𝐞𝐝 {stopped_count} 𝐛𝐨𝐦𝐛𝐢𝐧𝐠 𝐭𝐡𝐫𝐞𝐚𝐝𝐬 𝐢𝐧𝐬𝐭𝐚𝐧𝐭𝐥𝐲! 💀")
    context.user_data['current_cmd'] = None

async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "login")
    await update.message.reply_text("🔑 𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐲𝐨𝐮𝐫 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 𝐒𝐞𝐬𝐬𝐢𝐨𝐧 𝐈𝐃 𝐭𝐨 𝐥𝐨𝐠𝐢𝐧.")
    return SESSION_ID

async def login_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_id = update.message.text.strip()
    user_id = update.effective_user.id
    u_id = str(user_id)
    
    cl = Client()
    try:
        # Revert to the absolute simplest method that usually works with browser sessions
        # Don't manually set cookies or UA before login_by_sessionid
        # Let the library handle the handshake
        await asyncio.to_thread(cl.login_by_sessionid, session_id)
        
        # If successful, the library will have populated the username
        # We verify by getting account info
        info = await asyncio.to_thread(cl.account_info)
        username = info.username
        
        if user_id not in user_clients:
            user_clients[user_id] = []
        
        user_clients[user_id].append({
            'client': cl,
            'username': username,
            'session_id': session_id
        })

        if u_id not in persisted_sessions:
            persisted_sessions[u_id] = []
        persisted_sessions[u_id].append({'username': username, 'session_id': session_id})
        save_json_file(SESSIONS_FILE, persisted_sessions)
        
        await update.message.reply_text(f"✅ ( {username} ) 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐋𝐨𝐠𝐠𝐞𝐝 𝐈𝐧 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲! 🎉")
        context.user_data['current_cmd'] = None
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"❌ 𝐋𝐨𝐠𝐢𝐧 𝐟𝐚𝐢𝐥𝐞𝐝: {e}. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧. 🔄")
        return SESSION_ID

async def raid_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_and_terminate_previous(update, context, "raid")
    user_id = update.effective_user.id
    if user_id not in user_clients or not user_clients[user_id]:
        await update.message.reply_text("⚠️ 𝐍𝐨 𝐚𝐜𝐜𝐨𝐮𝐧𝐭𝐬 𝐥𝐨𝐠𝐠𝐞𝐝 𝐢𝐧. 𝐔𝐬𝐞 /login 𝐭𝐨 𝐚𝐝𝐝 𝐨𝐧𝐞! 🔑")
        context.user_data['current_cmd'] = None
        return ConversationHandler.END
    
    accounts = user_clients[user_id]
    text = "🤔 𝐖𝐡𝐢𝐜𝐡 𝐚𝐜𝐜𝐨𝐮𝐧𝐭 𝐝𝐨 𝐲𝐨𝐮 𝐰𝐚𝐧𝐭 𝐭𝐨 𝐮𝐬𝐞?\n"
    for i, acc in enumerate(accounts, 1):
        text += f"{i}. 👤 {acc['username']}\n"
    
    await update.message.reply_text(text)
    return RAID_ACCOUNT

async def raid_account_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        choice = int(update.message.text) - 1
        user_id = update.effective_user.id
        context.user_data['selected_account'] = user_clients[user_id][choice]
        await update.message.reply_text("🔗 𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐲𝐨𝐮𝐫 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 𝐠𝐫𝐨𝐮𝐩 𝐨𝐫 𝐜𝐡𝐚𝐭 𝐔𝐑𝐋.")
        return RAID_URL
    except (ValueError, IndexError):
        await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐜𝐡𝐨𝐢𝐜𝐞. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐢𝐜𝐤 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫 𝐟𝐫𝐨𝐦 𝐭𝐡𝐞 𝐥𝐢𝐬𝐭. 🔢")
        return RAID_ACCOUNT

async def raid_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['chat_url'] = update.message.text
    await update.message.reply_text("✅ 𝐆𝐫𝐨𝐮𝐩 𝐢𝐝𝐞𝐧𝐭𝐢𝐟𝐢𝐞𝐝. 𝐇𝐨𝐰 𝐦𝐚𝐧𝐲 𝐭𝐡𝐫𝐞𝐚𝐝𝐬 𝐝𝐨 𝐲𝐨𝐮 𝐰𝐚𝐧𝐭 𝐭𝐨 𝐮𝐬𝐞? (𝐃𝐞𝐟𝐚𝐮𝐥𝐭 𝟑𝟎, 𝐋𝐢𝐦𝐢𝐭 𝟖𝟎) ⚙️")
    return RAID_THREADS

async def raid_threads_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text
    threads = 30
    if val.isdigit():
        threads = min(max(1, int(val)), 80)
    context.user_data['threads'] = threads
    
    user_id = update.effective_user.id
    templates = get_user_templates(user_id)
    text = "📝 𝐒𝐞𝐥𝐞𝐜𝐭 𝐚 𝐫𝐚𝐢𝐝 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞:\n"
    for i, template in enumerate(templates, 1):
        preview = template[:50].replace('\n', ' ')
        text += f"{i}. {preview}...\n"
    
    await update.message.reply_text(text)
    return RAID_TEMPLATE_SELECT

async def raid_template_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        templates = get_user_templates(user_id)
        choice = int(update.message.text) - 1
        context.user_data['selected_template'] = templates[choice]
        await update.message.reply_text("🎯 𝐍𝐨𝐰 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐭𝐡𝐞 𝐭𝐚𝐫𝐠𝐞𝐭 𝐧𝐚𝐦𝐞:")
        return RAID_TARGET
    except (ValueError, IndexError):
        await update.message.reply_text("❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐜𝐡𝐨𝐢𝐜𝐞. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐢𝐜𝐤 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫 𝐟𝐫𝐨𝐦 𝐭𝐡𝐞 𝐥𝐢𝐬𝐭. 🔢")
        return RAID_TEMPLATE_SELECT

async def raid_target_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['target_name'] = update.message.text
    await update.message.reply_text(f"🚀 𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐭𝐨 𝐬𝐞𝐧𝐝 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐟𝐨𝐫 𝐭𝐚𝐫𝐠𝐞𝐭: {update.message.text}. 𝐒𝐞𝐭 𝐝𝐞𝐥𝐚𝐲 (𝐬𝐞𝐜𝐨𝐧𝐝𝐬, 𝟎 𝐟𝐨𝐫 𝐛𝐨𝐦𝐛𝐢𝐧𝐠): ⏳")
    return RAID_DELAY

async def raid_delay_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        delay = float(update.message.text)
        context.user_data['delay'] = delay
        await update.message.reply_text(f"⏳ 𝐃𝐞𝐥𝐚𝐲 𝐬𝐞𝐭 𝐭𝐨 {delay}𝐬. 🔥 𝐁𝐎𝐌𝐁𝐈𝐍𝐆 𝐒𝐓𝐀𝐑𝐓𝐄𝐃 𝐟𝐨𝐫 𝐭𝐚𝐫𝐠𝐞𝐭: {context.user_data['target_name']}! 💀")
        
        user_id = update.effective_user.id
        acc = context.user_data['selected_account']
        cl = acc['client']
        url = context.user_data['chat_url']
        threads = context.user_data['threads']
        target = context.user_data['target_name']
        template = context.user_data['selected_template']
        
        msg = template.replace("{target}", str(target))
        thread_id = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]

        if user_id not in active_workers:
            active_workers[user_id] = []

        async def bomb_worker():
            while True:
                try:
                    await asyncio.to_thread(cl.direct_send, msg, thread_ids=[str(thread_id)])
                    if delay > 0:
                        await asyncio.sleep(delay)
                    else:
                        await asyncio.sleep(0.01)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logging.error(f"Bombing error for user {user_id}: {e}")
                    await asyncio.sleep(1)

        for _ in range(threads):
            task = asyncio.create_task(bomb_worker())
            active_workers[user_id].append(task)
        
        context.user_data['current_cmd'] = None
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐞𝐧𝐭𝐞𝐫 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫 𝐟𝐨𝐫 𝐝𝐞𝐥𝐚𝐲. 🔢")
        return RAID_DELAY

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    old_cmd = context.user_data.get('current_cmd', 'command')
    await update.message.reply_text(f"⚠️ 𝐏𝐫𝐞𝐯𝐢𝐨𝐮𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 ({old_cmd}) 𝐭𝐞𝐫𝐦𝐢𝐧𝐚𝐭𝐞𝐝. 🛑")
    context.user_data['current_cmd'] = None
    return ConversationHandler.END

def main():
    install_dependencies()
    
    if not TELEGRAM_TOKEN:
        logging.error("TELEGRAM_BOT_TOKEN is missing!")
        return

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    login_conv = ConversationHandler(
        entry_points=[CommandHandler('login', login_start)],
        states={
            SESSION_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_session)],
        },
        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(filters.COMMAND, cancel)],
        allow_reentry=True
    )
    
    raid_conv = ConversationHandler(
        entry_points=[CommandHandler('raid', raid_start)],
        states={
            RAID_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, raid_account_choice)],
            RAID_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, raid_url_input)],
            RAID_THREADS: [MessageHandler(filters.TEXT & ~filters.COMMAND, raid_threads_input)],
            RAID_TEMPLATE_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, raid_template_select)],
            RAID_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, raid_target_input)],
            RAID_DELAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, raid_delay_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(filters.COMMAND, cancel)],
        allow_reentry=True
    )

    add_tpl_conv = ConversationHandler(
        entry_points=[CommandHandler('addtemplate', add_template_start)],
        states={
            ADD_TEMPLATE_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_template_receive)],
        },
        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(filters.COMMAND, cancel)],
        allow_reentry=True
    )

    del_tpl_conv = ConversationHandler(
        entry_points=[CommandHandler('deltemplate', del_template_start)],
        states={
            DELETE_TEMPLATE_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, del_template_receive)],
        },
        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(filters.COMMAND, cancel)],
        allow_reentry=True
    )

    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('ping', ping_command))
    application.add_handler(CommandHandler('status', status_command))
    application.add_handler(CommandHandler('accounts', accounts_command))
    application.add_handler(CommandHandler('stop', stop_command))
    application.add_handler(CommandHandler('templates', templates_command))
    application.add_handler(login_conv)
    application.add_handler(raid_conv)
    application.add_handler(add_tpl_conv)
    application.add_handler(del_tpl_conv)
    
    logging.info("Bot is active and VPS ready!")
    application.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
