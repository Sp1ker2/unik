"""
Telegram Bot for Image Uniqueization.

Provides multiple methods for making images unique while preserving quality.
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from src.config import BOT_TOKEN, METHOD_NAMES
from src.handlers.photo import handle_photo, handle_document, handle_media_group
from src.handlers.callbacks import handle_callback, handle_custom_count_input

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        "Привет! Отправь мне изображение, и я сделаю его уникальным.\n\n"
        "Доступные методы:\n"
        "• Только метаданные — замена EXIF/IPTC/XMP\n"
        "• Микро-изменения — незаметные изменения пикселей\n"
        "• LSB-модификация — изменение младших битов\n"
        "• ICC цветовой профиль — смена цветового пространства\n"
        "• Простая (Метод 1) — обрезка, цвет, яркость, EXIF\n"
        "• Продвинутая (Метод 2) — 6 вариантов с зеркалированием\n"
        "• Комбинация 1+2 (Метод 3) — все возможности вместе\n"
        "• ВСЕ МЕТОДЫ ВМЕСТЕ 🔥 — максимальная уникализация (1 вариант)\n"
        "• ВСЕ МЕТОДЫ ВМЕСТЕ 🔥 PIXEL — все методы + pixel pattern (alpha 10)\n\n"
        "Поддерживаются форматы: JPEG, PNG\n"
        "Максимальный размер: 20 МБ"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await start(update, context)


async def preview_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /preview command to toggle preview mode."""
    user_id = update.effective_user.id

    if "user_settings" not in context.bot_data:
        context.bot_data["user_settings"] = {}

    if user_id not in context.bot_data["user_settings"]:
        context.bot_data["user_settings"][user_id] = {"preview_mode": False}

    settings = context.bot_data["user_settings"][user_id]
    settings["preview_mode"] = not settings.get("preview_mode", False)

    status = "включен" if settings["preview_mode"] else "выключен"
    await update.message.reply_text(
        f"Режим предпросмотра {status}.\n\n"
        "Когда режим включён, вы увидите уменьшенную версию результата "
        "перед получением полноразмерного файла."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle text messages.

    Checks if this is a custom count input, otherwise ignores.
    """
    handled = await handle_custom_count_input(update, context)
    if not handled:
        # Not a custom count input - could show help or ignore
        pass


async def handle_photo_with_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo with album detection."""
    if update.message.media_group_id:
        await handle_media_group(update, context)
    else:
        await handle_photo(update, context)


async def handle_document_with_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document with album detection."""
    if update.message.media_group_id:
        await handle_media_group(update, context)
    else:
        await handle_document(update, context)


def create_application() -> Application:
    """
    Create and configure the bot application.

    Returns:
        Configured Application instance
    """
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set")

    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("preview", preview_command))

    # Photo and document handlers with media group detection
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo_with_album))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document_with_album))

    # Callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Text handler for custom count input
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    return application


def main() -> None:
    """Start the bot."""
    logger.info("Бот запускается...")

    try:
        application = create_application()
        logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        logger.error("Установите переменную окружения BOT_TOKEN")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    main()
