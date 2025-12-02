"""
Callback handlers for inline keyboard buttons.
"""

import asyncio
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.config import (
    METHOD_NAMES,
    DEFAULT_METHOD,
    DEFAULT_COPY_COUNT,
    METHOD_SELECTION_TIMEOUT,
    COUNT_SELECTION_TIMEOUT,
    MAX_COPY_COUNT,
)
from src.uniqueizers import UniqueizationMethod


def get_method_keyboard() -> InlineKeyboardMarkup:
    """
    Create inline keyboard for method selection.

    Returns:
        InlineKeyboardMarkup with method buttons
    """
    keyboard = [
        [InlineKeyboardButton("Только метаданные", callback_data="method:metadata")],
        [InlineKeyboardButton("Микро-изменения", callback_data="method:micro")],
        [InlineKeyboardButton("LSB-модификация", callback_data="method:lsb")],
        [InlineKeyboardButton("ICC цветовой профиль", callback_data="method:icc_profile")],
        [InlineKeyboardButton("Простая (Метод 1)", callback_data="method:method1")],
        [InlineKeyboardButton("Продвинутая (Метод 2)", callback_data="method:method2")],
        [InlineKeyboardButton("Комбинация 1+2 (Метод 3)", callback_data="method:method3")],
        [InlineKeyboardButton("ВСЕ МЕТОДЫ ВМЕСТЕ 🔥", callback_data="method:all_combined")],
        [InlineKeyboardButton("ВСЕ МЕТОДЫ ВМЕСТЕ 🔥 PIXEL", callback_data="method:all_combined_with_pixel")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_count_keyboard() -> InlineKeyboardMarkup:
    """
    Create inline keyboard for copy count selection.

    Returns:
        InlineKeyboardMarkup with count buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="count:1"),
            InlineKeyboardButton("5", callback_data="count:5"),
            InlineKeyboardButton("10", callback_data="count:10"),
            InlineKeyboardButton("20", callback_data="count:20"),
        ],
        [InlineKeyboardButton("Другое число...", callback_data="count:custom")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_preview_confirm_keyboard() -> InlineKeyboardMarkup:
    """
    Create inline keyboard for preview confirmation.

    Returns:
        InlineKeyboardMarkup with confirm/cancel buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("✓ Подтвердить", callback_data="preview:confirm"),
            InlineKeyboardButton("✗ Отмена", callback_data="preview:cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle all callback queries from inline buttons.

    Args:
        update: Telegram update
        context: Bot context
    """
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = update.effective_user.id

    # Initialize user data if needed
    if "sessions" not in context.bot_data:
        context.bot_data["sessions"] = {}

    session = context.bot_data["sessions"].get(user_id, {})

    if data.startswith("method:"):
        # Method selection
        method = data.split(":")[1]
        session["method"] = method

        # Check if this is a batch processing session
        if session.get("state") == "batch_method_select":
            session["state"] = "batch_processing"
            context.bot_data["sessions"][user_id] = session

            method_name = METHOD_NAMES.get(method, method)
            images = session.get("batch_images", [])

            await query.edit_message_text(
                f"Обрабатываю {len(images)} изображений методом {method_name}..."
            )

            # Process batch
            from src.handlers.photo import process_batch
            await process_batch(
                context,
                user_id,
                query.message.chat_id,
                images,
                method
            )
        else:
            # Single image - show count selection
            session["state"] = "count_select"
            context.bot_data["sessions"][user_id] = session

            method_name = METHOD_NAMES.get(method, method)
            await query.edit_message_text(
                f"Выбран метод: {method_name}\n\nСколько уникальных копий сгенерировать?",
                reply_markup=get_count_keyboard(),
            )

            # Set timeout for count selection
            asyncio.create_task(
                _count_selection_timeout(
                    context, user_id, query.message.chat_id, query.message.message_id
                )
            )

    elif data.startswith("count:"):
        count_str = data.split(":")[1]

        if count_str == "custom":
            session["state"] = "awaiting_custom_count"
            context.bot_data["sessions"][user_id] = session
            await query.edit_message_text(
                "Введите количество копий (1-100):"
            )
        else:
            count = int(count_str)
            session["count"] = count
            session["state"] = "processing"
            context.bot_data["sessions"][user_id] = session

            # Trigger processing
            from src.handlers.photo import process_image_request
            await process_image_request(update, context, session)

    elif data.startswith("preview:"):
        action = data.split(":")[1]

        if action == "confirm":
            session["state"] = "processing"
            context.bot_data["sessions"][user_id] = session

            from src.handlers.photo import send_full_result
            await send_full_result(update, context, session)
        else:
            # Cancel - clear session
            if user_id in context.bot_data["sessions"]:
                del context.bot_data["sessions"][user_id]
            await query.edit_message_text("Обработка отменена.")


async def handle_custom_count_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    """
    Handle custom count number input.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        True if handled, False if not a custom count input
    """
    user_id = update.effective_user.id

    if "sessions" not in context.bot_data:
        return False

    session = context.bot_data["sessions"].get(user_id, {})

    if session.get("state") != "awaiting_custom_count":
        return False

    text = update.message.text.strip()

    try:
        count = int(text)
        if count < 1 or count > MAX_COPY_COUNT:
            await update.message.reply_text(
                f"Введите число от 1 до {MAX_COPY_COUNT}."
            )
            return True

        session["count"] = count
        session["state"] = "processing"
        context.bot_data["sessions"][user_id] = session

        # Trigger processing
        from src.handlers.photo import process_image_request
        await process_image_request(update, context, session)
        return True

    except ValueError:
        await update.message.reply_text(
            f"Введите число от 1 до {MAX_COPY_COUNT}."
        )
        return True


async def _count_selection_timeout(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    chat_id: int,
    message_id: int,
) -> None:
    """Handle timeout for count selection."""
    await asyncio.sleep(COUNT_SELECTION_TIMEOUT)

    if "sessions" not in context.bot_data:
        return

    session = context.bot_data["sessions"].get(user_id, {})

    if session.get("state") == "count_select":
        session["count"] = DEFAULT_COPY_COUNT
        session["state"] = "processing"
        context.bot_data["sessions"][user_id] = session

        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"Время истекло. Генерирую {DEFAULT_COPY_COUNT} копию...",
            )

            # Create a minimal update object for processing
            from src.handlers.photo import process_image_from_session
            await process_image_from_session(context, user_id, chat_id)
        except Exception:
            pass
