import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8005668138:AAF74r146ylnOb_9V-bbN4wAqV_FQwxKCwo"  # @BotFather dan olingan token

# Xitoy ombori umumiy ID (barcha userlarga bir xil ko'rsatiladi)
WAREHOUSE_ID = "CNSHA001"
WAREHOUSE_NAME = "Shanghai Warehouse"
WAREHOUSE_ADDRESS = "No.88, Pudong New Area, Shanghai, China"

# ====================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Oddiy xotira (production uchun bazaga almashtiriladi)
# Format: { user_id: { "track_numbers": ["TN001", "TN002", ...] } }
user_data_store = {}


def get_user_data(user_id: int) -> dict:
    """User ma'lumotlarini olish yoki yangi yaratish"""
    if user_id not in user_data_store:
        user_data_store[user_id] = {
            "track_numbers": []
        }
    return user_data_store[user_id]


# ==================== BUYRUQLAR ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start - barcha userlarga bir xil ombor ID beradi,
    lekin har bir user o'zining trek raqamlarini ko'radi
    """
    user = update.effective_user
    user_id = user.id
    
    # User ma'lumotlarini olish/yaratish
    data = get_user_data(user_id)
    trek_count = len(data["track_numbers"])
    
    keyboard = [
        [InlineKeyboardButton("📦 Trek raqam qo'shish", callback_data="add_track")],
        [InlineKeyboardButton("📋 Mening yuklarim", callback_data="my_tracks")],
        [InlineKeyboardButton("🔍 Trek raqam tekshirish", callback_data="check_track")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        f"👋 Salom, {user.first_name}!\n\n"
        f"🏭 **Sizning ombor ma'lumotlaringiz:**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Ombor ID: `{WAREHOUSE_ID}`\n"
        f"🏪 Ombor nomi: {WAREHOUSE_NAME}\n"
        f"📍 Manzil: {WAREHOUSE_ADDRESS}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 Sizning yuklaringiz soni: **{trek_count} ta**\n\n"
        f"Quyidagi menyudan tanlang:"
    )
    
    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def add_track_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trek raqam qo'shish - /add TN12345 formatida"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "📝 Trek raqamni quyidagi formatda yuboring:\n"
            "`/add TN12345678`\n\n"
            "Yoki shunchaki trek raqamni yuboring.",
            parse_mode="Markdown"
        )
        return
    
    track_number = context.args[0].upper().strip()
    data = get_user_data(user_id)
    
    if track_number in data["track_numbers"]:
        await update.message.reply_text(
            f"⚠️ `{track_number}` allaqachon qo'shilgan!",
            parse_mode="Markdown"
        )
        return
    
    data["track_numbers"].append(track_number)
    
    await update.message.reply_text(
        f"✅ Trek raqam muvaffaqiyatli qo'shildi!\n\n"
        f"🔖 Trek: `{track_number}`\n"
        f"🏭 Ombor: `{WAREHOUSE_ID}`\n"
        f"📦 Jami yuklaringiz: {len(data['track_numbers'])} ta",
        parse_mode="Markdown"
    )


async def my_tracks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/mytracks - foydalanuvchining barcha trek raqamlarini ko'rsatish"""
    user_id = update.effective_user.id
    data = get_user_data(user_id)
    tracks = data["track_numbers"]
    
    if not tracks:
        await update.message.reply_text(
            "📭 Sizda hali hech qanday yuk yo'q.\n\n"
            "Trek raqam qo'shish uchun:\n"
            "`/add TREKNOMER`",
            parse_mode="Markdown"
        )
        return
    
    text = f"📦 **Sizning yuklaringiz** ({len(tracks)} ta):\n"
    text += f"🏭 Ombor: `{WAREHOUSE_ID}`\n\n"
    
    for i, track in enumerate(tracks, 1):
        text += f"{i}. `{track}`\n"
    
    keyboard = [[InlineKeyboardButton("🗑 Yuk o'chirish", callback_data="delete_track")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def check_track_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/check TN12345 - trek raqam o'z yukiga tegishli ekanligini tekshirish"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "🔍 Tekshirish uchun:\n`/check TREKNOMER`",
            parse_mode="Markdown"
        )
        return
    
    track_number = context.args[0].upper().strip()
    data = get_user_data(user_id)
    
    if track_number in data["track_numbers"]:
        await update.message.reply_text(
            f"✅ **TASDIQLANDI!**\n\n"
            f"🔖 Trek: `{track_number}`\n"
            f"👤 Bu yuk SIZGA tegishli\n"
            f"🏭 Ombor: `{WAREHOUSE_ID}`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ `{track_number}` - bu yuk sizga tegishli emas\n"
            f"yoki ro'yxatga olinmagan.",
            parse_mode="Markdown"
        )


# ==================== MATN HANDLER ====================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Oddiy matn kelganda - trek raqam sifatida qo'shish"""
    user_id = update.effective_user.id
    text = update.message.text.strip().upper()
    
    # Agar matn trek raqamga o'xshasa (harflar + raqamlar)
    if len(text) >= 5 and any(c.isdigit() for c in text) and any(c.isalpha() for c in text):
        data = get_user_data(user_id)
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Ha, qo'shish", callback_data=f"confirm_add_{text}"),
                InlineKeyboardButton("❌ Yo'q", callback_data="cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📦 `{text}` - bu trek raqamni qo'shmoqchimisiz?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "ℹ️ Trek raqam kiritish uchun: `/add TREKNOMER`\n"
            "Yoki shunchaki trek raqamni yuboring (masalan: `TN12345678`)",
            parse_mode="Markdown"
        )


# ==================== CALLBACK HANDLER ====================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline tugmalar uchun handler"""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    data_str = query.data
    
    if data_str == "add_track":
        await query.message.reply_text(
            "📝 Trek raqamni yuboring:\n"
            "Misol: `TN12345678` yoki `/add TN12345678`",
            parse_mode="Markdown"
        )
    
    elif data_str == "my_tracks":
        data = get_user_data(user_id)
        tracks = data["track_numbers"]
        
        if not tracks:
            await query.message.reply_text("📭 Sizda hali yuk yo'q.")
            return
        
        text = f"📦 **Sizning yuklaringiz** ({len(tracks)} ta):\n"
        text += f"🏭 Ombor ID: `{WAREHOUSE_ID}`\n\n"
        for i, track in enumerate(tracks, 1):
            text += f"{i}. `{track}`\n"
        
        await query.message.reply_text(text, parse_mode="Markdown")
    
    elif data_str == "check_track":
        await query.message.reply_text(
            "🔍 Tekshirish uchun trek raqamni yuboring:\n`/check TREKNOMER`",
            parse_mode="Markdown"
        )
    
    elif data_str.startswith("confirm_add_"):
        track_number = data_str.replace("confirm_add_", "")
        user_data = get_user_data(user_id)
        
        if track_number not in user_data["track_numbers"]:
            user_data["track_numbers"].append(track_number)
            await query.message.reply_text(
                f"✅ `{track_number}` qo'shildi!\n"
                f"🏭 Ombor: `{WAREHOUSE_ID}`\n"
                f"📦 Jami: {len(user_data['track_numbers'])} ta yuk",
                parse_mode="Markdown"
            )
        else:
            await query.message.reply_text(f"⚠️ `{track_number}` allaqachon mavjud.")
    
    elif data_str == "delete_track":
        data = get_user_data(user_id)
        tracks = data["track_numbers"]
        
        if not tracks:
            await query.message.reply_text("📭 O'chirish uchun yuk yo'q.")
            return
        
        keyboard = []
        for track in tracks:
            keyboard.append([InlineKeyboardButton(f"🗑 {track}", callback_data=f"del_{track}")])
        keyboard.append([InlineKeyboardButton("↩️ Orqaga", callback_data="cancel")])
        
        await query.message.reply_text(
            "Qaysi yukni o'chirmoqchisiz?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data_str.startswith("del_"):
        track_to_delete = data_str[4:]
        user_data = get_user_data(user_id)
        
        if track_to_delete in user_data["track_numbers"]:
            user_data["track_numbers"].remove(track_to_delete)
            await query.message.reply_text(
                f"✅ `{track_to_delete}` o'chirildi.",
                parse_mode="Markdown"
            )
        else:
            await query.message.reply_text("❌ Trek raqam topilmadi.")
    
    elif data_str == "cancel":
        await query.message.reply_text("↩️ Bekor qilindi.")


# ==================== MAIN ====================

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Buyruqlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_track_command))
    app.add_handler(CommandHandler("mytracks", my_tracks_command))
    app.add_handler(CommandHandler("check", check_track_command))
    
    # Callback va matn
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
