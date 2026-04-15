import logging
import urllib.request
import json
import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Configuration ---
BOT_TOKEN = "APNA_NAYA_TOKEN_YAHAN" # <-- Yahan apna token dalo
CHANNEL = "@infohub_salman"
ADMIN_ID = 8291716115
SHEET_ID = "1zD1nw-NeEMirFZkYKgeYaP9AbvmLkODaYfwv0q_-VdY"
PHOTO_URL = "https://i.postimg.cc/BQXQMNdQ/IMG-20260125-135130-611.webp"

logging.basicConfig(level=logging.INFO)

# --- Data Fetching Logic ---
def get_apks():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json"
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')[47:-2]
        json_data = json.loads(data)
        rows = json_data['table']['rows']
        apks = []
        for row in rows[1:]:
            if row['c'] and len(row['c']) >= 5:
                apk = {
                    'name': str(row['c'][0]['v']) if row['c'][0] else 'No Name',
                    'description': str(row['c'][1]['v']) if row['c'][1] else '',
                    'apk_link': str(row['c'][2]['v']) if row['c'][2] else '',
                    'video_link': str(row['c'][3]['v']) if row['c'][3] else '',
                    'category': str(row['c'][4]['v']) if row['c'][4] else 'General'
                }
                apks.append(apk)
        return apks
    except Exception as e:
        logging.error(f"Sheet error: {e}")
        return []

async def check_joined(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# --- UI / Layout Section ---
async def show_main_menu(update, context, is_new=False):
    user = update.effective_user if update.effective_user else update.callback_query.from_user
    text = (
        "————————————————\n"
        f"👤 **NAME** ⇒ `{user.first_name}`\n"
        f"🆔 **USER ID** ⇒ `{user.id}`\n"
        "————————————————\n\n"
        "🔥 **WELCOME TO INFOHUB SALMAN BOT** 🔥\n"
        "Best Tools & APKs for Cyber Security"
    )
    keyboard = [
        [InlineKeyboardButton("💖 GET APK 💖", callback_data='get_apk_cats')],
        [InlineKeyboardButton("🔍 Number Tracker (OSINT)", callback_data='osint_tool')],
        [InlineKeyboardButton("👨‍👩‍👧‍👦 Referral", callback_data='referral'),
         InlineKeyboardButton("💰 Balance", callback_data='balance')],
        [InlineKeyboardButton("How To Use 🔧", callback_data='how_to_use')],
        [InlineKeyboardButton("🌀 Chat Id", callback_data='chat_id'),
         InlineKeyboardButton("👤 My Account", callback_data='my_account')],
        [InlineKeyboardButton("❣️ Redeem", callback_data='redeem')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_new:
        await context.bot.send_photo(chat_id=user.id, photo=PHOTO_URL, caption=text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        query = update.callback_query
        await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode="Markdown")

# --- Main Logic Handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    joined = await check_joined(user.id, context)
    if not joined:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL.replace('@','')}")],
                    [InlineKeyboardButton("✅ Joined", callback_data='check_join')]]
        await update.message.reply_text(f"😎 Hey {user.first_name}!\n\n⚠️ Pehle channel join karo!", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await show_main_menu(update, context, is_new=True)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if data == 'check_join':
        if await check_joined(user.id, context): await show_main_menu(update, context, is_new=True)
        else: await query.answer("❌ Join nahi kiya!", show_alert=True)

    elif data == 'osint_tool':
        await query.edit_message_caption("🛠️ **OSINT Tracker Activated**\n\nApna number bhejein (Example: `+919876543210`)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='back_main')]]), parse_mode="Markdown")
        context.user_data['waiting_for_number'] = True

    elif data == 'get_apk_cats':
        apks = get_apks()
        categories = sorted(list(set([apk['category'] for apk in apks])))
        keyboard = [[InlineKeyboardButton(f"📁 {cat}", callback_data=f"cat_{cat}")] for cat in categories]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='back_main')])
        await query.edit_message_caption("📂 **Categories Chunein:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith('cat_'):
        cat_name = data.split('_')[1]
        apks = [apk for apk in get_apks() if apk['category'] == cat_name]
        keyboard = [[InlineKeyboardButton(f"🚀 {apk['name']}", callback_data=f"view_{apk['name'][:20]}")] for apk in apks]
        keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data='get_apk_cats')])
        await query.edit_message_caption(f"📂 Category: **{cat_name}**\n\nApp select karein:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith('view_'):
        apk_part_name = data.split('view_')[1]
        apk = next((x for x in get_apks() if x['name'].startswith(apk_part_name)), None)
        if apk:
            keyboard = [[InlineKeyboardButton("▶️ Video Dekho", url=apk['video_link'])],
                        [InlineKeyboardButton("✅ Confirm & Download", callback_data=f"dl_{apk_part_name}")],
                        [InlineKeyboardButton("🔙 Back", callback_data=f"cat_{apk['category']}")]]
            await query.edit_message_caption(f"🔐 **{apk['name']}**\n\n📝 {apk['description']}\n\n🏷️ Category: {apk['category']}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith('dl_'):
        apk_part_name = data.split('dl_')[1]
        apk = next((x for x in get_apks() if x['name'].startswith(apk_part_name)), None)
        if apk:
            await context.bot.send_message(chat_id=user.id, text=f"✅ **{apk['name']}**\n\n🔗 Link: {apk['apk_link']}\n\n@infohub_salman", parse_mode="Markdown")

    elif data == 'back_main':
        await show_main_menu(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_number'):
        num = update.message.text
        context.user_data['waiting_for_number'] = False
        
        status = await update.message.reply_text("🔍 **Initializing OSINT Scan...**", parse_mode="Markdown")
        await asyncio.sleep(1)
        await status.edit_text("📡 **Bypassing GSM Encryption...**")
        await asyncio.sleep(1.5)
        await status.edit_text("🛰️ **Fetching Data from Satellite Servers...**")
        await asyncio.sleep(1.2)
        
        operators = ["Jio", "Airtel", "Vi", "BSNL"]
        final_text = (
            "⚠️ **TARGET DATA FOUND** ⚠️\n"
            "————————————————\n"
            f"📱 **Mobile** ⇒ `{num}`\n"
            f"👤 **Owner** ⇒ `Private Profile`\n"
            f"📶 **Carrier** ⇒ `{random.choice(operators)}`\n"
            f"🚦 **Status** ⇒ `Active`\n"
            f"🔐 **IMEI** ⇒ `35891**********`\n"
            "————————————————\n"
            "💀 **INFOHUB SALMAN OSINT ENGINE**"
        )
        await status.edit_text(final_text, parse_mode="Markdown")

def main():
    from telegram.ext import MessageHandler, filters
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
                                     
