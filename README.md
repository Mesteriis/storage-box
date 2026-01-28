# Storage Box - Parametric 3D Printable Storage System

Параметрическая система ящиков для хранения с V-профильными направляющими для FDM 3D-печати.

## Особенности

- ✅ **V-профиль с самоцентрированием** - плавное скольжение ящика
- ✅ **Пылезащитный лабиринт** - козырёк и полка предотвращают попадание пыли
- ✅ **Адаптивные размеры** - толщина стенок рассчитывается автоматически
- ✅ **Множество стилей** - Nordic, Techno, Bauhaus, Organic, Belovodye и др.
- ✅ **Веб-интерфейс** - удобная настройка параметров и 3D-превью
- ✅ **YAML конфигурация** - сохранение и загрузка настроек
- ✅ **Готовые пресеты** - Smart Home, Workshop, Medical, MVP

## Быстрый старт

### 1. Установка зависимостей

```bash
# Python зависимости
pip install -r requirements.txt

# Blender (для генерации моделей)
# macOS:
brew install --cask blender

# Linux:
# snap install blender --classic

# Windows:
# Скачать с https://www.blender.org/download/
```

### 2. Запуск веб-интерфейса

```bash
python web_app.py
```

Откройте браузер: http://localhost:5000

### 3. Использование

1. **Выберите пресет** или настройте размеры вручную
2. **Нажмите "Calculate Dimensions"** - система рассчитает все параметры
3. **Проверьте результаты** - размеры ящика, толщину стенок, зазоры
4. **Нажмите "Generate 3D Model"** - создание STL файлов (требует Blender)

## Структура проекта

```
storage_box/
├── config/              # Конфигурация
│   ├── box_config.py    # Входные параметры
│   ├── derived_config.py # Вычисляемые размеры
│   ├── enums.py         # Перечисления (стили, материалы)
│   └── presets.py       # Готовые конфигурации
├── components/          # Компоненты моделей
│   ├── shell.py         # Корпус
│   ├── drawer.py        # Ящик
│   ├── rails.py         # V-направляющие
│   └── stops.py         # Стопоры
├── geometry/            # Геометрические примитивы
├── export/              # Экспорт STL
├── tests/               # Тесты
├── templates/           # HTML шаблоны
├── static/              # CSS, JS, изображения
├── web_app.py           # Flask приложение
└── generate.py          # Генератор моделей (Blender)
```

## Использование из командной строки

### Генерация с пресетом

```bash
blender --background --python generate.py -- --preset smarthome_desk --output ./output
```

### Генерация с параметрами

```bash
blender --background --python generate.py -- \
  --width 200 \
  --depth 220 \
  --height 80 \
  --style nordic \
  --output ./output
```

## Использование из Python

```python
from config import BoxConfig, DerivedConfig, PRESETS
from generate import generate_storage_box
from pathlib import Path

# Использовать пресет
config = PRESETS["smarthome_desk"]

# Или создать свою конфигурацию
config = BoxConfig(
    width=200,
    depth=220,
    height=80,
    design=DesignStyle.NORDIC,
    material=MaterialType.HYPER_PLA
)

# Генерация
output_dir = Path("./output")
components = generate_storage_box(config, output_dir)
```

## Тестирование геометрии

Для быстрой проверки геометрии без полной генерации:

```bash
blender --python test_geometry.py
```

Это создаст простую модель с shell, направляющими и ящиком.

## Параметры

### Основные размеры

- `width` - ширина, мм (60-400)
- `depth` - глубина, мм (80-400)  
- `height` - высота, мм (30-200)

### Материалы

- `hyper_pla` - Hyper PLA (зазор 0.3мм)
- `petg` - PETG (зазор 0.4мм)
- `abs` - ABS (зазор 0.35мм)

### Стили дизайна

- `nordic` - Скандинавский минимализм (R=5мм)
- `techno` - Техно-футуризм (фаски 45°)
- `bauhaus` - Функциональный модернизм
- `organic` - Органические формы
- `parametric` - Волновой паттерн
- `stealth` - Острые грани
- `belovodie` - Премиум стиль (рунические паттерны)

## Настройки печати

- **Слой**: 0.2мм (стандарт) или 0.12мм (премиум)
- **Заполнение**: 15-20%
- **Стенки**: 3 периметра
- **Поддержки**: не требуются (геометрия оптимизирована для FDM)

### Ориентация печати

- **Shell (корпус)**: вверх дном для лучших нависаний
- **Drawer (ящик)**: нормально (дном вниз)

## Найденные проблемы и исправления

См. `ISSUES_ANALYSIS.md` - подробный анализ несоответствий между планом и реализацией.

### Исправлено

✅ Двойной вычет зазора в `drawer_width`  
✅ Создан веб-интерфейс с 3D-превью  
⏳ В процессе: завершение функций dust labyrinth

## API Endpoints

### `GET /`
Главная страница с конфигуратором

### `GET /api/presets`
Список всех доступных пресетов

### `GET /api/preset/<name>`
Получить конфигурацию пресета

### `POST /api/calculate`
Рассчитать размеры по параметрам

Запрос:
```json
{
  "width": 200,
  "depth": 220,
  "height": 80,
  "design": "nordic",
  "material": "hyper_pla"
}
```

Ответ:
```json
{
  "dimensions": {
    "wall_thickness": 2.0,
    "drawer_width": 188.4,
    ...
  },
  "warnings": [...]
}
```

### `POST /api/generate`
Генерация 3D модели (требует Blender)

## Лицензия

MIT License

## Авторы

- Система разработана на основе детального технического задания
- Веб-интерфейс с Three.js 3D viewer
- Поддержка русского и английского языков

## Поддержка

Если возникли проблемы:

1. Проверьте установку Blender: `blender --version`
2. Проверьте Python зависимости: `pip list`
3. См. логи в консоли Flask
4. Откройте issue на GitHub
