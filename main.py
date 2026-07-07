import os
import asyncio
import aiohttp
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable not set!")
    exit(1)

# Supported languages
LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "ms": "Malay",
    "sw": "Swahili",
    "ha": "Hausa",
    "yo": "Yoruba",
    "ig": "Igbo",
    "zu": "Zulu",
    "af": "Afrikaans",
    "el": "Greek",
    "he": "Hebrew",
    "hu": "Hungarian",
    "ro": "Romanian",
    "sk": "Slovak",
    "sv": "Swedish",
    "uk": "Ukrainian",
    "da": "Danish",
    "fi": "Finnish",
    "no": "Norwegian",
    "fa": "Persian",
    "ur": "Urdu",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam"
}

# ==================== KEYBOARDS ====================
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔍 Detect Language", callback_data="detect")],
        [InlineKeyboardButton("📋 Language List", callback_data="languages")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== COMMAND HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    welcome = (
        f"🌍 Welcome {user.first_name} to **WhatLangBot**!\n\n"
        "🔍 Your language detection assistant!\n\n"
        "**✨ Features:**\n"
        "• 🔍 Detect language of any text\n"
        "• 📊 Shows confidence percentage\n"
        "• 🌍 Supports 40+ languages\n"
        "• 📋 List all supported languages\n\n"
        "**📖 How to use:**\n"
        "1. Send me any text\n"
        "2. I'll detect the language!\n"
        "3. Get results with confidence\n\n"
        "⬇️ Send text or click 'Detect Language'!"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 **WhatLangBot - Help Guide**\n\n"
        "**🔍 How to Detect Language:**\n"
        "• Send any text message\n"
        "• Or click 'Detect Language' button\n"
        "• I'll detect the language instantly!\n\n"
        "**🔧 Commands:**\n"
        "• `/start` - Start the bot\n"
        "• `/help` - Show this help\n"
        "• `/languages` - List all languages\n"
        "• `/detect [text]` - Detect language of text\n\n"
        "**📊 What You Get:**\n"
        "• Detected language name\n"
        "• Language code\n"
        "• Confidence percentage\n\n"
        "**💡 Examples:**\n"
        "• Send: 'Hello world' → English (99%)\n"
        "• Send: 'Bonjour' → French (95%)\n"
        "• Send: 'Hola' → Spanish (97%)"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_list = "🌍 **Supported Languages**\n\n"
    for code, name in sorted(LANGUAGES.items(), key=lambda x: x[1]):
        lang_list += f"• {name} (`{code}`)\n"
    await update.message.reply_text(lang_list, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def detect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide text to detect.\n\n"
            "Example: `/detect Hello world`\n"
            "Or just send me any text!",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
    
    text = " ".join(context.args)
    await detect_language_and_reply(update, text)

# ==================== CALLBACK HANDLERS ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "detect":
        await query.edit_message_text(
            "🔍 **Send me any text**\n\n"
            "I'll detect the language for you!\n\n"
            "📝 Just type or paste any text.\n"
            "💡 You can also use /detect [text]",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    
    elif data == "languages":
        lang_list = "🌍 **Supported Languages**\n\n"
        for code, name in sorted(LANGUAGES.items(), key=lambda x: x[1]):
            lang_list += f"• {name} (`{code}`)\n"
        await query.edit_message_text(lang_list, parse_mode="Markdown", reply_markup=get_main_keyboard())
    
    elif data == "help":
        help_text = (
            "📖 **WhatLangBot - Help Guide**\n\n"
            "**🔍 How to Detect Language:**\n"
            "• Send any text message\n"
            "• Or click 'Detect Language' button\n"
            "• I'll detect the language instantly!\n\n"
            "**🔧 Commands:**\n"
            "• `/start` - Start the bot\n"
            "• `/help` - Show this help\n"
            "• `/languages` - List all languages\n"
            "• `/detect [text]` - Detect language of text\n\n"
            "**📊 What You Get:**\n"
            "• Detected language name\n"
            "• Language code\n"
            "• Confidence percentage"
        )
        await query.edit_message_text(help_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# ==================== DETECTION FUNCTIONS ====================
async def detect_language(text: str):
    """Detect language using LibreTranslate API"""
    if not text or len(text.strip()) < 2:
        return None
    
    try:
        url = "https://libretranslate.com/detect"
        payload = {"q": text}
        headers = {"Content-Type": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        return {
                            "language": data[0].get("language"),
                            "confidence": data[0].get("confidence", 0)
                        }
                return None
    except asyncio.TimeoutError:
        logger.warning("Detection API timeout")
        return None
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return None

async def detect_language_and_reply(update: Update, text: str):
    """Detect language and reply with results"""
    if len(text.strip()) < 2:
        await update.message.reply_text(
            "❌ **Text too short**\n\n"
            "Please send at least 2 characters for accurate detection.",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        "🔍 **Detecting language...**\n\n"
        "⏳ Analyzing text...",
        parse_mode="Markdown"
    )
    
    result = await detect_language(text)
    
    if result:
        lang_code = result.get("language", "unknown")
        confidence = result.get("confidence", 0) * 100
        
        lang_name = LANGUAGES.get(lang_code, lang_code.upper())
        
        await processing_msg.delete()
        
        # Create confidence bar
        bar_length = min(int(confidence / 10), 10)
        confidence_bar = "▰" * bar_length + "▱" * (10 - bar_length)
        
        await update.message.reply_text(
            f"✅ **Language Detected!**\n\n"
            f"🌍 **Language:** {lang_name}\n"
            f"🔤 **Code:** `{lang_code}`\n"
            f"📊 **Confidence:** {confidence:.1f}%\n"
            f"📈 **Bar:** {confidence_bar}\n\n"
            f"📝 **Text:** _{text[:100]}{'...' if len(text) > 100 else ''}_\n\n"
            f"💡 Try sending more text for better accuracy!",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    else:
        await processing_msg.edit_text(
            "❌ **Detection Failed**\n\n"
            "I couldn't detect the language. Please try:\n"
            "• Sending longer text (minimum 5-10 words)\n"
            "• Sending text in a different language\n"
            "• Checking if the language is supported\n\n"
            "If the problem persists, try using the /detect command.",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

# ==================== MESSAGE HANDLER ====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if text.startswith('/'):
        return
    
    await detect_language_and_reply(update, text)

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Update {update} caused error {context.error}")

# ==================== MAIN FUNCTION ====================
def main():
    print("=" * 50)
    print("🌍 Starting WhatLangBot...")
    print(f"🌍 Supported languages: {len(LANGUAGES)}")
    print("✅ Bot is ready!")
    print("=" * 50)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("languages", languages_command))
    application.add_handler(CommandHandler("detect", detect_command))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_error_handler(error_handler)
    
    print("✅ Bot is running! Press Ctrl+C to stop.")
    print("=" * 50)
    
    application.run_polling()

if __name__ == "__main__":
    main()
