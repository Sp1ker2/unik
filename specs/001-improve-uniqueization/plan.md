# Implementation Plan: Улучшение методов уникализации изображений

**Branch**: `001-improve-uniqueization` | **Date**: 2025-11-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-improve-uniqueization/spec.md`

## Summary

Улучшение Telegram-бота уникализации изображений: добавление нескольких методов уникализации (метаданные, микро-изменения, LSB-модификация, комбинированный), интерактивный выбор метода через inline-кнопки, **генерация 1-100 уникальных копий с выдачей в ZIP-архиве**, пакетная обработка до 10 изображений, полная замена метаданных EXIF/IPTC/XMP. Критерий качества: SSIM >= 0.99.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- python-telegram-bot >= 21.0 (async Telegram Bot API)
- Pillow >= 10.0.0 (обработка изображений)
- piexif >= 1.1.3 (EXIF метаданные)
- numpy (LSB-модификация, SSIM расчёт)
- scikit-image (SSIM метрика для тестирования)

**Storage**: N/A (stateless bot, временное хранение в памяти во время обработки)
**Testing**: pytest + pytest-asyncio
**Target Platform**: Linux server (Docker-ready)
**Project Type**: single (Telegram bot)
**Performance Goals**: < 5 сек на изображение до 10 МБ
**Constraints**:
- Telegram Bot API лимит: 20 МБ на файл
- SSIM >= 0.99 (визуальное качество)
- Размер результата <= 120% оригинала

**Scale/Scope**: Однопользовательские сессии, без персистентного состояния

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution не определена (шаблон). Применяются стандартные практики:
- [x] Код покрыт тестами
- [x] Модульная архитектура (разделение методов уникализации)
- [x] Обработка ошибок с понятными сообщениями

## Project Structure

### Documentation (this feature)

```text
specs/001-improve-uniqueization/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (bot commands/callbacks)
├── checklists/          # Quality checklists
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
bot.py                   # Существующий файл → рефакторинг в модули
requirements.txt         # Зависимости

src/
├── __init__.py
├── bot.py               # Telegram bot handlers
├── handlers/
│   ├── __init__.py
│   ├── photo.py         # Обработка фото
│   └── callbacks.py     # Inline-кнопки
├── uniqueizers/
│   ├── __init__.py
│   ├── base.py          # Базовый класс
│   ├── metadata.py      # Только метаданные
│   ├── micro.py         # Микро-изменения
│   ├── lsb.py           # LSB-модификация
│   └── combined.py      # Комбинированный
├── utils/
│   ├── __init__.py
│   ├── image.py         # Работа с изображениями
│   ├── metadata.py      # EXIF/IPTC/XMP утилиты
│   └── archive.py       # ZIP-архивирование результатов
└── config.py            # Конфигурация

tests/
├── __init__.py
├── conftest.py          # Фикстуры pytest
├── unit/
│   ├── test_metadata.py
│   ├── test_micro.py
│   ├── test_lsb.py
│   └── test_combined.py
└── integration/
    └── test_bot.py
```

**Structure Decision**: Рефакторинг из одного файла (bot.py) в модульную структуру src/ с разделением по ответственности: handlers (Telegram), uniqueizers (алгоритмы), utils (утилиты).

## Complexity Tracking

> No constitution violations - standard modular design.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
