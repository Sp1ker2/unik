# Data Model: Уникализация изображений

**Feature**: 001-improve-uniqueization
**Date**: 2025-11-28

## Entities

### UniqueizationMethod (Enum)

Метод уникализации изображения.

| Value | Description | Callback Data |
|-------|-------------|---------------|
| METADATA | Только замена метаданных EXIF/IPTC/XMP | `method:metadata` |
| MICRO | Микро-изменения (сдвиг, яркость, цвет) | `method:micro` |
| LSB | LSB-модификация младших битов | `method:lsb` |
| COMBINED | Все методы вместе (по умолчанию) | `method:combined` |

### ImageFormat (Enum)

Поддерживаемые форматы изображений.

| Value | MIME Type | Extension |
|-------|-----------|-----------|
| JPEG | image/jpeg | .jpg, .jpeg |
| PNG | image/png | .png |

### CopyCountOption (Enum)

Предустановленные варианты количества копий.

| Value | Count | Callback Data |
|-------|-------|---------------|
| ONE | 1 | `count:1` |
| FIVE | 5 | `count:5` |
| TEN | 10 | `count:10` |
| TWENTY | 20 | `count:20` |
| CUSTOM | — | `count:custom` |

### ProcessingSession

Временный контекст обработки изображения (in-memory, не персистируется).

| Field | Type | Description |
|-------|------|-------------|
| user_id | int | Telegram user ID |
| message_id | int | ID сообщения с изображением |
| image_bytes | bytes | Оригинальное изображение |
| original_filename | str | Имя файла от пользователя |
| format | ImageFormat | Формат изображения |
| selected_method | UniqueizationMethod | Выбранный метод (default: COMBINED) |
| copy_count | int | Количество уникальных копий (default: 1, max: 100) |
| created_at | datetime | Время создания сессии |

**Lifecycle**:
1. Created → когда пользователь отправляет изображение
2. Method selected → когда пользователь выбирает метод
3. Count selected → когда пользователь выбирает количество копий
4. Processing → во время уникализации
5. Completed → изображение(я) отправлено
6. Expired → таймаут 30 сек без выбора

### BatchSession

Контекст пакетной обработки (для альбомов).

| Field | Type | Description |
|-------|------|-------------|
| user_id | int | Telegram user ID |
| media_group_id | str | ID группы медиа Telegram |
| images | list[ProcessingSession] | Список сессий для каждого изображения |
| selected_method | UniqueizationMethod | Метод для всех изображений |
| created_at | datetime | Время создания |

**Constraints**:
- Максимум 10 изображений в группе
- Таймаут сбора группы: 2 секунды

### UniqueizationResult

Результат уникализации одного изображения.

| Field | Type | Description |
|-------|------|-------------|
| image_bytes | bytes | Уникализированное изображение |
| filename | str | Имя файла с суффиксом `_unique` |
| format | ImageFormat | Формат изображения |
| original_hash | str | SHA-256 оригинала |
| result_hash | str | SHA-256 результата |
| ssim | float | SSIM метрика (>= 0.99) |
| size_ratio | float | Отношение размеров (result/original) |

### MultiCopyResult

Результат генерации нескольких копий (возвращается пользователю).

| Field | Type | Description |
|-------|------|-------------|
| copies | list[UniqueizationResult] | Список уникализированных копий |
| archive_bytes | bytes | None | ZIP-архив (если копий > 1) |
| archive_filename | str | None | Имя архива (если копий > 1) |
| total_count | int | Запрошенное количество копий |
| success_count | int | Успешно созданных копий |

**Output behavior**:
- `copy_count == 1`: Отправляется одиночный файл (archive_bytes = None)
- `copy_count > 1`: Отправляется ZIP-архив со всеми копиями

## State Transitions

### ProcessingSession States

```
┌─────────┐    image     ┌──────────────┐  method    ┌─────────────┐  count   ┌────────────┐
│  START  │─────────────▶│METHOD_SELECT │──────────▶│COUNT_SELECT │────────▶│ PROCESSING │
└─────────┘              └──────────────┘            └─────────────┘          └────────────┘
                                │                          │                        │
                                │ 30s timeout              │ 30s timeout            │ done
                                ▼                          ▼                        ▼
                         ┌────────────┐             ┌────────────┐           ┌───────────┐
                         │  EXPIRED   │             │  EXPIRED   │           │ COMPLETED │
                         │(COMBINED,1)│             │ (count=1)  │           └───────────┘
                         └────────────┘             └────────────┘
                                │                          │
                                └──────────────────────────┘
                                              │
                                              ▼
                                       ┌───────────┐
                                       │ COMPLETED │
                                       └───────────┘
```

**State descriptions**:
- **START**: Ожидание изображения
- **METHOD_SELECT**: Показаны кнопки выбора метода
- **COUNT_SELECT**: Показаны кнопки выбора количества копий
- **PROCESSING**: Генерация уникальных копий
- **COMPLETED**: Результат отправлен
- **EXPIRED**: Таймаут, применяются значения по умолчанию

## Validation Rules

### Image Validation

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Format | JPEG or PNG only | "Поддерживаются только JPEG и PNG" |
| Size | <= 20 MB | "Файл слишком большой (максимум 20 МБ)" |
| Dimensions | > 0 x 0 | "Изображение повреждено" |
| Not animated | No GIF/APNG | "Анимированные изображения не поддерживаются" |

### Copy Count Validation

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Min | >= 1 | "Минимум 1 копия" |
| Max | <= 100 | "Максимум 100 копий за раз" |
| Type | integer | "Введите целое число" |

### Batch Validation

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Count | <= 10 images | "Максимум 10 изображений за раз" |

## Relationships

```
User (Telegram)
  │
  └── ProcessingSession (1:N, in-memory)
        │
        ├── UniqueizationMethod (1:1)
        │
        └── UniqueizationResult (1:1)

User (Telegram)
  │
  └── BatchSession (1:N, in-memory)
        │
        └── ProcessingSession (1:N)
```
