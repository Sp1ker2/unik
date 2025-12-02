# Модульные Уникализаторы

## Обзор

Проект использует модульную архитектуру для уникализации изображений. Каждый модуль отвечает за изменение конкретного параметра или аспекта изображения.

## Список Модулей

### 1. BitDepthUniqueizer
**Файл:** `src/uniqueizers/bit_depth.py`

**Изменяет:** Битовую глубину PNG изображений (8 или 16 бит)

**Параметры:**
- BitDepth: 8 или 16

### 2. ColorTypeUniqueizer
**Файл:** `src/uniqueizers/color_type.py`

**Изменяет:** Тип цвета PNG изображения

**Параметры:**
- ColorType: RGB или RGBA

### 3. PNGFilterUniqueizer
**Файл:** `src/uniqueizers/png_filter.py`

**Изменяет:** Алгоритм фильтрации PNG

**Параметры:**
- Filter: None, Sub, Up, Average, Paeth, Adaptive

### 4. InterlaceUniqueizer
**Файл:** `src/uniqueizers/interlace.py`

**Изменяет:** Режим чересстрочности PNG

**Параметры:**
- Interlace: Progressive / Noninterlaced

### 5. CompressionUniqueizer
**Файл:** `src/uniqueizers/compression.py`

**Изменяет:** Метод сжатия

**Параметры:**
- Compression: Deflate/Inflate (PNG стандарт)

### 6. WhiteBalanceUniqueizer
**Файл:** `src/uniqueizers/white_balance.py`

**Изменяет:** Баланс белого в EXIF метаданных

**Параметры:**
- WhiteBalance: 0 (Auto) или 1 (Manual)

### 7. ApertureUniqueizer
**Файл:** `src/uniqueizers/aperture.py`

**Изменяет:** Значение диафрагмы в EXIF

**Параметры:**
- Aperture: случайное значение f/1.4 - f/22

### 8. ResolutionUniqueizer
**Файл:** `src/uniqueizers/resolution.py`

**Изменяет:** DPI/разрешение изображения в метаданных

**Параметры:**
- Resolution: 72, 96, 150, 200, 300 DPI

### 9. CreatorToolUniqueizer ✨ NEW
**Файл:** `src/uniqueizers/creator_tool.py`

**Изменяет:** Поле CreatorTool / Software в метаданных

**Параметры:**
- CreatorTool: случайное значение из списка популярных редакторов:
  - Adobe Photoshop CC 2023/2024
  - Adobe Lightroom Classic 12.0/13.0
  - ON1 Photo RAW 2023/2024
  - Capture One 23
  - DxO PhotoLab 7
  - Luminar AI/Neo
  - Affinity Photo 2
  - GIMP 2.10.36
  - И другие...

### 10. RatingUniqueizer ✨ NEW
**Файл:** `src/uniqueizers/rating.py`

**Изменяет:** Рейтинг изображения в метаданных

**Параметры:**
- Rating: случайное значение от 0 до 5 звёзд

### 11. ColorSpaceUniqueizer ✨ NEW
**Файл:** `src/uniqueizers/color_space.py`

**Изменяет:** Цветовое пространство в метаданных

**Параметры:**
- ColorSpace: случайное значение из:
  - sRGB
  - Display P3
  - Adobe RGB (1998)
  - ProPhoto RGB
  - Rec. 2020
  - Rec. 709
  - DCI-P3
  - NTSC (1953)
  - PAL/SECAM

### 12. ExposureTimeUniqueizer ✨ NEW
**Файл:** `src/uniqueizers/exposure_time.py`

**Изменяет:** Выдержку (ExposureTime) в EXIF метаданных

**Параметры:**
- ExposureTime: случайное значение из:
  - 1/8000, 1/4000, 1/2000, 1/1000, 1/500
  - 1/250, 1/125, 1/60, 1/30, 1/15
  - 1/8, 1/4, 1/2, 1 sec
  - 2, 4, 8, 15, 30 sec

## Как Работает AllCombinedUniqueizer

`AllCombinedUniqueizer` применяет все методы последовательно:

1. **CombinedUniqueizer** (metadata + micro + lsb)
2. **ICC Profile** - смена цветового профиля
3. **Method1** - простые улучшения
4. **Method2** - продвинутая обработка (1 вариант)
5. **Method3** - финальная комбинация (1 вариант)
6. **Модульные методы** - случайные 4-7 из 11 модулей

### Модульные Методы в AllCombined

При каждом вызове `AllCombinedUniqueizer.process()`:
- Выбираются **случайные 4-8 методов** из 12 доступных
- Методы применяются в случайном порядке
- Это обеспечивает дополнительную уникальность каждой копии

## AllCombinedWithPixelUniqueizer

Добавляет к `AllCombinedUniqueizer`:
- **Pixel Pattern overlay** - наложение текстового паттерна с прозрачностью

## Создание Собственного Модуля

1. Создайте файл в `src/uniqueizers/your_module.py`
2. Наследуйтесь от `BaseUniqueizer`
3. Реализуйте метод `process(self, image_bytes: bytes) -> bytes`
4. Добавьте импорт в `all_combined.py`
5. Добавьте инстанс в `__init__` метод `AllCombinedUniqueizer`
6. Добавьте в список `modular_methods`

### Пример:

```python
from .base import BaseUniqueizer
from src.utils.image import load_image, save_image

class MyUniqueizer(BaseUniqueizer):
    def process(self, image_bytes: bytes) -> bytes:
        img, original_format = load_image(image_bytes)
        
        # Ваша логика здесь
        
        return save_image(img, original_format)
```

## Тестирование

Каждый модуль можно протестировать отдельно:

```python
from src.uniqueizers.creator_tool import CreatorToolUniqueizer

uniqueizer = CreatorToolUniqueizer()
with open('input.jpg', 'rb') as f:
    image_bytes = f.read()

result = uniqueizer.process(image_bytes)

with open('output.jpg', 'wb') as f:
    f.write(result)
```

## Параметры, Которые Изменяются

### Для PNG:
- BitDepth: 8/16
- ColorType: RGB/RGBA
- Filter: Adaptive/None/Sub/Up/Average/Paeth
- Interlace: Progressive/Noninterlaced
- Compression: Deflate/Inflate
- CreatorTool: случайный редактор
- Rating: 0-5
- ColorSpace: Display P3/sRGB/Adobe RGB/и т.д.

### Для JPEG:
- WhiteBalance: 0/1
- Aperture: f/1.4 - f/22
- Resolution: 72-300 DPI
- CreatorTool: случайный редактор
- Rating: 0-5
- ColorSpace: sRGB/Adobe RGB/и т.д.
- ExposureTime: 1/8000 - 30 sec

## Производительность

- **Легкие методы** (<0.1s): Metadata, Rating, CreatorTool
- **Средние методы** (0.1-0.5s): BitDepth, ColorType, WhiteBalance
- **Тяжелые методы** (>0.5s): AllCombined, AllCombinedWithPixel

## Безопасность

Все модули:
- Сохраняют визуальное качество (SSIM >= 0.99)
- Не увеличивают размер файла более чем на 20%
- Обрабатывают ошибки gracefully
- Логируют предупреждения при проблемах

---

**Версия:** 2.0  
**Дата обновления:** 2025-12-02

