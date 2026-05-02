# Nokol Ar Hobe Na! (Python + OpenGL)

A simple 3D game built with **Python** and **OpenGL (PyOpenGL + GLUT)**, following the **Entity-Component-System (ECS)** architectural pattern. The scene places a student at a desk in an exam room, with interactive desk items that can be inspected.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Core Layer](#core-layer)
  - [Component](#component)
  - [Entity](#entity)
- [Components](#components)
  - [Transform](#transform)
  - [StudentAnimState](#studentanimstate)
  - [StudentDeskState](#studentdeskstate)
  - [ExamSheetState](#examsheetstate)
  - [CalculatorState](#calculatorstate)
  - [SmartphoneState](#smartphonestate)
- [Entities & What They Can Do](#entities--what-they-can-do)
  - [Student Entity](#student-entity)
  - [StudentDesk Entity](#studentdesk-entity)
- [Renderers](#renderers)
  - [StudentRenderer](#studentrenderer)
  - [StudentDeskRenderer](#studentdeskrenderer)
  - [ExamSheetRenderer](#examsheetrenderer)
  - [CalculatorRenderer](#calculatorrenderer)
  - [SmartphoneRenderer](#smartphonerenderer)
- [GameManager](#gamemanager)
- [Input & Controls](#input--controls)

---

## Architecture Overview

This project uses a strict **Entity-Component-System** pattern:

| Layer | Responsibility |
|---|---|
| **Component** | Pure data. No logic. Holds state flags and values. |
| **Entity** | A blank ID container. Stores components in a dictionary. |
| **System / Renderer** | Reads component data and produces output (rendering, movement). |
| **GameManager** | Wires everything together: creates entities, runs update + render loops. |

> **Rule of thumb:** Components never call renderers. Renderers never modify components. `GameManager` owns the loop.

---

## Project Structure

```
project/
│
├── core/
│   ├── component.py          # Abstract base class for all components
│   └── entity.py             # Entity container class
│
├── components/
│   ├── transform.py          # World position & rotation
│   ├── student_anim_state.py # Student animation flags
│   ├── student_desk_state.py # Desk aggregate (holds 3 sub-states)
│   ├── exam_sheet_state.py   # Exam sheet visibility
│   ├── calculator_state.py   # Calculator visibility + inspection
│   └── smartphone_state.py   # Smartphone visibility + inspection
│
├── game/
│   ├── game_manager.py         # Main game loop controller
│   ├── student_renderer.py     # Draws the 3D student character
│   ├── student_desk_renderer.py# Draws the desk + delegates to item renderers
│   ├── exam_sheet_renderer.py  # Draws the exam paper
│   ├── calculator_renderer.py  # Draws the calculator (+ inspection HUD)
│   └── smartphone_renderer.py  # Draws the smartphone (+ inspection HUD)
```

---

## Core Layer

### Component

**File:** `core/component.py`

The abstract base class that all components must inherit from. It carries no data or logic — it simply enforces that everything attached to an entity is a `Component`.

```python
from abc import ABC

class Component(ABC):
    """Abstract base class for all components."""
    pass
```

---

### Entity

**File:** `core/entity.py`

A plain container identified by a string ID. Components are stored and retrieved by name (string key).

```python
class Entity:
    def __init__(self, entity_id):
        self.id = entity_id
        self.components = {}

    def add_component(self, name, component): ...
    def get_component(self, name): ...
```

**Usage:**

```python
from core.entity import Entity
from components.transform import Transform

player = Entity("Player_01")
player.add_component("Transform", Transform(x=0, y=0, z=40))

# Retrieve it later
t = player.get_component("Transform")
print(t.x, t.y, t.z)  # 0 0 40
```

---

## Components

Components are **pure data containers** — they hold state but contain zero rendering or game logic.

---

### Transform

**File:** `components/transform.py`

Stores the world position `(x, y, z)` and rotation `yaw` (rotation around the Z-axis, in degrees) of any entity that exists in 3D space.

| Field | Type | Default | Description |
|---|---|---|---|
| `x` | float | 0 | World X position |
| `y` | float | 0 | World Y position |
| `z` | float | 0 | World Z position (height) |
| `yaw` | float | 0 | Rotation around Z-axis (degrees) |

```python
from components.transform import Transform

# Place an entity at world position (100, 50, 0), facing default direction
t = Transform(x=100, y=50, z=0)

# Rotate it 90 degrees
t.yaw = 90.0
```

---

### StudentAnimState

**File:** `components/student_anim_state.py`

Holds independent boolean flags that drive the student's animation. Renderers read these flags every frame to decide how to draw the character.

| Flag | Type | Default | Description |
|---|---|---|---|
| `is_idle` | bool | `True` | Gentle breathing bob animation |
| `is_walking` | bool | `False` | Leg/arm swing + slight vertical bounce |
| `is_sitting` | bool | `False` | Seated posture; arms resting forward |
| `is_dancing` | bool | `False` | Head and arm sway animation |
| `is_writing` | bool | `False` | Right arm reaches forward; holds a pen |
| `is_alien` | bool | `False` | Overrides body + head color to neon green |
| `is_ghost` | bool | `False` | Enables alpha blending; pulsing transparency |

> **Note:** `is_sitting` and `is_walking` are mutually exclusive. `GameManager.toggle_state()` enforces this automatically.

```python
from components.student_anim_state import StudentAnimState

anim = StudentAnimState()

# Make the student sit and write
anim.is_sitting = True
anim.is_writing = True

# Make the student a translucent ghost
anim.is_ghost = True

# Make the student an alien (neon green override)
anim.is_alien = True
```

---

### StudentDeskState

**File:** `components/student_desk_state.py`

An aggregate component that owns three sub-state components — one for each item on the desk. You never attach `ExamSheetState`, `CalculatorState`, or `SmartphoneState` directly to the entity; you access them through this parent.

| Field | Type | Description |
|---|---|---|
| `exam_sheet` | `ExamSheetState` | State of the exam paper |
| `calculator` | `CalculatorState` | State of the calculator |
| `smartphone` | `SmartphoneState` | State of the smartphone |

```python
from components.student_desk_state import StudentDeskState

desk_state = StudentDeskState()

# Access child states directly
desk_state.calculator.is_visible = True
desk_state.smartphone.is_visible = False
desk_state.exam_sheet.is_visible = True
```

---

### ExamSheetState

**File:** `components/exam_sheet_state.py`

Controls the visibility of the white exam paper sitting on the desk.

| Field | Type | Default | Description |
|---|---|---|---|
| `is_visible` | bool | `True` | Whether the exam sheet is drawn |

```python
desk_state.exam_sheet.is_visible = False  # Hide the exam sheet
desk_state.exam_sheet.is_visible = True   # Show it again
```

---

### CalculatorState

**File:** `components/calculator_state.py`

Controls the calculator's visibility and whether it is currently being inspected (triggering the full-screen evidence HUD).

| Field | Type | Default | Description |
|---|---|---|---|
| `is_visible` | bool | `False` | Whether the calculator is drawn on the desk |
| `is_being_inspected` | bool | `False` | If `True`, renders the full-screen inspection overlay |

```python
# Show the calculator on the desk
desk_state.calculator.is_visible = True

# Trigger the inspection overlay (e.g., when player presses a key near it)
desk_state.calculator.is_being_inspected = True

# Return to desk view
desk_state.calculator.is_being_inspected = False
```

When `is_being_inspected` is `True`, the `CalculatorRenderer` renders:
- A full-screen dark overlay
- An **EVIDENCE LOG** panel on the left showing `STATUS: AUTHORIZED DEVICE`
- A scaled 3D model of the calculator on the right

---

### SmartphoneState

**File:** `components/smartphone_state.py`

Controls the smartphone's visibility and inspection mode.

| Field | Type | Default | Description |
|---|---|---|---|
| `is_visible` | bool | `True` | Whether the phone is drawn on the desk |
| `is_being_inspected` | bool | `False` | If `True`, renders the full-screen inspection overlay |

```python
# Show the phone on the desk
desk_state.smartphone.is_visible = True

# Trigger inspection (catches cheating)
desk_state.smartphone.is_being_inspected = True
```

When `is_being_inspected` is `True`, the `SmartphoneRenderer` renders:
- A full-screen dark overlay
- An **EVIDENCE LOG** panel showing `STATUS: UNAUTHORIZED DEVICE` in red, with `Active Application: ChatGPT`
- A scaled 3D model of the phone on the right

---

## Entities & What They Can Do

Entities are created and managed inside `GameManager`. Here is a full breakdown of what each entity is capable of.

---

### Student Entity

**ID:** `"Student_01"`  
**Components:** `Transform`, `AnimState` (`StudentAnimState`)

The student is the main character. Its behavior is driven entirely by the flags in `StudentAnimState`.

#### Full Capability Matrix

| Capability | How to Enable | Visual Result |
|---|---|---|
| Idle breathing | `anim.is_idle = True` (default) | Torso bobs up and down slowly |
| Walking | `anim.is_walking = True` | Legs/arms swing; slight vertical bounce |
| Sitting | `anim.is_sitting = True` | Legs fold under desk; arms rest forward |
| Dancing | `anim.is_dancing = True` | Head and arms sway side to side |
| Writing | `anim.is_writing = True` | Right arm extends forward; red pen held in hand |
| Ghost mode | `anim.is_ghost = True` | Full body becomes semi-transparent, pulsing alpha |
| Alien mode | `anim.is_alien = True` | Full body and head become neon green |
| Movement | `W/A/S/D` keys | Updates `Transform.x/y`; auto-sets `is_walking` |

#### Code Examples

```python
# Get the student's components
transform = game_manager.test_student.get_component("Transform")
anim = game_manager.test_student.get_component("AnimState")

# --- Scenario 1: Sit the student down and make them write ---
anim.is_sitting = True
anim.is_writing = True

# --- Scenario 2: Make the student a ghost ---
anim.is_ghost = True
anim.is_alien = False  # Ghost and alien are independent; only ghost takes priority visually

# --- Scenario 3: Alien student dancing ---
anim.is_alien = True
anim.is_dancing = True

# --- Scenario 4: Teleport the student to a new position ---
transform.x = 200.0
transform.y = -100.0

# --- Scenario 5: Toggle a state safely (respects mutual exclusion) ---
game_manager.toggle_state("is_sitting")   # Sitting → auto-disables walking
game_manager.toggle_state("is_walking")   # Walking → auto-disables sitting
```

---

### StudentDesk Entity

**ID:** `"StudentDesk_01"`  
**Components:** `Transform`, `StudentDeskState`

The desk is a static 3D object with a wooden tabletop and four legs. It holds three interactive items, each controlled by its own sub-state inside `StudentDeskState`.

#### Full Capability Matrix

| Item | Show/Hide | Inspection Mode | Inspection Verdict |
|---|---|---|---|
| Exam Sheet | `exam_sheet.is_visible` | N/A | N/A |
| Calculator | `calculator.is_visible` | `calculator.is_being_inspected` | ✅ Authorized Device |
| Smartphone | `smartphone.is_visible` | `smartphone.is_being_inspected` | ❌ Unauthorized Device |

#### Code Examples

```python
desk_state = game_manager.test_desk.get_component("StudentDeskState")

# --- Scenario 1: Standard exam setup (sheet + calculator visible, no phone) ---
desk_state.exam_sheet.is_visible = True
desk_state.calculator.is_visible = True
desk_state.smartphone.is_visible = False

# --- Scenario 2: Cheating setup (phone hidden on desk) ---
desk_state.smartphone.is_visible = True
desk_state.calculator.is_visible = False

# --- Scenario 3: Invigilator inspects the calculator ---
desk_state.calculator.is_visible = True
desk_state.calculator.is_being_inspected = True
# Renders full-screen HUD: "STATUS: AUTHORIZED DEVICE" — press SPACE to dismiss

# --- Scenario 4: Invigilator catches the phone ---
desk_state.smartphone.is_visible = True
desk_state.smartphone.is_being_inspected = True
# Renders full-screen HUD: "STATUS: UNAUTHORIZED DEVICE" / "Active Application: ChatGPT"

# --- Scenario 5: Dismiss any inspection ---
desk_state.calculator.is_being_inspected = False
desk_state.smartphone.is_being_inspected = False

# --- Scenario 6: Hide everything from the desk ---
desk_state.exam_sheet.is_visible = False
desk_state.calculator.is_visible = False
desk_state.smartphone.is_visible = False
```

---

## Renderers

Renderers are **stateless systems** — they receive component data as arguments and produce OpenGL draw calls. They do not store game state.

---

### StudentRenderer

**File:** `game/student_renderer.py`

Builds the full 3D student character from primitive geometry (cubes and spheres). Reads `Transform` and `StudentAnimState` every frame.

- **Torso:** Colored cube; shirt stripe drawn on front
- **Head:** Sphere with eyes (hidden in ghost mode)
- **Arms:** Two-segment limbs with per-state rotation math
- **Legs:** Two-segment limbs with walking swing and sitting fold
- **Pen:** Cylinder + cone attached to right hand when `is_writing = True`
- **Ghost:** Enables `GL_BLEND`; alpha pulses using `sin(frame_count)`
- **Alien:** Color override applied to every body part

---

### StudentDeskRenderer

**File:** `game/student_desk_renderer.py`

Draws the wooden desk geometry, then **delegates** rendering of each item to its dedicated child renderer.

```
StudentDeskRenderer.render()
    ├── draws desk top + 4 legs (OpenGL directly)
    ├── ExamSheetRenderer.render(transform, state.exam_sheet)
    ├── CalculatorRenderer.render(transform, state.calculator)
    └── SmartphoneRenderer.render(transform, state.smartphone)
```

---

### ExamSheetRenderer

**File:** `game/exam_sheet_renderer.py`

Draws a flat white rectangular prism (the exam paper) offset from the desk center. Controlled entirely by `ExamSheetState.is_visible`.

---

### CalculatorRenderer

**File:** `game/calculator_renderer.py`

Has two render modes selected by `CalculatorState`:

| Mode | Trigger | Description |
|---|---|---|
| **Desk** | `is_being_inspected = False` | Small calculator model placed on the desk, slightly rotated |
| **Inspection HUD** | `is_being_inspected = True` | Full-screen dark overlay + evidence log (green text) + scaled 3D model |

---

### SmartphoneRenderer

**File:** `game/smartphone_renderer.py`

Has two render modes selected by `SmartphoneState`:

| Mode | Trigger | Description |
|---|---|---|
| **Desk** | `is_being_inspected = False` | Phone model on the desk with ChatGPT visible on screen |
| **Inspection HUD** | `is_being_inspected = True` | Full-screen overlay + evidence log (red text, unauthorized) + scaled model |

---

## GameManager

**File:** `game/game_manager.py`

The central controller. Responsible for:

1. **Creating entities** and attaching components
2. **Running `update(dt, keys)`** — handles movement, enforces state rules
3. **Running `render()`** — draws floor/grid, routes each entity to its renderer
4. **`toggle_state(state_name)`** — safely flips a boolean on `StudentAnimState` with mutual exclusion enforcement

### Entity Creation Reference

```python
# Student
test_student = Entity("Student_01")
test_student.add_component("Transform", Transform(0, 0, 40))
test_student.add_component("AnimState", StudentAnimState())

# Desk
test_desk = Entity("StudentDesk_01")
test_desk.add_component("Transform", Transform(0, 30, 0))
test_desk.add_component("StudentDeskState", StudentDeskState())
```

### Render Routing Logic

```python
for entity in self.entities:
    transform = entity.get_component("Transform")
    anim      = entity.get_component("AnimState")
    desk      = entity.get_component("StudentDeskState")

    if transform and anim:
        student_renderer.render(transform, anim, frame_count)
    elif transform and desk:
        student_desk_renderer.render(transform, desk)
```

---

## Input & Controls

| Key | Action |
|---|---|
| `W` | Move student forward (+Y) |
| `S` | Move student backward (−Y) |
| `A` | Move student left (−X) |
| `D` | Move student right (+X) |
| `SPACE` | Dismiss inspection HUD (intended, see renderer notes) |

> Movement is normalized so diagonal movement is not faster than cardinal movement. The student's `yaw` is updated automatically to face the direction of travel using `atan2`.
