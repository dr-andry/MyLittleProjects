from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from text_base import TextBase  

# Состояния для ConversationHandler
ASK_QUESTION, ASK_ANSWER = range(2)
ADMINS = [
    0000000 # Я
    ]

text_base = TextBase()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name

    await update.message.reply_text(
        f"👋 Привет, {user}! Я интеллектуальный бот для ответов на вопросы по экологии.\n"
        "Задайте мне вопрос, и я постараюсь найти ответ!\n\n"
        "Для справки используйте /help"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 Список доступных команд:\n"
        "/start - Начать диалог\n"
        "/help - Показать справку\n"
        "/add_qna - Добавить новый вопрос-ответ (только для администраторов)"
    )
    
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    answer = text_base.find_answer(question)

    user = update.message.from_user
    print(f"User {user.id} ({user.first_name}) sent message: {update.message.text}")

    if answer:
        response = f"✅ Ответ:\n{answer}"
    else:
        response = "❌ Извините, я не нашел ответа на этот вопрос."
    
    await update.message.reply_text(response)

# Обработчики для добавления QnA
async def add_qna(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("⛔ У вас недостаточно прав для этой команды.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Добавление нового вопроса-ответа:\n"
        "Пожалуйста, введите вопрос."
        "\n\nДля отмены используйте /cancel"
    )
    return ASK_QUESTION

async def receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['question'] = update.message.text
    await update.message.reply_text("Теперь введите ответ:")
    return ASK_ANSWER

async def receive_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['answer'] = update.message.text
    text_base.add_qna(
        [{
            "question" : context.user_data['question'],
            "answer" : context.user_data['answer']
        }]
    )
    await update.message.reply_text("✅ Вопрос и ответ успешно добавлены!")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Добавление отменено.")
    context.user_data.clear()
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token("").build()

    # Настройка обработчиков
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add_qna', add_qna)],
        states={
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question)],
            ASK_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_answer)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()