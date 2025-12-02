"""
Photo and document message handlers.
"""

import asyncio
import io
import os
import hashlib
from typing import Optional, Dict, Any, List, Tuple

from telegram import Update, Message
from telegram.ext import ContextTypes

from src.config import (
    MAX_FILE_SIZE_BYTES,
    SUPPORTED_MIME_TYPES,
    METHOD_NAMES,
    DEFAULT_METHOD,
    DEFAULT_COPY_COUNT,
    METHOD_SELECTION_TIMEOUT,
    MAX_COPY_COUNT,
    MAX_BATCH_SIZE,
    MEDIA_GROUP_COLLECTION_TIMEOUT,
)
from src.uniqueizers import UniqueizationMethod, get_uniqueizer
from src.utils.archive import create_zip_archive
from src.utils.image import get_image_format
from src.utils.filename import generate_random_filename, normalize_to_photo
from src.handlers.callbacks import get_method_keyboard


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle photo messages (compressed by Telegram).

    Args:
        update: Telegram update
        context: Bot context
    """
    user_id = update.effective_user.id
    photo = update.message.photo[-1]  # Get highest resolution

    # Download photo
    file = await context.bot.get_file(photo.file_id)
    file_bytes = await file.download_as_bytearray()
    image_bytes = bytes(file_bytes)

    # Initialize session with random filename
    random_filename = generate_random_filename("photo.jpg", prefix="photo")
    await _init_session(context, user_id, image_bytes, random_filename, update.message)

    # Show method selection
    msg = await update.message.reply_text(
        "Выберите метод уникализации:",
        reply_markup=get_method_keyboard(),
    )

    # Store message for editing
    session = context.bot_data["sessions"][user_id]
    session["selection_message_id"] = msg.message_id
    session["chat_id"] = update.effective_chat.id

    # Set timeout for method selection
    asyncio.create_task(
        _method_selection_timeout(context, user_id, msg.chat_id, msg.message_id)
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle document messages (uncompressed images).

    Args:
        update: Telegram update
        context: Bot context
    """
    document = update.message.document
    mime_type = document.mime_type

    # Validate format
    if mime_type not in SUPPORTED_MIME_TYPES:
        await update.message.reply_text(
            "Поддерживаются только изображения JPEG и PNG."
        )
        return

    # Validate size
    if document.file_size > MAX_FILE_SIZE_BYTES:
        await update.message.reply_text(
            "Файл слишком большой. Максимальный размер: 20 МБ."
        )
        return

    user_id = update.effective_user.id

    # Download document
    file = await context.bot.get_file(document.file_id)
    file_bytes = await file.download_as_bytearray()
    image_bytes = bytes(file_bytes)

    # Validate image
    try:
        get_image_format(image_bytes)
    except Exception:
        await update.message.reply_text(
            "Не удалось обработать изображение. Файл может быть повреждён."
        )
        return

    # Initialize session with normalized random filename
    original_filename = document.file_name or "image.jpg"
    normalized_filename = normalize_to_photo(original_filename)
    random_filename = generate_random_filename(normalized_filename, prefix="photo")
    await _init_session(context, user_id, image_bytes, random_filename, update.message)

    # Show method selection
    msg = await update.message.reply_text(
        "Выберите метод уникализации:",
        reply_markup=get_method_keyboard(),
    )

    # Store message for editing
    session = context.bot_data["sessions"][user_id]
    session["selection_message_id"] = msg.message_id
    session["chat_id"] = update.effective_chat.id

    # Set timeout
    asyncio.create_task(
        _method_selection_timeout(context, user_id, msg.chat_id, msg.message_id)
    )


async def _init_session(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    image_bytes: bytes,
    filename: str,
    message: Message,
) -> None:
    """Initialize user processing session."""
    if "sessions" not in context.bot_data:
        context.bot_data["sessions"] = {}

    context.bot_data["sessions"][user_id] = {
        "image_bytes": image_bytes,
        "original_filename": filename,
        "method": None,
        "count": None,
        "state": "method_select",
        "message": message,
    }


async def _method_selection_timeout(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    chat_id: int,
    message_id: int,
) -> None:
    """Handle timeout for method selection."""
    await asyncio.sleep(METHOD_SELECTION_TIMEOUT)

    if "sessions" not in context.bot_data:
        return

    session = context.bot_data["sessions"].get(user_id, {})

    if session.get("state") == "method_select":
        session["method"] = DEFAULT_METHOD
        session["count"] = DEFAULT_COPY_COUNT
        session["state"] = "processing"
        context.bot_data["sessions"][user_id] = session

        try:
            method_name = METHOD_NAMES.get(DEFAULT_METHOD, DEFAULT_METHOD)
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"Время истекло. Применяю метод по умолчанию: {method_name}...",
            )

            await process_image_from_session(context, user_id, chat_id)
        except Exception:
            pass


async def process_image_request(
    update: Update, context: ContextTypes.DEFAULT_TYPE, session: Dict[str, Any]
) -> None:
    """
    Process image with selected method and count.

    Args:
        update: Telegram update
        context: Bot context
        session: User session data
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    query = update.callback_query
    if query:
        method_name = METHOD_NAMES.get(session["method"], session["method"])
        count = session["count"]

        if count == 1:
            await query.edit_message_text(
                f"Генерирую уникальное изображение методом {method_name}..."
            )
        else:
            await query.edit_message_text(
                f"Генерирую {count} уникальных копий методом {method_name}..."
            )

    await process_image_from_session(context, user_id, chat_id)


async def process_image_from_session(
    context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int
) -> None:
    """
    Process image using session data.

    Args:
        context: Bot context
        user_id: User ID
        chat_id: Chat ID
    """
    session = context.bot_data["sessions"].get(user_id, {})

    if not session:
        return

    image_bytes = session.get("image_bytes")
    method_str = session.get("method", DEFAULT_METHOD)
    count = session.get("count", DEFAULT_COPY_COUNT)
    original_filename = session.get("original_filename", "image.jpg")

    if not image_bytes:
        return

    # Check if preview mode is enabled
    user_settings = context.bot_data.get("user_settings", {}).get(user_id, {})
    preview_mode = user_settings.get("preview_mode", False)

    try:
        # Get uniqueizer
        method = UniqueizationMethod(method_str)
        uniqueizer = get_uniqueizer(method)

        # Generate copies with progress updates for heavy methods
        if count > 5 and method_str in ["all_combined", "all_combined_with_pixel"]:
            # Send progress message for heavy operations
            progress_msg = await context.bot.send_message(
                chat_id=chat_id,
                text=f"Обрабатываю изображение... Это может занять некоторое время."
            )
            copies = await generate_copies(image_bytes, count, uniqueizer, original_filename, method_str)
            try:
                await progress_msg.delete()
            except:
                pass
        else:
            copies = await generate_copies(image_bytes, count, uniqueizer, original_filename, method_str)
        
        # Check: ensure we got the correct number of copies
        if len(copies) != count:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Generated {len(copies)} copies but {count} were requested!")
            logger.warning(f"Method: {method_str}, User: {user_id}")
            # Don't raise error, just use what we have
            if len(copies) == 0:
                raise ValueError(f"Failed to generate any copies!")

        if preview_mode and copies:
            # Show preview first
            from src.utils.image import create_preview
            from src.handlers.callbacks import get_preview_confirm_keyboard

            preview_bytes = create_preview(copies[0][0])
            session["processed_copies"] = copies
            session["state"] = "awaiting_preview_confirm"
            context.bot_data["sessions"][user_id] = session

            count_text = "копия" if count == 1 else "копий"
            method_name = METHOD_NAMES.get(method_str, method_str)
            caption = "Предпросмотр результата ({}) {}\nМетод: {}".format(count, count_text, method_name)
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=io.BytesIO(preview_bytes),
                caption=caption,
                reply_markup=get_preview_confirm_keyboard(),
            )
        else:
            # Send result directly
            await send_result(context, chat_id, copies, method_str, original_filename)

            # Clear session
            if user_id in context.bot_data["sessions"]:
                del context.bot_data["sessions"][user_id]

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Error processing image: {}".format(e), exc_info=True)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Произошла ошибка при обработке. Попробуйте ещё раз.",
        )
        if user_id in context.bot_data["sessions"]:
            del context.bot_data["sessions"][user_id]


async def generate_copies(
    image_bytes: bytes,
    count: int,
    uniqueizer,
    original_filename: str,
    method_str: str = None,
) -> List[Tuple[bytes, str]]:
    """
    Generate multiple unique copies of an image.

    Args:
        image_bytes: Original image bytes
        count: Number of copies to generate
        uniqueizer: Uniqueizer instance
        original_filename: Original filename

    Returns:
        List of (image_bytes, filename) tuples
    """
    copies = []
    name, ext = os.path.splitext(original_filename)
    if not ext:
        ext = ".jpg"

    # Track hashes to ensure uniqueness
    seen_hashes = set()
    original_hash = hashlib.md5(image_bytes).hexdigest()
    seen_hashes.add(original_hash)

    # Check if uniqueizer supports variants (method2, method3)
    has_process_variants = hasattr(uniqueizer, 'process_variants')
    
    if has_process_variants:
        # For methods with process_variants support, generate variants directly
        try:
            variants = uniqueizer.process_variants(image_bytes, count=count)
            # Debug: check how many variants we got
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"process_variants returned {len(variants)} variants (requested {count})")
            
            if len(variants) == 0:
                # Fallback to standard processing
                pass
            else:
                for i, variant_bytes in enumerate(variants):
                    processed_hash = hashlib.md5(variant_bytes).hexdigest()
                    
                    # Ensure uniqueness
                    attempts = 0
                    while processed_hash in seen_hashes and attempts < 3:
                        # Re-process this variant
                        variant_bytes = uniqueizer.process(image_bytes)
                        processed_hash = hashlib.md5(variant_bytes).hexdigest()
                        attempts += 1
                    
                    seen_hashes.add(processed_hash)
                    
                    # Generate random filename (always random, not numbered)
                    # Ensure unique filename to avoid ZIP renaming duplicates
                    seen_filenames = {f[1] for f in copies}  # Get all existing filenames
                    filename_attempts = 0
                    while filename_attempts < 10:
                        filename = generate_random_filename(original_filename, prefix="photo")
                        if filename not in seen_filenames:
                            break
                        filename_attempts += 1
                        logger.warning(f"Filename collision: {filename}, generating new one...")
                    
                    logger.info(f"Generated filename for variant {i+1}: {filename}")
                    copies.append((variant_bytes, filename))
                    
                    # Check if we got enough variants
                    if len(copies) >= count:
                        break
            
            # If we got all needed copies, return early
            if len(copies) >= count:
                return copies[:count]
            
            # If we got some but not enough, continue with standard processing for remaining
            if len(copies) < count:
                remaining = count - len(copies)
                logger.warning(f"Only got {len(copies)} variants, generating {remaining} more with standard processing")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"process_variants failed: {e}, falling back to standard processing")
            # Fallback to standard processing
            pass

    # Standard processing for other methods (or remaining copies)
    # Calculate how many more copies we need
    remaining_copies = count - len(copies)
    if remaining_copies <= 0:
        return copies[:count]
    
    for i in range(remaining_copies):
        # Process with uniqueizer
        processed = uniqueizer.process(image_bytes)

        # Verify unique hash
        processed_hash = hashlib.md5(processed).hexdigest()

        # If hash collision, re-process (rare but possible)
        attempts = 0
        while processed_hash in seen_hashes and attempts < 5:
            processed = uniqueizer.process(image_bytes)
            processed_hash = hashlib.md5(processed).hexdigest()
            attempts += 1

        seen_hashes.add(processed_hash)

        # Generate random filename (always random, not numbered)
        # Ensure unique filename to avoid ZIP renaming duplicates
        import logging
        logger = logging.getLogger(__name__)
        seen_filenames = {f[1] for f in copies}  # Get all existing filenames
        attempts = 0
        while attempts < 10:
            filename = generate_random_filename(original_filename, prefix="photo")
            if filename not in seen_filenames:
                break
            attempts += 1
            logger.warning(f"Filename collision: {filename}, generating new one...")
        
        logger.info(f"Generated filename for copy {len(copies) + 1}/{count}: {filename}")
        seen_filenames.add(filename)
        copies.append((processed, filename))

    return copies


async def send_result(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    copies: List[Tuple[bytes, str]],
    method: str,
    original_filename: str,
) -> None:
    """
    Send processing result to user.

    Args:
        context: Bot context
        chat_id: Chat ID
        copies: List of (image_bytes, filename) tuples
        method: Method used
        original_filename: Original filename
    """
    method_name = METHOD_NAMES.get(method, method)

    if len(copies) == 1:
        # Send single file
        image_bytes, filename = copies[0]
        await context.bot.send_document(
            chat_id=chat_id,
            document=io.BytesIO(image_bytes),
            filename=filename,
            caption=f"Уникализированное изображение\nМетод: {method_name}",
        )
    else:
        # Send as ZIP archive
        archive = create_zip_archive(copies)
        name, _ = os.path.splitext(original_filename)
        archive_name = f"{name}_unique_{len(copies)}.zip"
        await context.bot.send_document(
            chat_id=chat_id,
            document=archive,
            filename=archive_name,
            caption=f"Архив с {len(copies)} уникальными копиями\nМетод: {method_name}",
        )


async def send_full_result(
    update: Update, context: ContextTypes.DEFAULT_TYPE, session: Dict[str, Any]
) -> None:
    """
    Send full result after preview confirmation.

    Args:
        update: Telegram update
        context: Bot context
        session: User session data
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if "processed_copies" in session:
        await send_result(
            context,
            chat_id,
            session["processed_copies"],
            session.get("method", DEFAULT_METHOD),
            session.get("original_filename", "image.jpg"),
        )

    # Clear session
    if user_id in context.bot_data["sessions"]:
        del context.bot_data["sessions"][user_id]


# ============================================================================
# Album / Batch Processing (US4)
# ============================================================================

async def handle_media_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle media group (album) messages.

    Collects images from the same media group and processes them together.

    Args:
        update: Telegram update
        context: Bot context
    """
    user_id = update.effective_user.id
    media_group_id = update.message.media_group_id

    if not media_group_id:
        # Single image, not an album - handled by handle_photo/handle_document
        return

    # Initialize media group collection
    if "media_groups" not in context.bot_data:
        context.bot_data["media_groups"] = {}

    group_key = f"{user_id}_{media_group_id}"

    if group_key not in context.bot_data["media_groups"]:
        context.bot_data["media_groups"][group_key] = {
            "images": [],
            "chat_id": update.effective_chat.id,
            "user_id": user_id,
            "collection_task": None,
        }

        # Start collection timeout
        task = asyncio.create_task(
            _collect_media_group(context, group_key, update.effective_chat.id)
        )
        context.bot_data["media_groups"][group_key]["collection_task"] = task

    # Add this image to the group
    group = context.bot_data["media_groups"][group_key]

    # Download the image
    try:
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            file_bytes = await file.download_as_bytearray()
            filename = generate_random_filename(f"photo_{len(group['images']) + 1}.jpg", prefix="photo")
        elif update.message.document:
            doc = update.message.document
            if doc.mime_type not in SUPPORTED_MIME_TYPES:
                return
            file = await context.bot.get_file(doc.file_id)
            file_bytes = await file.download_as_bytearray()
            base_filename = doc.file_name or f"image_{len(group['images']) + 1}.jpg"
            normalized = normalize_to_photo(base_filename)
            filename = generate_random_filename(normalized, prefix="photo")
        else:
            return

        group["images"].append({
            "bytes": bytes(file_bytes),
            "filename": filename,
        })

    except Exception as e:
        # Log error but continue collecting other images
        pass


async def _collect_media_group(
    context: ContextTypes.DEFAULT_TYPE,
    group_key: str,
    chat_id: int,
) -> None:
    """
    Wait for media group collection and then process.

    Args:
        context: Bot context
        group_key: Key for the media group
        chat_id: Chat ID
    """
    # Wait for more images to arrive
    await asyncio.sleep(MEDIA_GROUP_COLLECTION_TIMEOUT)

    if "media_groups" not in context.bot_data:
        return

    group = context.bot_data["media_groups"].pop(group_key, None)
    if not group or not group["images"]:
        return

    images = group["images"]
    user_id = group["user_id"]

    # Validate batch size
    if len(images) > MAX_BATCH_SIZE:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Максимум {MAX_BATCH_SIZE} изображений за раз. Отправлено: {len(images)}"
        )
        return

    # Initialize batch session
    if "sessions" not in context.bot_data:
        context.bot_data["sessions"] = {}

    context.bot_data["sessions"][user_id] = {
        "batch_images": images,
        "method": None,
        "state": "batch_method_select",
        "chat_id": chat_id,
    }

    # Show method selection for batch
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"Получено {len(images)} изображений.\nВыберите метод уникализации:",
        reply_markup=get_method_keyboard(),
    )

    session = context.bot_data["sessions"][user_id]
    session["selection_message_id"] = msg.message_id

    # Set timeout
    asyncio.create_task(
        _batch_method_selection_timeout(context, user_id, chat_id, msg.message_id, images)
    )


async def _batch_method_selection_timeout(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    chat_id: int,
    message_id: int,
    images: List[Dict[str, Any]],
) -> None:
    """Handle timeout for batch method selection."""
    await asyncio.sleep(METHOD_SELECTION_TIMEOUT)

    if "sessions" not in context.bot_data:
        return

    session = context.bot_data["sessions"].get(user_id, {})

    if session.get("state") == "batch_method_select":
        session["method"] = DEFAULT_METHOD
        session["state"] = "batch_processing"
        context.bot_data["sessions"][user_id] = session

        try:
            method_name = METHOD_NAMES.get(DEFAULT_METHOD, DEFAULT_METHOD)
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"Время истекло. Обрабатываю {len(images)} изображений методом {method_name}...",
            )

            await process_batch(context, user_id, chat_id, images, DEFAULT_METHOD)
        except Exception:
            pass


async def process_batch(
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int,
    chat_id: int,
    images: List[Dict[str, Any]],
    method_str: str,
) -> None:
    """
    Process a batch of images.

    Args:
        context: Bot context
        user_id: User ID
        chat_id: Chat ID
        images: List of image dicts with 'bytes' and 'filename'
        method_str: Method to use
    """
    try:
        method = UniqueizationMethod(method_str)
        uniqueizer = get_uniqueizer(method)
        method_name = METHOD_NAMES.get(method_str, method_str)

        total = len(images)
        processed = 0
        errors = []

        # Send progress message
        if total > 3:
            progress_msg = await context.bot.send_message(
                chat_id=chat_id,
                text=f"Обрабатываю изображения: 0/{total}..."
            )
        else:
            progress_msg = None

        for i, img_data in enumerate(images):
            try:
                image_bytes = img_data["bytes"]
                filename = img_data["filename"]

                # Process image
                processed_bytes = uniqueizer.process(image_bytes)

                # Generate random output filename
                output_filename = generate_random_filename(filename, prefix="photo")

                # Send result
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=io.BytesIO(processed_bytes),
                    filename=output_filename,
                    caption=f"Изображение {i + 1}/{total}\nМетод: {method_name}",
                )

                processed += 1

                # Update progress
                if progress_msg and (i + 1) % 3 == 0:
                    try:
                        await progress_msg.edit_text(
                            f"Обрабатываю изображения: {i + 1}/{total}..."
                        )
                    except Exception:
                        pass

            except Exception as e:
                errors.append(f"Изображение {i + 1}: ошибка обработки")

        # Send completion message
        if errors:
            error_text = "\n".join(errors)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Обработано {processed}/{total} изображений.\n\nОшибки:\n{error_text}"
            )
        elif progress_msg:
            try:
                await progress_msg.edit_text(f"Готово! Обработано {total} изображений.")
            except Exception:
                pass

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Произошла ошибка при обработке. Попробуйте ещё раз.",
        )
    finally:
        # Clear session
        if user_id in context.bot_data.get("sessions", {}):
            del context.bot_data["sessions"][user_id]
