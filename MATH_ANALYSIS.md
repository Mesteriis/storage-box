# Математический анализ расчётов Storage Box

## Проверка всех формул на корректность

### Тестовая конфигурация
```python
width = 200mm
depth = 220mm
height = 80mm
material = HYPER_PLA (tolerance = 0.3mm)
wall_thickness = 2.0mm (при area < 100 см²)
RAIL_WIDTH = 5.0mm
```

---

## ❌ КРИТИЧЕСКАЯ ОШИБКА №1: Shell Front Opening

**Проблема**: Shell должен быть открыт ТОЛЬКО спереди!

**План (DESIGN.md строка 18)**:
```
Front wall removed (П-shape, open front)
```

**Текущий код**: Нет явной проверки, что front wall удаляется правильно.

**Исправление**: В `components/shell.py` нужно:
1. Создать solid box
2. Вырезать внутреннюю полость
3. **ВЫРЕЗАТЬ переднюю стенку полностью** (не только отверстие для ящика!)

```python
# ПРАВИЛЬНО:
front_opening_width = inner_width  # Между боковыми стенками
front_opening_height = inner_height - 5  # Небольшой lip сверху
front_cut_depth = wall * 2  # Пробить переднюю стенку насквозь
```

---

## ❌ КРИТИЧЕСКАЯ ОШИБКА №2: effective_inner_width

**Текущая формула** (строка 114-121):
```python
effective_inner_width = (
    width                    # 200
    - 2 * wall_thickness     # - 4
    - 2 * RAIL_WIDTH         # - 10
    - 2 * tolerances["slide"] # - 0.6
)
# = 200 - 4 - 10 - 0.6 = 185.4mm
```

**Проверка**: Это пространство МЕЖДУ рельсами, где должен ходить ящик.

**Визуализация**:
```
|<----------- width = 200mm ----------->|
|                                       |
|wall|rail|<-inner->|rail|wall|
|2mm |5mm |         |5mm |2mm |
     |<-- inner = 185.4mm -->|
```

**ПРОБЛЕМА**: Формула включает СЛИШКОМ МНОГО вычетов!

**Правильная логика**:
```
Пространство между рельсами = width - 2*wall - 2*rail_width
                            = 200 - 4 - 10 = 186mm

Ящик должен поместиться с зазором:
drawer_width = inner_space - 2*tolerance
            = 186 - 0.6 = 185.4mm
```

**ВЫВОД**: Формула `effective_inner_width` ПРАВИЛЬНАЯ! Но...

---

## ❌ КРИТИЧЕСКАЯ ОШИБКА №3: drawer_width НЕ УЧИТЫВАЕТ ГЕОМЕТРИЮ!

**Текущий код** (строка 138-148):
```python
drawer_width = effective_inner_width  # 185.4mm
```

**ПРОБЛЕМА**: Эта ширина для **тела ящика**, НО:
1. Ящик имеет V-grooves по бокам для скольжения по V-rails
2. V-groove **углубляется ВНУТРЬ** ящика
3. Значит внешняя ширина ящика ДОЛЖНА быть БОЛЬШЕ!

**Правильная геометрия** (из DESIGN.md строки 64-80):
```
Shell side (V-rail - выступает ВНУТРЬ):
  |wall|
  |    ╲
  |     ╲  ← V-профиль торчит в полость
  |      ╲

Drawer side (V-groove - вырезан):
       ╱|
      ╱ |
     ╱  |  ← Groove вырезан из тела ящика
```

**ИСПРАВЛЕНИЕ**:
```python
# Ящик должен иметь:
# 1. Базовую ширину (185.4mm)
# 2. ПЛЮС компенсация за V-grooves по бокам

# V-groove вырезается на глубину ~2mm с каждой стороны
# Значит тело ящика должно быть шире на 2*2 = 4mm

drawer_body_width = effective_inner_width + 2 * 2.0  # +4mm
# = 185.4 + 4 = 189.4mm

# После вырезания V-grooves:
# drawer_width_after_grooves = 189.4 - 4 = 185.4mm ✓
```

---

## ❌ КРИТИЧЕСКАЯ ОШИБКА №4: drawer_depth

**Текущая формула** (строка 151-153):
```python
drawer_depth = effective_inner_depth - 10.0
             = (220 - 2*2) - 10
             = 216 - 10 = 206mm
```

**Почему -10mm?** "Front clearance" - непонятно!

**Правильная логика** (из DESIGN.md):
```
1. Shell внутренняя глубина = depth - 2*wall = 216mm
2. Ящик должен НЕ упираться в заднюю стенку
3. Зазор сзади: ~5mm (для дренажа, воздуха)
4. Зазор спереди: зависит от front_panel_thickness

drawer_depth = inner_depth - back_clearance - front_panel_thickness
             = 216 - 5 - max(2, wall)
             = 216 - 5 - 2 = 209mm
```

**НО**: В текущей формуле -10mm слишком много!

**ВЫВОД**: Нужно уточнить:
- Какая толщина front panel?
- Сколько зазора нужно сзади?
- Сколько спереди для выдвижения?

---

## ❌ КРИТИЧЕСКАЯ ОШИБКА №5: drawer_height

**Текущая формула** (строка 156-158):
```python
drawer_height = effective_inner_height - tolerances["slide"]
              = (80 - floor - 2) - 0.3
```

**Разбор**:
```
effective_inner_height = height - floor_thickness - 2
                      = 80 - 1.6 - 2 = 76.4mm

drawer_height = 76.4 - 0.3 = 76.1mm
```

**ПРОБЛЕМА**: Ящик **СИДИТ НА РЕЛЬСАХ**, а не на полу!

**Правильная схема** (из DESIGN.md):
```
Shell (вид сбоку):
┌──────────────────────┐  ← Top (height = 80mm)
│                      │
│  ═════════════════   │  ← Rail на высоте ~15mm от пола
│                      │
└──────────────────────┘  ← Floor (thickness = 1.6mm)
        │
        v Ground (0mm)

Drawer sits ON rails:
Rail height (ledge_z) = floor + 15mm
Drawer bottom at: ledge_z
Drawer top clearance: ~5mm from shell top
```

**ПРАВИЛЬНЫЙ РАСЧЁТ**:
```python
rail_height = floor_thickness + 15  # Высота рельса от пола = 16.6mm
top_clearance = 5.0  # Зазор до крышки shell

drawer_height = (
    height           # 80mm
    - rail_height    # - 16.6mm (ящик начинается здесь)
    - top_clearance  # - 5mm (до крышки)
    - tolerance      # - 0.3mm (зазор скольжения)
)
# = 80 - 16.6 - 5 - 0.3 = 58.1mm
```

**ВЫВОД**: Текущая формула **НЕВЕРНА**! Не учитывает высоту рельса!

---

## ❌ КРИТИЧЕСКАЯ ОШИБКА №6: drawer_inner_depth

**Текущая формула** (строка 161-163):
```python
drawer_inner_depth = drawer_height - floor_thickness - 2.0
```

**ПРОБЛЕМА**: Перепутаны HEIGHT и DEPTH!

**drawer_inner_depth** должен быть:
```python
drawer_inner_depth = drawer_depth - 2 * drawer_wall_thickness
```

А **drawer_inner_height**:
```python
drawer_inner_height = drawer_height - drawer_floor_thickness
```

**ИСПРАВЛЕНИЕ**: Переименовать переменную или исправить формулу!

---

## ❌ КРИТИЧЕСКАЯ ОШИБКА №7: floor_thickness

**Текущая формула** (строка 109-111):
```python
floor_thickness = max(1.6, wall_thickness * 0.8)
                = max(1.6, 2.0 * 0.8)
                = max(1.6, 1.6) = 1.6mm
```

**ПРОБЛЕМА**: Floor ТОНЬШЕ стенок (1.6mm vs 2.0mm)???

**Из DESIGN.md (строка 23)**:
```
Floor thickness CAN DIFFER from walls
```

НО в плане НЕ сказано, что floor ТОНЬШЕ!

**Логично**: Floor должен быть ТОЛЩЕ или РАВЕН:
```python
floor_thickness = max(2.0, wall_thickness)  # Минимум 2мм
```

Или использовать тот же wall:
```python
floor_thickness = wall_thickness
```

---

## Исправленные формулы

### 1. Shell dimensions

```python
@property
def shell_inner_width(self) -> float:
    """Width of the internal cavity."""
    return self.config.width - 2 * self.wall_thickness

@property  
def shell_inner_depth(self) -> float:
    """Depth of the internal cavity."""
    return self.config.depth - 2 * self.wall_thickness

@property
def shell_inner_height(self) -> float:
    """Height of the internal cavity."""
    return self.config.height - self.floor_thickness
```

### 2. Rail positioning

```python
@property
def rail_height_from_floor(self) -> float:
    """Height where rails are positioned."""
    return self.floor_thickness + 15.0  # 15mm above floor

@property
def space_between_rails(self) -> float:
    """Space between left and right rails (where drawer slides)."""
    return self.shell_inner_width - 2 * self.RAIL_WIDTH
```

### 3. Drawer dimensions

```python
@property
def drawer_body_width(self) -> float:
    """Drawer body width BEFORE V-grooves are cut."""
    # Need extra width to compensate for V-grooves
    v_groove_compensation = 2.0  # mm per side
    return (
        self.space_between_rails 
        - 2 * self.tolerances["slide"]
        + 2 * v_groove_compensation
    )

@property
def drawer_width_final(self) -> float:
    """Drawer width AFTER V-grooves (what actually slides)."""
    return self.space_between_rails - 2 * self.tolerances["slide"]

@property
def drawer_depth(self) -> float:
    """Drawer depth."""
    back_clearance = 5.0  # Space at back for air/drainage
    front_panel = self.front_panel_thickness
    return (
        self.shell_inner_depth 
        - back_clearance 
        - front_panel
    )

@property
def drawer_height(self) -> float:
    """Drawer outer height."""
    top_clearance = 5.0  # Clearance to shell top
    return (
        self.config.height
        - self.rail_height_from_floor  # Start at rail height
        - top_clearance
        - self.tolerances["slide"]
    )

@property
def drawer_inner_height(self) -> float:
    """Drawer internal height for contents."""
    drawer_floor = max(1.6, self.wall_thickness * 0.8)
    return self.drawer_height - drawer_floor

@property
def drawer_inner_width(self) -> float:
    """Drawer internal width."""
    drawer_wall = self.wall_thickness * 0.75
    return self.drawer_width_final - 2 * drawer_wall

@property
def drawer_inner_depth(self) -> float:
    """Drawer internal depth."""
    drawer_wall = self.wall_thickness * 0.75
    return self.drawer_depth - 2 * drawer_wall
```

### 4. Front opening

```python
@property
def front_opening_width(self) -> float:
    """Width of front opening in shell."""
    return self.shell_inner_width  # Full width between walls

@property
def front_opening_height(self) -> float:
    """Height of front opening."""
    return self.shell_inner_height - 5.0  # Small lip at top
```

---

## Тестовый пример (width=200, depth=220, height=80, wall=2.0)

### Shell
- Внешний: 200 × 220 × 80mm
- Внутренний: 196 × 216 × 78.4mm
- Стенки: 2mm, Пол: 2mm

### Rails
- Ширина рельса: 5mm
- Высота от пола: 17mm (floor 2 + offset 15)
- Расстояние между рельсами: 186mm (196 - 2*5)

### Drawer
- Тело (до V-grooves): 189.4mm × 209mm × 57.7mm
- После V-grooves: 185.4mm (проверка: 186 - 2*0.3 ✓)
- Внутренний: 183.9mm × 206mm × 56.1mm

### Front Opening
- Ширина: 196mm (вся ширина между стенками)
- Высота: 73.4mm (внутренняя высота - 5mm lip)

---

## Выводы

Нужно исправить 7 критических ошибок в `derived_config.py`:
1. ✅ Добавить расчёт высоты рельса
2. ❌ Исправить drawer_height (учесть rail_height)
3. ❌ Добавить drawer_body_width (до V-grooves)
4. ❌ Исправить drawer_depth (уточнить зазоры)
5. ❌ Исправить drawer_inner_depth (это не высота!)
6. ❌ Исправить floor_thickness (не должен быть тоньше стенок)
7. ❌ Добавить параметры front_opening

Также нужно проверить `components/shell.py`, что front wall ДЕЙСТВИТЕЛЬНО удаляется!
