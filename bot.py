import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

import os
from dotenv import load_dotenv
from converter import CATEGORIES, get_unit_display_name, format_number

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables.")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- User State Management ---
user_sessions = {}

# --- Keyboard Builders ---
def get_main_keyboard():
    """Main menu keyboard with all categories."""
    keyboard = []
    for key, cat in CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(cat['name'], callback_data=f"cat_{key}")])
    return InlineKeyboardMarkup(keyboard)

def get_units_keyboard(category_key, action):
    """Keyboard for unit selection (from or to)."""
    category = CATEGORIES[category_key]
    keyboard = []
    row = []
    for i, unit in enumerate(category['units']):
        display_name = get_unit_display_name(unit)
        row.append(InlineKeyboardButton(display_name, callback_data=f"{action}_{category_key}_{unit}"))
        if len(row) == 3:  # 3 buttons per row for cleaner look
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(keyboard)

def get_back_to_main_keyboard():
    """Keyboard to return to main menu."""
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_categories")]]
    return InlineKeyboardMarkup(keyboard)

# --- Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    user = update.effective_user
    user_id = user.id
    user_sessions[user_id] = {}  # Reset session

    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        f"Welcome to the **Unit Converter Bot**.\n"
        f"Please select a category to begin:\n\n"
        f"You can convert between Length, Weight, Temperature, Volume, Area, Speed, Time, and Data sizes.",
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command."""
    help_text = """
🤖 **Unit Converter Bot - Help**

**Commands:**
/start - Start the bot and select a category
/help - Show this help message
/about - About this bot
/cancel - Cancel current operation

**How to convert:**
1. Select a category (e.g., Length, Weight).
2. Choose the unit you want to convert **from**.
3. Choose the unit you want to convert **to**.
4. Send me the value you want to convert.

**Example:**
1. Category: Length
2. From: Kilometers
3. To: Miles
4. Value: 10

That's it! The bot will show you the converted result.
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /about command."""
    about_text = """
⚡ **Unit Converter Bot v1.0**

A simple and fast unit converter right inside Telegram.

**Features:**
• 8 categories with 40+ units
• Easy button-based navigation
• No external API required

**Tech Stack:**
• Python + python-telegram-bot
• Deployed on Railway

**Developer:** @YourUsername
"""
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /cancel command."""
    user_id = update.effective_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    await update.message.reply_text(
        "🔄 Operation cancelled. Use /start to begin again.",
        reply_markup=get_main_keyboard()
    )

# --- Callback Query Handlers ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles all button callback queries."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # Initialize session if it doesn't exist
    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    # Back to categories / main menu
    if data == "back_to_categories":
        user_sessions[user_id] = {}
        await query.edit_message_text(
            "🏠 **Main Menu**\n\nPlease select a category:",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return

    # Category selection
    if data.startswith("cat_"):
        category_key = data.replace("cat_", "")
        if category_key not in CATEGORIES:
            await query.edit_message_text("❌ Invalid category. Please try again.")
            return

        user_sessions[user_id]['category'] = category_key
        category = CATEGORIES[category_key]
        
        await query.edit_message_text(
            f"📂 **{category['name']}**\n\n"
            f"Step 1: Choose the unit you want to convert **FROM**:",
            parse_mode='Markdown',
            reply_markup=get_units_keyboard(category_key, "from")
        )
        return

    # Unit selection (from or to)
    if data.startswith("from_") or data.startswith("to_"):
        parts = data.split("_")
        action = parts[0]  # 'from' or 'to'
        category_key = parts[1]
        unit = parts[2]

        if action == "from":
            user_sessions[user_id]['from_unit'] = unit
            category = CATEGORIES[category_key]
            await query.edit_message_text(
                f"📂 **{category['name']}**\n\n"
                f"From: **{get_unit_display_name(unit)}**\n"
                f"Step 2: Choose the unit you want to convert **TO**:",
                parse_mode='Markdown',
                reply_markup=get_units_keyboard(category_key, "to")
            )
        elif action == "to":
            user_sessions[user_id]['to_unit'] = unit
            category = CATEGORIES[category_key]
            from_unit = user_sessions[user_id].get('from_unit')
            
            if not from_unit:
                await query.edit_message_text(
                    "⚠️ Something went wrong. Please start over with /start."
                )
                return

            # Show confirmation and ask for value
            await query.edit_message_text(
                f"📂 **{category['name']}**\n\n"
                f"✅ Conversion setup complete!\n"
                f"From: **{get_unit_display_name(from_unit)}**\n"
                f"To: **{get_unit_display_name(unit)}**\n\n"
                f"Step 3: Send me the numeric value to convert.\n"
                f"(e.g., `10` or `3.14`)",
                parse_mode='Markdown',
                reply_markup=get_back_to_main_keyboard()
            )

# --- Message Handlers ---
async def handle_value_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the numeric value sent by the user for conversion."""
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_sessions:
        await update.message.reply_text(
            "🚀 Let's start! Use /start to select a category.",
            reply_markup=get_main_keyboard()
        )
        return

    session = user_sessions[user_id]
    if 'category' not in session or 'from_unit' not in session or 'to_unit' not in session:
        await update.message.reply_text(
            "⚠️ Please set up a conversion first.\n"
            "Use /start to select a category and units.",
            reply_markup=get_main_keyboard()
        )
        return

    # Try to parse the value
    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text(
            "❌ Please send a valid number.\n"
            "For example: `10`, `5.5`, or `-3.14`",
            parse_mode='Markdown'
        )
        return

    # Perform the conversion
    category_key = session['category']
    from_unit = session['from_unit']
    to_unit = session['to_unit']
    category = CATEGORIES[category_key]
    convert_func = category['func']

    try:
        result = convert_func(value, from_unit, to_unit)
        if result is None:
            raise ValueError("Conversion returned None")
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        await update.message.reply_text(
            f"❌ Sorry, an error occurred during conversion.\n"
            f"Please try again or use /start to restart."
        )
        return

    # Format the result and send it
    formatted_value = format_number(value)
    formatted_result = format_number(result)
    from_display = get_unit_display_name(from_unit)
    to_display = get_unit_display_name(to_unit)

    result_text = (
        f"✅ **Conversion Result**\n\n"
        f"`{formatted_value}` {from_display} = `{formatted_result}` {to_display}\n\n"
        f"🔁 To do another conversion, just select a new unit or category from the menu."
    )

    # Send the result with a "Continue" button
    keyboard = [
        [InlineKeyboardButton("🔄 Convert More", callback_data="back_to_categories")],
        [InlineKeyboardButton("⚡ Quick Reverse", callback_data=f"reverse_{category_key}_{from_unit}_{to_unit}_{value}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        result_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

    # Reset the session's unit selection, but keep the last conversion for "Quick Reverse"
    session['last_conversion'] = {
        'category': category_key,
        'from': from_unit,
        'to': to_unit,
        'value': value
    }
    # Clear the current units so user must select new ones or use reverse
    session['from_unit'] = None
    session['to_unit'] = None

async def handle_quick_reverse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the quick reverse button callback."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if not data.startswith("reverse_"):
        return

    parts = data.split("_")
    category_key = parts[1]
    from_unit = parts[2]
    to_unit = parts[3]
    try:
        value = float(parts[4])
    except (ValueError, IndexError):
        await query.edit_message_text("❌ Error with reverse conversion. Please start over.")
        return

    # Perform reverse conversion (swap from and to)
    category = CATEGORIES[category_key]
    convert_func = category['func']
    
    try:
        result = convert_func(value, to_unit, from_unit)
        if result is None:
            raise ValueError("Conversion returned None")
    except Exception as e:
        logger.error(f"Reverse conversion error: {str(e)}")
        await query.edit_message_text("❌ Error performing reverse conversion. Please try again.")
        return

    formatted_value = format_number(value)
    formatted_result = format_number(result)
    from_display = get_unit_display_name(to_unit)  # Swapped
    to_display = get_unit_display_name(from_unit)   # Swapped

    result_text = (
        f"✅ **Reverse Conversion Result**\n\n"
        f"`{formatted_value}` {from_display} = `{formatted_result}` {to_display}\n\n"
        f"🔁 Use the menu to continue."
    )

    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_categories")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        result_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# --- Main Function ---
def main():
    """Start the bot."""
    logger.info("Starting Unit Converter Bot...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("cancel", cancel_command))

    # Callback query handler for all buttons
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(cat_|from_|to_|back_to_categories)"))
    application.add_handler(CallbackQueryHandler(handle_quick_reverse, pattern="^reverse_"))

    # Message handler for numeric values
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_value_message))

    logger.info("Bot is running and polling for updates...")
    application.run_polling()

if __name__ == '__main__':
    main()
