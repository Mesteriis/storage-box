# Анализ несоответствий между планом и реализацией

## Критические проблемы

### 1. Геометрия Shell и Rails

**Проблема**: В `test_geometry.py` используется упрощённая система ledges (полок), а не V-профиль из плана.

**План (DESIGN.md строки 100-117)**:
```
V-профиль с самоцентрированием:
- Угол V: 45° (оптимум для PLA/PETG)
- Самоцентрирование при выдвижении
```

**Текущий код (`test_geometry.py` строки 142-174)**:
- Создаются простые прямоугольные ledges (полки)
- Нет V-профиля
- Нет самоцентрирования

**Решение**:
1. Использовать `build_v_rail()` из `components/rails.py`
2. Интегрировать пылезащитный лабиринт (dust lip + shelf)
3. Добавить окна каждые 35мм для выхода мусора

---

### 2. Размеры Drawer

**Проблема**: Расчёт ширины ящика не соответствует системе V-направляющих.

**План (DESIGN.md строки 666-673)**:
```python
effective_inner_width = (
    width 
    - 2 * wall_thickness 
    - 2 * rail_width 
    - 2 * tolerances["slide"]
)
```

**Текущий код (`derived_config.py` строки 114-121)**:
```python
# ПРАВИЛЬНО - соответствует плану
effective_inner_width = (
    self.config.width
    - 2 * self.wall_thickness
    - 2 * self.RAIL_WIDTH
    - 2 * self.tolerances["slide"]
)
```

**НО**: В `drawer_width` (строки 138-140):
```python
drawer_width = self.effective_inner_width - 2 * self.tolerances["slide"]
```
❌ **ОШИБКА**: Зазор вычитается дважды!

**Решение**:
```python
@property
def drawer_width(self) -> float:
    """Drawer outer width - fits between rails."""
    # effective_inner_width уже учитывает rail_width и tolerances
    return self.effective_inner_width
```

---

### 3. Отсутствуют Dust Labyrinth элементы

**Проблема**: Пылезащита не реализована.

**План (DESIGN.md строки 119-135)**:
- Козырёк на корпусе: 1 мм вниз
- Полка на ящике: 0.8 мм вверх  
- Окна каждые 35 мм

**Текущий код**:
- `build_rail_with_dust_lip()` начат, но не завершён
- Нет `build_rail_windows()`
- Нет dust shelf на drawer

**Решение**:
Реализовать функции:
1. `add_dust_lip_to_rail()` - козырёк 1мм
2. `add_dust_shelf_to_drawer()` - полка 0.8мм  
3. `create_rail_windows()` - окна каждые 35мм

---

### 4. Двухступенчатые стопоры не реализованы

**Проблема**: В плане описаны два стопора, в коде их нет.

**План (DESIGN.md строки 320-348)**:
- Стопор 1: пружинная лапка PETG (1.2мм, 8мм длина, угол 15°)
- Стопор 2: жёсткий упор 3мм
- Release slot: окно 15×5мм снизу

**Текущий код**:
- `components/stops.py` существует, но функции пустые
- `build_two_stage_stop()` вызывается, но не реализована

**Решение**:
Реализовать в `stops.py`:
```python
def build_spring_tab_stop(config, name, location)
def build_hard_stop(config, name, location)  
def build_release_slot(config, name, location)
```

---

### 5. Front Panel: отсутствуют рёбра жёсткости

**Проблема**: Передняя панель без усиления.

**План (DESIGN.md строки 350-372)**:
```
Рёбра: высота 3 мм, толщина 1.2 мм
Крестообразная или рамочная схема
Внутренние радиусы на ручке R=2 мм
Филе = wall * 0.8
```

**Текущий код**:
- `components/front_panel.py` не содержит рёбер жёсткости
- Нет внутренних радиусов

**Решение**:
Добавить функцию:
```python
def add_reinforcement_ribs(panel, config, tokens)
```

---

### 6. Shadow Gap не реализован

**Проблема**: "Парящая" панель без micro-шва.

**План (DESIGN.md строки 435-453)**:
```
Микрошов по периметру фронта: 0.3–0.5 мм
Shadow gap вокруг label frame: 0.2–0.3 мм
```

**Текущий код**: Нет

**Решение**:
Добавить в `DesignTokens` и применить в front_panel:
```python
shadow_gap: float = 0.4  # mm
```

---

### 7. Anti-wobble (Spring Whisker) отсутствует

**Проблема**: Система анти-люфта не реализована.

**План (DESIGN.md строки 222-243)**:
```
Пружинный ус 0.9-1.1 мм PETG
Одна сторона — V-контакт, вторая — V + ус
```

**Текущий код**: 
- `AntiWobbleType.SPRING_WHISKER` в enum есть
- Но геометрия не создаётся

**Решение**:
Создать test kit с 6 вариантами whisker:
```python
def build_spring_whisker_variants(config)
```

---

## План исправлений

### Приоритет 1 (критично для работоспособности)
1. ✅ Исправить `drawer_width` в `derived_config.py`
2. ✅ Реализовать V-rail с dust lip
3. ✅ Добавить V-groove на drawer
4. ✅ Создать окна в направляющих

### Приоритет 2 (важные механизмы)
5. ✅ Двухступенчатые стопоры
6. ✅ Рёбра жёсткости на front panel
7. ✅ Shadow gap

### Приоритет 3 (премиум-функции)
8. Spring whisker test kit
9. Smart cartridge bay
10. Belovodye pattern generation

---

## Следующие шаги

1. Исправить критические ошибки в расчётах
2. Доработать geometry builders
3. Создать веб-интерфейс для тестирования
4. Добавить визуализацию 3D моделей
