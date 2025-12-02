# Bot Commands & Callbacks Contract

**Feature**: 001-improve-uniqueization
**Date**: 2025-11-28

## Commands

### /start

Приветственное сообщение и инструкция.

**Trigger**: User sends `/start`

**Response**:
```
Привет! Отправь мне изображение, и я сделаю его уникальным.

Доступные методы:
• Только метаданные — замена EXIF/IPTC/XMP
• Микро-изменения — незаметные изменения пикселей
• LSB-модификация — изменение младших битов
• Комбинированный — все методы вместе (по умолчанию)

Поддерживаются форматы: JPEG, PNG
Максимальный размер: 20 МБ
```

### /help

Справка по использованию.

**Trigger**: User sends `/help`

**Response**: Same as `/start`

## Message Handlers

### Photo Handler

**Trigger**: User sends photo (compressed by Telegram)

**Flow**:
1. Download photo from Telegram
2. Show method selection keyboard
3. Wait for method callback or timeout (30s)
4. Show copy count selection keyboard
5. Wait for count callback or timeout (30s)
6. Process with selected/default settings
7. Send result as document (1 copy) or ZIP archive (>1 copy)

**Response** (step 2 - method selection):
```
Выберите метод уникализации:

[Только метаданные]
[Микро-изменения]
[LSB-модификация]
[Комбинированный ⭐]
```

**Response** (step 4 - copy count selection):
```
Сколько уникальных копий сгенерировать?

[1] [5] [10] [20]
[Другое число...]
```

### Document Handler

**Trigger**: User sends document with MIME type `image/jpeg` or `image/png`

**Flow**: Same as Photo Handler

**Error Response** (wrong format):
```
Поддерживаются только изображения JPEG и PNG.
```

### MediaGroup Handler

**Trigger**: User sends album (multiple photos)

**Flow**:
1. Collect all images in group (2s timeout)
2. Validate count <= 10
3. Show method selection keyboard (once)
4. Process all images with selected method
5. Send results as separate documents

**Error Response** (too many):
```
Максимум 10 изображений за раз. Отправлено: {count}
```

## Callback Queries

### Method Selection

**Callback Data Format**: `method:{method_id}`

| Callback Data | Method | Description |
|---------------|--------|-------------|
| `method:metadata` | METADATA | Только метаданные |
| `method:micro` | MICRO | Микро-изменения |
| `method:lsb` | LSB | LSB-модификация |
| `method:combined` | COMBINED | Комбинированный |

**Response Flow**:
1. Answer callback query (remove loading indicator)
2. Edit message to show copy count selection keyboard

### Copy Count Selection

**Callback Data Format**: `count:{count}` or `count:custom`

| Callback Data | Count | Description |
|---------------|-------|-------------|
| `count:1` | 1 | Одна копия (без архива) |
| `count:5` | 5 | 5 копий в архиве |
| `count:10` | 10 | 10 копий в архиве |
| `count:20` | 20 | 20 копий в архиве |
| `count:custom` | — | Запрос произвольного числа |

**Response Flow (preset count)**:
1. Answer callback query
2. Edit message: "Генерирую {count} уникальных копий методом {method_name}..."
3. Process and generate copies
4. Send result (single file or ZIP)
5. Edit message: "Готово! ✓"

**Response Flow (custom count)**:
1. Answer callback query
2. Edit message: "Введите количество копий (1-100):"
3. Wait for text message with number
4. Validate number (1-100)
5. Continue with processing

### Custom Count Input Handler

**Trigger**: Text message with number after `count:custom` callback

**Validation**:
- Must be integer
- Range: 1-100

**Error Response** (invalid):
```
Введите число от 1 до 100.
```

## Response Templates

### Processing Status

```
Обрабатываю изображение...
```

### Processing Status (batch)

```
Обрабатываю изображения: {current}/{total}...
```

### Success (single copy)

Document caption:
```
Уникализированное изображение
Метод: {method_name}
```

### Success (multiple copies - ZIP archive)

Document caption:
```
Архив с {count} уникальными копиями
Метод: {method_name}
```

### Success (batch - multiple images)

Document caption:
```
Изображение {index}/{total}
Метод: {method_name}
```

### Error: Invalid Format

```
Поддерживаются только изображения JPEG и PNG.
```

### Error: File Too Large

```
Файл слишком большой. Максимальный размер: 20 МБ.
```

### Error: Corrupted Image

```
Не удалось обработать изображение. Файл может быть повреждён.
```

### Error: Processing Failed

```
Произошла ошибка при обработке. Попробуйте ещё раз.
```

## Inline Keyboard Layouts

### Method Selection

```
┌─────────────────────────────┐
│     Только метаданные       │
├─────────────────────────────┤
│      Микро-изменения        │
├─────────────────────────────┤
│      LSB-модификация        │
├─────────────────────────────┤
│    Комбинированный ⭐       │
└─────────────────────────────┘
```

### Copy Count Selection

```
┌───────┬───────┬───────┬───────┐
│   1   │   5   │  10   │  20   │
├───────┴───────┴───────┴───────┤
│       Другое число...         │
└───────────────────────────────┘
```

## Timeouts

| Event | Timeout | Action |
|-------|---------|--------|
| Method selection | 30 seconds | Use COMBINED (default) |
| Count selection | 30 seconds | Use 1 copy (default) |
| Custom count input | 60 seconds | Use 1 copy (default) |
| MediaGroup collection | 2 seconds | Process collected images |
| Processing (per copy) | 60 seconds | Send error message |
| Processing (100 copies) | 300 seconds | Send error message |
