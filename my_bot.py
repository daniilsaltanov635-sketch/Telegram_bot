# --- 1. ИМПОРТ БИБЛИОТЕК ---
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# --- 2. КОНСТАНТЫ ---
# Этапы диалога (по порядку)
ASK_SERVICE, ASK_NAME, ASK_PROFESSION, ASK_WISH, ASK_PHONE = range(5)

# --- 3. ОБРАБОТЧИКИ СООБЩЕНИЙ ---
# --- 1. ИМПОРТ БИБЛИОТЕК ---
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# --- 2. КОНСТАНТЫ ---
# Этапы диалога (по порядку)
ASK_SERVICE, ASK_NAME, ASK_PROFESSION, ASK_WISH, ASK_PHONE = range(5)

# --- 3. ОБРАБОТЧИКИ СООБЩЕНИЙ ---
# Шаг 1: старт — выбор услуги
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ищу работу", callback_data='job')],
        [InlineKeyboardButton("Ищу место в садике", callback_data='kindergarten')],
        [InlineKeyboardButton("Разработка бизнес-идеи", callback_data='business')],
        [InlineKeyboardButton("Обучение новой профессии", callback_data='education')],
        [InlineKeyboardButton("Консультация по документам", callback_data='documents')],
        [InlineKeyboardButton("Помощь с жильём", callback_data='apartment')],
        [InlineKeyboardButton("Другое", callback_data='other')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Привет! Выбери услугу 👇", reply_markup=reply_markup)
    return ASK_SERVICE

# Шаг 2: сохраняем выбранную услугу
async def service_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["service"] = query.data
    await query.edit_message_text("✍ Введите ваше имя и фамилию:")
    return ASK_NAME

# Шаг 3: спрашиваем профессию
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("👔 Кто вы по профессии или чем занимаетесь?")
    return ASK_PROFESSION

# Шаг 4: спрашиваем кем хочет работать
async def get_profession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["profession"] = update.message.text
    await update.message.reply_text("💡 Кем бы вы хотели работать или что хотите изучить?")
    return ASK_WISH

# Шаг 5: просим номер телефона
async def get_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wish"] = update.message.text
    contact_button = KeyboardButton("📞 Отправить номер телефона", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("📱 Отправьте ваш номер телефона:", reply_markup=reply_markup)
    return ASK_PHONE

# Шаг 6: сохраняем данные
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.contact.phone_number if update.message.contact else update.message.text
    context.user_data["phone"] = phone

    # --- Сохраняем всё в файл ---
    with open("users_data.txt", "a", encoding="utf-8") as f:
        f.write(
            f"Услуга: {context.user_data['service']}\n"
            f"Имя: {context.user_data['name']}\n"
            f"Профессия: {context.user_data['profession']}\n"
            f"Хочет: {context.user_data['wish']}\n"
            f"Телефон: {context.user_data['phone']}\n"
            f"{'-'*30}\n"
        )

    await update.message.reply_text("✅ Спасибо! Ваши данные сохранены. С вами скоро свяжутся.")
    await update.message.reply_text("Чтобы оставить ещё одну заявку, введите /start")
    return ConversationHandler.END

# Команда /cancel — прерывает диалог
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Диалог отменён.")
    return ConversationHandler.END


# --- 4. ЗАПУСК БОТА ---
if __name__ == "__main__":
    TOKEN = "8462971057:AAFjZNsucikp9cTCr4-rFsGDclOP-EZJXkM"

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_SERVICE: [CallbackQueryHandler(service_chosen)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_PROFESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_profession)],
            ASK_WISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wish)],
            ASK_PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("🚀 Бот запущен! Открой Telegram и напиши ему /start")
    app.run_polling()

