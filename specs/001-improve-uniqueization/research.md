# Research: Методы уникализации изображений

**Feature**: 001-improve-uniqueization
**Date**: 2025-11-28

## 1. Методы уникализации изображений

### 1.1 Метаданные (EXIF/IPTC/XMP)

**Decision**: Использовать piexif для EXIF, Pillow для базовых операций

**Rationale**:
- piexif уже в проекте, хорошо документирован
- Поддерживает чтение/запись/удаление EXIF
- Для IPTC и XMP достаточно удаления через Pillow (не сохранять при save)

**Alternatives considered**:
- exifread — только чтение, не подходит
- py3exiv2 — требует libexiv2, усложняет деплой
- Pillow.ExifTags — только чтение

**Implementation notes**:
- Полное удаление: `img.save()` без параметра exif
- Новые метаданные: генерация случайных значений для Artist, DateTime, Software
- Формат даты: `YYYY:MM:DD HH:MM:SS`

### 1.2 Микро-изменения пикселей

**Decision**: Комбинация субпиксельного сдвига и микро-коррекции яркости/цвета

**Rationale**:
- Субпиксельный сдвиг (0.1-0.5 пикселя) через интерполяцию минимально влияет на качество
- Микро-коррекция яркости/цвета (±0.5-1%) незаметна глазу
- SSIM остаётся > 0.99 при таких параметрах

**Alternatives considered**:
- Обрезка краёв — теряется информация (текущий метод в боте)
- Поворот на микро-угол — артефакты интерполяции
- Масштабирование — потеря резкости

**Implementation notes**:
```python
# Субпиксельный сдвиг через affine transform
from PIL import Image
import random

def micro_shift(img):
    dx = random.uniform(0.1, 0.5)
    dy = random.uniform(0.1, 0.5)
    return img.transform(img.size, Image.AFFINE, (1, 0, dx, 0, 1, dy))

# Микро-коррекция
from PIL import ImageEnhance
def micro_enhance(img):
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.995, 1.005))
    img = ImageEnhance.Color(img).enhance(random.uniform(0.995, 1.005))
    return img
```

### 1.3 LSB-модификация (Least Significant Bit)

**Decision**: Модификация младших 1-2 битов в случайных пикселях

**Rationale**:
- Изменение LSB визуально незаметно (разница в 1-3 единицы из 255)
- Гарантированно меняет хеш файла
- Быстрая операция через numpy

**Alternatives considered**:
- Стеганография с сообщением — избыточно для задачи
- DCT-модификация — сложнее, риск артефактов для JPEG

**Implementation notes**:
```python
import numpy as np
from PIL import Image

def lsb_modify(img, intensity=0.1):
    arr = np.array(img)
    # Маска случайных пикселей (10% по умолчанию)
    mask = np.random.random(arr.shape[:2]) < intensity
    # Случайное изменение LSB
    noise = np.random.randint(-2, 3, arr.shape, dtype=np.int16)
    arr = arr.astype(np.int16)
    arr[mask] = np.clip(arr[mask] + noise[mask], 0, 255)
    return Image.fromarray(arr.astype(np.uint8))
```

### 1.4 Комбинированный метод

**Decision**: Последовательное применение всех методов

**Rationale**:
- Максимальная уникализация при сохранении качества
- Порядок: метаданные → микро-изменения → LSB
- Каждый метод независим, легко тестировать

## 2. Inline-кнопки Telegram

**Decision**: Использовать InlineKeyboardMarkup с callback_data

**Rationale**:
- Стандартный паттерн для python-telegram-bot
- Callback data содержит ID метода
- ConversationHandler для управления состоянием

**Implementation notes**:
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_method_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Только метаданные", callback_data="method:metadata")],
        [InlineKeyboardButton("Микро-изменения", callback_data="method:micro")],
        [InlineKeyboardButton("LSB-модификация", callback_data="method:lsb")],
        [InlineKeyboardButton("Комбинированный ⭐", callback_data="method:combined")],
    ])
```

## 3. Генерация нескольких уникальных копий

**Decision**: Использовать встроенный модуль zipfile для создания архивов в памяти

**Rationale**:
- zipfile — стандартная библиотека Python, не требует дополнительных зависимостей
- Поддержка создания архива в BytesIO (без записи на диск)
- Telegram принимает ZIP-файлы как документы

**Alternatives considered**:
- tarfile — менее распространён для пользователей Windows
- RAR — требует внешнюю библиотеку
- 7z — требует внешнюю библиотеку

**Implementation notes**:
```python
import zipfile
import io
from typing import List, Tuple

def create_zip_archive(images: List[Tuple[bytes, str]]) -> io.BytesIO:
    """
    Создаёт ZIP-архив из списка изображений.

    Args:
        images: Список кортежей (image_bytes, filename)

    Returns:
        BytesIO с ZIP-архивом
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for image_bytes, filename in images:
            zf.writestr(filename, image_bytes)
    buffer.seek(0)
    return buffer
```

**Copy count selection**:
- Предустановленные варианты: 1, 5, 10, 20
- Кнопка "Другое" для ввода произвольного числа (1-100)
- Ограничение 100 копий для предотвращения злоупотреблений

**Naming convention**:
- Одиночный файл: `{original_name}_unique.{ext}`
- Архив: `{original_name}_unique_x{count}.zip`
- Файлы в архиве: `{original_name}_1.{ext}`, `{original_name}_2.{ext}`, ...

**Performance considerations**:
- До 10 копий: последовательная генерация
- 10+ копий: asyncio.gather для параллельной генерации
- Прогресс-бар для > 10 копий

## 4. Пакетная обработка альбомов

**Decision**: Обработка MediaGroup через message.media_group_id

**Rationale**:
- Telegram группирует альбомы с одинаковым media_group_id
- Сбор всех изображений группы перед обработкой
- Возврат каждого файла отдельно (не альбомом)

**Implementation notes**:
- Таймаут 2 сек для сбора всех изображений группы
- asyncio.gather для параллельной обработки
- Лимит 10 изображений на группу

## 5. Сохранение качества

**Decision**: Параметры сохранения зависят от формата

**Rationale**:
- JPEG: quality=95 (баланс качества и размера)
- PNG: compress_level=6 (стандартное сжатие)
- Сохранение ICC-профиля через `icc_profile` параметр

**Quality metrics**:
- SSIM >= 0.99 — обязательно для всех методов
- Размер файла <= 120% оригинала

## 6. Зависимости

| Пакет | Версия | Назначение |
|-------|--------|------------|
| python-telegram-bot | >= 21.0 | Telegram Bot API |
| Pillow | >= 10.0.0 | Обработка изображений |
| piexif | >= 1.1.3 | EXIF метаданные |
| numpy | >= 1.24.0 | LSB-модификация |
| scikit-image | >= 0.21.0 | SSIM (только для тестов) |
| pytest | >= 7.0.0 | Тестирование |
| pytest-asyncio | >= 0.21.0 | Async тесты |
