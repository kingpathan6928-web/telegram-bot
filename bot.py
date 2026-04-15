import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8004368216:AAEGFuNmjMvnazODL1scTYB-b-j6aFdxucI"
CHANNEL = "@infohub_salman"
ADMIN_ID = 8291716115
SHEET_ID = "1-0qJ9L_94f_9dLxt0HPbLadPXEuIdIHIRb_ICn38dck"

logging.basicConfig(level=logging.INFO)

# Google Sheet se data lena
def get_apks():
    try:
        import urllib.request
        import json
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json"
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')
        data = data[47:-2]
        json_data = json.loads(data)
        rows = json_data['table']['rows']
        apks = []
        for row in rows[1:]:
            if row['c'][0]:
                apk = {
                    'name': row['c'][0]['v'] if row['c'][0] else '',
                    'description': row['c'][1]['v'] if row['c'][1] else '',
                    'apk_link': row['c'][2]['v'] if row['c'][2] else '',
                    'video_link': row['c'][3]['v'] if row['c'][3] else '',
                    'category': row['c'][4]['v'] if row['c'][4] else ''
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    joined = await check_joined(user.id, context)
    if not joined:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/infohub_salman")],
            [InlineKeyboardButton("✅ Joined", callback_data='check_join')]
        ]
        await update.message.reply_text(
            f"😎 Hey {user.first_name}!\n\n⚠️ Pehle channel join karo!\nJoin karne ke baad ✅ Joined dabao!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await show_main_menu(update, context, is_new=True)

async def show_main_menu(update, context, is_new=False):
    user = update.effective_user if hasattr(update, 'effective_user') else update.from_user
    keyboard = [
        [InlineKeyboardButton("💝 GET APK 💝", callback_data='get_apk')],
        [InlineKeyboardButton("👫 Referral", callback_data='referral'),
         InlineKeyboardButton("💰 Balance", callback_data='balance')],
        [InlineKeyboardButton("🔧 How To Use", callback_data='how_to_use')],
        [InlineKeyboardButton("↩️ Chat Id", callback_data='chat_id'),
         InlineKeyboardButton("👤 My Account", callback_data='my_account')],
        [InlineKeyboardButton("❤️ Redeem", callback_data='redeem')]
    ]
    text = f"😎 Hey {user.first_name}!\n\n🔐 Welcome To Infohub Salman Bot!\n\n• Cyber Security Tools\n• Free APKs\n• Latest Updates\n\n@infohub_salman"
    if is_new:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if query.data == 'check_join':
        joined = await check_joined(user.id, context)
        if joined:
            await show_main_menu(query, context)
        else:
            await query.answer("❌ Pehle channel join karo!", show_alert=True)

    elif query.data == 'get_apk':
        apks = get_apks()
        if not apks:
            await query.edit_message_text("❌ Abhi koi APK available nahi!")
            return
        keyboard = []
        for i, apk in enumerate(apks):
            keyboard.append([InlineKeyboardButton(
                f"🔐 {apk['name']}", callback_data=f'apk_{i}'
            )])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='back_main')])
        await query.edit_message_text(
            "💝 GET APK 💝\n\nAPK choose karo:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith('apk_'):
        index = int(query.data.split('_')[1])
        apks = get_apks()
        apk = apks[index]
        keyboard = [
            [InlineKeyboardButton("▶️ Video Dekho", url=apk['video_link'])],
            [InlineKeyboardButton("✅ Confirm & Download", callback_data=f'confirm_{index}')],
            [InlineKeyboardButton("🔙 Back", callback_data='get_apk')]
        ]
        await query.edit_message_text(
            f"🔐 {apk['name']}\n\n📝 {apk['description']}\n\n🏷️ Category: {apk['category']}\n\n▶️ Pehle video dekho phir confirm karo!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith('confirm_'):
        index = int(query.data.split('_')[1])
        apks = get_apks()
        apk = apks[index]
        await query.message.reply_text(
            f"✅ {apk['name']}\n\n⬇️ Download link:\n{apk['apk_link']}\n\n@infohub_salman"
        )

    elif query.data == 'referral':
        invite_link = f"https://t.me/Salman_hging_bot?start=ref{user.id}"
        keyboard = [
            [InlineKeyboardButton("🔍 My Refers", callback_data='my_refers'),
             InlineKeyboardButton("🔥 Top List", callback_data='top_list')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
        ]
        await query.edit_message_text(
            f"👫 Referral\n\n🤝 Total Refers = 0\n\n🔗 Your Link:\n{invite_link}\n\n💰 10 Coins Per Invite!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'balance':
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='back_main')]]
        await query.edit_message_text(
            f"💰 Balance\n\n👤 User: {user.first_name}\n💰 Balance: 0 Points\n\n👫 Refer karo aur kamao!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'chat_id':
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='back_main')]]
        await query.edit_message_text(
            f"↩️ Chat Id\n\n👤 {user.first_name}\n🆔 YOUR ID: {user.id}\n💬 CHAT ID: {user.id}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'my_account':
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='back_main')]]
        await query.edit_message_text(
            f"👤 My Account\n\n😎 Name: {user.first_name}\n🆔 ID: {user.id}\n👤 Username: @{user.username}\n💰 Balance: 0 Points\n👫 Referrals: 0",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'how_to_use':
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='back_main')]]
        await query.edit_message_text(
            "🔧 How To Use\n\n1️⃣ Channel join karo\n2️⃣ GET APK pe click karo\n3️⃣ Tool choose karo\n4️⃣ Video dekho\n5️⃣ Confirm karo\n6️⃣ APK download karo!\n\n❓ Help: @infohub_salman",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'redeem':
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='back_main')]]
        await query.edit_message_text(
            "❤️ Redeem\n\n😘 Code bhejo redeem karne ke liye!\n\n💰 Coins kaise kamayein?\n👫 Refer karo = 10 Coins\n\n@infohub_salman",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'back_main':
        await show_main_menu(query, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button)
    main()
        
