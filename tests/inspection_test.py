import math
import os
import random
import sys

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.student_anim_state import StudentAnimState
from components.student_desk_state import StudentDeskState
from components.transform import Transform
from core.entity import Entity
from game.inspection_renderer import InspectionRenderer
from game.student_desk_renderer import StudentDeskRenderer
from game.student_renderer import StudentRenderer
from game.teacher_desk_renderer import TeacherDeskRenderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# --- Test Environment State (Mirrored from GameManager) ---
window_width, window_height = 1000, 800
last_time = 0
frame_count = 0.0

# Room Dimensions
room_width = 1000
room_depth = 1200
wall_height = 200

# States
STATE_PLAYING = 0
STATE_INSPECTING = 1
current_state = STATE_PLAYING

# Inspection Logic
inspection_renderer = InspectionRenderer()
selected_index = 0
is_viewing_item = False

# Entities
entities = []
player_transform = Transform(0, 255, 100)
player_transform.yaw = 180
target_student = None
target_desk_entity = None

# Input
key_states = {
    b"w": False,
    b"a": False,
    b"s": False,
    b"d": False,
    "left": False,
    "right": False,
    "up": False,
    "down": False,
}

# Renderers
student_renderer = StudentRenderer()
student_desk_renderer = StudentDeskRenderer()
teacher_desk_renderer = TeacherDeskRenderer()


def setup_classroom():
    """Identical setup to game_manager.py with item randomization."""
    global entities
    names = [
        "Abul",
        "Kuddus",
        "Kashem",
        "Mokless",
        "Boltu",
        "Poltu",
        "Hablu",
        "Gablu",
        "Jobbar",
        "Motin",
        "Solim",
        "Kolim",
        "Sokina",
        "Jorina",
        " Morjina",
        "Kulsum",
    ]
    random.shuffle(names)

    colors = [
        (0.8, 0.2, 0.2),
        (0.2, 0.8, 0.2),
        (0.2, 0.2, 0.8),
        (0.8, 0.8, 0.2),
        (0.8, 0.2, 0.8),
        (0.2, 0.8, 0.8),
        (0.5, 0.5, 0.5),
        (0.9, 0.5, 0.1),
        (0.5, 0.1, 0.9),
        (0.1, 0.9, 0.5),
        (0.4, 0.2, 0.1),
        (0.1, 0.4, 0.2),
    ]
    random.shuffle(colors)

    desk_indices = list(range(16))
    occupied_indices = random.sample(desk_indices, 12)

    start_x, start_y = -300, -430
    spacing_x, spacing_y = 200, 180

    student_count = 0
    for i in range(16):
        row = i // 4
        col = i % 4
        desk_id = f"StudentDesk_{row}_{col}"
        desk = Entity(desk_id)
        x = start_x + col * spacing_x
        y = start_y + row * spacing_y
        desk.add_component("Transform", Transform(x, y, 0))
        
        desk_state = StudentDeskState()
        # Randomize items for testing
        desk_state.calculator.is_visible = random.choice([True, False])
        if not desk_state.calculator.is_visible:
            desk_state.smartphone.is_visible = random.choice([True, False])
        else:
            desk_state.smartphone.is_visible = False
        desk_state.cheatsheet.is_visible = random.choice([True, False])
        
        desk.add_component("StudentDeskState", desk_state)

        if i in occupied_indices:
            name = names[student_count]
            id_num = f"22-4{random.randint(100, 999)}-3"
            color = colors[student_count % len(colors)]
            student_state = StudentAnimState(name, id_num, color)
            student_state.is_sitting = True
            desk.add_component("AnimState", student_state)
            student_count += 1

        entities.append(desk)

    # Add Teacher Desk
    t_desk = Entity("TeacherDesk")
    t_desk.add_component("Transform", Transform(0, 450, 0))
    from components.teacher_desk_state import TeacherDeskState

    t_desk.add_component("TeacherDeskState", TeacherDeskState())
    entities.append(t_desk)


def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, window_width / window_height, 0.5, 5000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    yaw_r = math.radians(player_transform.yaw)
    pitch_r = math.radians(player_transform.pitch)

    look_x = math.sin(yaw_r) * math.cos(pitch_r)
    look_y = math.cos(yaw_r) * math.cos(pitch_r)
    look_z = math.sin(pitch_r)

    gluLookAt(
        player_transform.x,
        player_transform.y,
        player_transform.z,
        player_transform.x + look_x,
        player_transform.y + look_y,
        player_transform.z + look_z,
        0,
        0,
        1,
    )


def _render_room():
    """Identical room rendering to game_manager.py"""
    # Floor
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-room_width / 2, room_depth / 2, 0)
    glVertex3f(room_width / 2, room_depth / 2, 0)
    glVertex3f(room_width / 2, -room_depth / 2, 0)
    glVertex3f(-room_width / 2, -room_depth / 2, 0)
    glEnd()

    # Roof
    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_QUADS)
    glVertex3f(-room_width / 2, room_depth / 2, wall_height)
    glVertex3f(room_width / 2, room_depth / 2, wall_height)
    glVertex3f(room_width / 2, -room_depth / 2, wall_height)
    glVertex3f(-room_width / 2, -room_depth / 2, wall_height)
    glEnd()

    # Walls
    glColor3f(0.55, 0.55, 0.6)
    half_w = room_width / 2
    half_d = room_depth / 2
    h = wall_height

    glBegin(GL_QUADS)
    # Front Wall
    glVertex3f(-half_w, half_d, 0)
    glVertex3f(half_w, half_d, 0)
    glVertex3f(half_w, half_d, h)
    glVertex3f(-half_w, half_d, h)
    # Back Wall
    glVertex3f(-half_w, -half_d, 0)
    glVertex3f(half_w, -half_d, 0)
    glVertex3f(half_w, -half_d, h)
    glVertex3f(-half_w, -half_d, h)
    # Left Wall
    glVertex3f(-half_w, -half_d, 0)
    glVertex3f(-half_w, half_d, 0)
    glVertex3f(-half_w, half_d, h)
    glVertex3f(-half_w, -half_d, h)
    # Right Wall
    glVertex3f(half_w, -half_d, 0)
    glVertex3f(half_w, half_d, 0)
    glVertex3f(half_w, half_d, h)
    glVertex3f(half_w, -half_d, h)
    glEnd()

    # Corner Shadows
    glColor3f(0.1, 0.1, 0.1)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    for x in [-half_w, half_w]:
        for y in [-half_d, half_d]:
            glVertex3f(x, y, 0)
            glVertex3f(x, y, h)
    glEnd()

    # Board
    glColor3f(0.1, 0.15, 0.1)
    glBegin(GL_QUADS)
    glVertex3f(-250, half_d - 1, 50)
    glVertex3f(250, half_d - 1, 50)
    glVertex3f(250, half_d - 1, 150)
    glVertex3f(-250, half_d - 1, 150)
    glEnd()

    # Grid
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_LINES)
    for i in range(int(-half_w), int(half_w) + 1, 50):
        glVertex3f(i, -half_d, 0.5)
        glVertex3f(i, half_d, 0.5)
    for i in range(int(-half_d), int(half_d) + 1, 50):
        glVertex3f(-half_w, i, 0.5)
        glVertex3f(half_w, i, 0.5)
    glEnd()


def render_scene():
    _render_room()
    for entity in entities:
        t = entity.get_component("Transform")
        s = entity.get_component("StudentDeskState")
        a = entity.get_component("AnimState")
        td = entity.get_component("TeacherDeskState")

        if t and s:
            student_desk_renderer.render(t, s)
        if t and a:
            student_renderer.render(t, a, frame_count)
        if t and td:
            teacher_desk_renderer.render(t, td)


def draw_hud():
    """Draw identical nametag/prompt to game_manager.py"""
    if target_student:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, 0, window_height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

        # Name plate
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.7)
        pw, ph = 300, 60
        px, py = window_width / 2 - pw / 2, window_height - 100
        glBegin(GL_QUADS)
        glVertex2f(px, py)
        glVertex2f(px + pw, py)
        glVertex2f(px + pw, py + ph)
        glVertex2f(px, py + ph)
        glEnd()
        glDisable(GL_BLEND)

        # Text
        glColor3f(1, 1, 1)
        name_text = f"NAME: {target_student.name}"
        id_text = f"ID: {target_student.id_number}"
        glRasterPos2f(px + 20, py + 35)
        for char in name_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        glRasterPos2f(px + 20, py + 12)
        for char in id_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

        # Prompt
        glColor4f(0, 0, 0, 0.6)
        glEnable(GL_BLEND)
        bw, bh = 250, 40
        bx, by = window_width / 2 - bw / 2, 180
        glBegin(GL_QUADS)
        glVertex2f(bx, by)
        glVertex2f(bx + bw, by)
        glVertex2f(bx + bw, by + bh)
        glVertex2f(bx, by + bh)
        glEnd()
        glDisable(GL_BLEND)
        glColor3f(1, 1, 1)
        glRasterPos2f(bx + 20, by + 15)
        for char in "[Q] Inspect  [F] Disqualify":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if current_state == STATE_PLAYING:
        setup_camera()
        render_scene()
        draw_hud()
    elif current_state == STATE_INSPECTING:
        desk_state = target_desk_entity.get_component("StudentDeskState")
        if is_viewing_item:
            inspection_renderer.render_item_inspection(
                window_width, window_height, selected_index, desk_state
            )
        else:
            setup_camera()
            render_scene()
            inspection_renderer.render_menu(
                window_width, window_height, selected_index, desk_state
            )

    glutSwapBuffers()


def update(dt):
    global frame_count, target_student, target_desk_entity
    if current_state != STATE_PLAYING:
        return

    frame_count += dt * 60.0

    # Movement
    MOVE_SPEED = 200.0
    ROTATE_SPEED = 120.0

    yaw_r = math.radians(player_transform.yaw)
    pitch_r = math.radians(player_transform.pitch)
    fwd_x = math.sin(yaw_r)
    fwd_y = math.cos(yaw_r)
    right_x = math.cos(yaw_r)
    right_y = -math.sin(yaw_r)

    if key_states[b"w"]:
        player_transform.x += fwd_x * MOVE_SPEED * dt
        player_transform.y += fwd_y * MOVE_SPEED * dt
    if key_states[b"s"]:
        player_transform.x -= fwd_x * MOVE_SPEED * dt
        player_transform.y -= fwd_y * MOVE_SPEED * dt
    if key_states[b"a"]:
        player_transform.x -= right_x * MOVE_SPEED * dt
        player_transform.y -= right_y * MOVE_SPEED * dt
    if key_states[b"d"]:
        player_transform.x += right_x * MOVE_SPEED * dt
        player_transform.y += right_y * MOVE_SPEED * dt

    if key_states["left"]:
        player_transform.yaw -= ROTATE_SPEED * dt
    if key_states["right"]:
        player_transform.yaw += ROTATE_SPEED * dt
    if key_states["up"]:
        player_transform.pitch = min(player_transform.pitch + ROTATE_SPEED * dt, 80.0)
    if key_states["down"]:
        player_transform.pitch = max(player_transform.pitch - ROTATE_SPEED * dt, -80.0)

    # Room Boundaries
    margin = 30
    half_w = room_width / 2 - margin
    half_d = room_depth / 2 - margin
    if player_transform.x < -half_w:
        player_transform.x = -half_w
    if player_transform.x > half_w:
        player_transform.x = half_w
    if player_transform.y < -half_d:
        player_transform.y = -half_d
    if player_transform.y > half_d:
        player_transform.y = half_d

    # Targeting
    target_student = None
    target_desk_entity = None
    best_dot = 0.95
    lx = math.sin(yaw_r) * math.cos(pitch_r)
    ly = math.cos(yaw_r) * math.cos(pitch_r)
    lz = math.sin(pitch_r)

    for entity in entities:
        anim = entity.get_component("AnimState")
        if anim:
            et = entity.get_component("Transform")
            dist = math.hypot(player_transform.x - et.x, player_transform.y - et.y)
            if dist < 120.0:
                ex, ey, ez = et.x, et.y - 25, 80
                vx, vy, vz = (
                    ex - player_transform.x,
                    ey - player_transform.y,
                    ez - player_transform.z,
                )
                dist_h = math.sqrt(vx * vx + vy * vy + vz * vz)
                if dist_h > 0:
                    vx /= dist_h
                    vy /= dist_h
                    vz /= dist_h
                    dot = lx * vx + ly * vy + lz * vz
                    if dot > best_dot:
                        best_dot = dot
                        target_student = anim
                        target_desk_entity = entity


def keyboardListener(key, x, y):
    global current_state, is_viewing_item, selected_index
    if key in key_states:
        key_states[key] = True
        return

    if key == b"q":
        if current_state == STATE_PLAYING and target_student:
            current_state = STATE_INSPECTING
            is_viewing_item = False
            selected_index = 0
        elif current_state == STATE_INSPECTING and not is_viewing_item:
            current_state = STATE_PLAYING

    if current_state == STATE_INSPECTING:
        if key == b"\r":  # Enter
            is_viewing_item = True
        elif key in [b"\x08", b"\x1b", b" "]:  # Back/Esc/Space
            if is_viewing_item:
                is_viewing_item = False
            else:
                current_state = STATE_PLAYING


def keyboardUpListener(key, x, y):
    if key in key_states:
        key_states[key] = False


def specialKeyListener(key, x, y):
    global selected_index
    if key == GLUT_KEY_LEFT:
        key_states["left"] = True
    elif key == GLUT_KEY_RIGHT:
        key_states["right"] = True
    elif key == GLUT_KEY_UP:
        key_states["up"] = True
        if current_state == STATE_INSPECTING and not is_viewing_item:
            menu_size = len(inspection_renderer.available_items)
            if menu_size > 0:
                selected_index = (selected_index - 1) % menu_size
    elif key == GLUT_KEY_DOWN:
        key_states["down"] = True
        if current_state == STATE_INSPECTING and not is_viewing_item:
            menu_size = len(inspection_renderer.available_items)
            if menu_size > 0:
                selected_index = (selected_index + 1) % menu_size


def specialKeyUpListener(key, x, y):
    if key == GLUT_KEY_LEFT:
        key_states["left"] = False
    elif key == GLUT_KEY_RIGHT:
        key_states["right"] = False
    elif key == GLUT_KEY_UP:
        key_states["up"] = False
    elif key == GLUT_KEY_DOWN:
        key_states["down"] = False


def idle():
    global last_time
    t = glutGet(GLUT_ELAPSED_TIME)
    dt = (t - last_time) / 1000.0
    last_time = t
    update(dt)
    glutPostRedisplay()


def main():
    global last_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Polished Inspection Prototype")
    glEnable(GL_DEPTH_TEST)
    setup_classroom()
    last_time = glutGet(GLUT_ELAPSED_TIME)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutSpecialUpFunc(specialKeyUpListener)
    glutIdleFunc(idle)

    print("--- Polished Prototype Controls ---")
    print("WASD       : Move")
    print("Arrows     : Look / Navigate Menu")
    print("Q          : Open/Close Inspection Menu")
    print("ENTER      : Select Item")
    print("SPACE/BACK : Go Back")

    glutMainLoop()


if __name__ == "__main__":
    main()
    print("Q          : Open/Close Inspection Menu")
    print("ENTER      : Select Item")
    print("SPACE/BACK : Go Back")

    glutMainLoop()

if __name__ == "__main__":
    main()
