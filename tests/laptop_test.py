import math
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.laptop_state import LaptopState
from components.transform import Transform
from game.laptop_renderer import LaptopRenderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# --- Camera / Player ---
cam_x = 0.0
cam_y = -180.0
cam_z = 60.0
cam_yaw = 0.0  # degrees, rotates left/right
cam_pitch = -15.0  # degrees, looks up/down

MOVE_SPEED = 80.0
ROTATE_SPEED = 60.0  # degrees per second
INTERACT_RANGE = 90.0

keys_held = {}
last_time = time.time()

# --- Scene objects ---
desk_transform = Transform(0, 0, 0)
laptop_state = LaptopState()
renderer = LaptopRenderer()


# ---------------------------------------------------------------------------
# Desk geometry
# ---------------------------------------------------------------------------
def draw_desk():
    glPushMatrix()
    glTranslatef(desk_transform.x, desk_transform.y, desk_transform.z)

    glColor3f(0.5, 0.35, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 40)
    glScalef(70, 40, 2)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(0.3, 0.2, 0.1)
    for dx in [-32, 32]:
        for dy in [-17, 17]:
            glPushMatrix()
            glTranslatef(dx, dy, 19.5)
            glScalef(4, 4, 39)
            glutSolidCube(1.0)
            glPopMatrix()

    glPopMatrix()


def draw_floor_grid():
    glColor3f(0.12, 0.12, 0.12)
    glBegin(GL_LINES)
    for i in range(-500, 501, 50):
        glVertex3f(i, -500, 0)
        glVertex3f(i, 500, 0)
        glVertex3f(-500, i, 0)
        glVertex3f(500, i, 0)
    glEnd()

    glColor3f(0.22, 0.22, 0.22)
    glBegin(GL_QUADS)
    glVertex3f(-500, -500, 0)
    glVertex3f(500, -500, 0)
    glVertex3f(500, 500, 0)
    glVertex3f(-500, 500, 0)
    glEnd()


# ---------------------------------------------------------------------------
# Proximity helper
# ---------------------------------------------------------------------------
def dist_to_desk():
    return math.hypot(cam_x - desk_transform.x, cam_y - desk_transform.y)


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, 800 / 600, 0.5, 2000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    yaw_r = math.radians(cam_yaw)
    pitch_r = math.radians(cam_pitch)

    # Direction the camera is looking
    look_x = math.sin(yaw_r) * math.cos(pitch_r)
    look_y = math.cos(yaw_r) * math.cos(pitch_r)
    look_z = math.sin(pitch_r)

    gluLookAt(
        cam_x, cam_y, cam_z, cam_x + look_x, cam_y + look_y, cam_z + look_z, 0, 0, 1
    )


# ---------------------------------------------------------------------------
# HUD — proximity prompt
# ---------------------------------------------------------------------------
def draw_prompt(text):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 0, 600, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glColor4f(0.0, 0.0, 0.0, 0.55)
    glBegin(GL_QUADS)
    glVertex2f(240, 28)
    glVertex2f(560, 28)
    glVertex2f(560, 58)
    glVertex2f(240, 58)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(1.2)
    glPushMatrix()
    glTranslatef(252, 36, 0)
    glScalef(0.09, 0.09, 1.0)
    for char in text:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(char))
    glPopMatrix()

    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


# ---------------------------------------------------------------------------
# GLUT callbacks
# ---------------------------------------------------------------------------
def display():
    global last_time, cam_x, cam_y, cam_yaw, cam_pitch

    now = time.time()
    dt = min(now - last_time, 0.05)
    last_time = now

    # --- Update laptop timer ---
    laptop_state.update(dt)

    # --- Movement (only when not using laptop) ---
    if not laptop_state.is_being_used:
        yaw_r = math.radians(cam_yaw)
        fwd_x = math.sin(yaw_r)
        fwd_y = math.cos(yaw_r)
        right_x = math.cos(yaw_r)
        right_y = -math.sin(yaw_r)

        if keys_held.get(b"w"):
            cam_x += fwd_x * MOVE_SPEED * dt
            cam_y += fwd_y * MOVE_SPEED * dt
        if keys_held.get(b"s"):
            cam_x -= fwd_x * MOVE_SPEED * dt
            cam_y -= fwd_y * MOVE_SPEED * dt
        if keys_held.get(b"a"):
            cam_x -= right_x * MOVE_SPEED * dt
            cam_y -= right_y * MOVE_SPEED * dt
        if keys_held.get(b"d"):
            cam_x += right_x * MOVE_SPEED * dt
            cam_y += right_y * MOVE_SPEED * dt

        if keys_held.get(b"left_arrow"):
            cam_yaw -= ROTATE_SPEED * dt
        if keys_held.get(b"right_arrow"):
            cam_yaw += ROTATE_SPEED * dt
        if keys_held.get(b"up_arrow"):
            cam_pitch = min(cam_pitch + ROTATE_SPEED * dt, 60.0)
        if keys_held.get(b"down_arrow"):
            cam_pitch = max(cam_pitch - ROTATE_SPEED * dt, -60.0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    setup_camera()

    draw_floor_grid()
    draw_desk()
    renderer.render(desk_transform, laptop_state)

    # --- Proximity prompt ---
    if not laptop_state.is_being_used and dist_to_desk() < INTERACT_RANGE:
        draw_prompt("[E] Use Laptop")

    glutSwapBuffers()
    glutPostRedisplay()


def keyboard_down(key, x, y):
    keys_held[key] = True

    if key == b"e":
        if not laptop_state.is_being_used and dist_to_desk() < INTERACT_RANGE:
            laptop_state.start_work()
    elif key == b" ":
        if laptop_state.is_being_used and laptop_state.is_work_done:
            laptop_state.finish()
            print("[Game] Work complete. Player returned to classroom.")
    elif key == b"\x1b":
        sys.exit()

    glutPostRedisplay()


def keyboard_up(key, x, y):
    keys_held[key] = False


def special_down(key, x, y):
    if key == GLUT_KEY_LEFT:
        keys_held[b"left_arrow"] = True
    elif key == GLUT_KEY_RIGHT:
        keys_held[b"right_arrow"] = True
    elif key == GLUT_KEY_UP:
        keys_held[b"up_arrow"] = True
    elif key == GLUT_KEY_DOWN:
        keys_held[b"down_arrow"] = True


def special_up(key, x, y):
    if key == GLUT_KEY_LEFT:
        keys_held[b"left_arrow"] = False
    elif key == GLUT_KEY_RIGHT:
        keys_held[b"right_arrow"] = False
    elif key == GLUT_KEY_UP:
        keys_held[b"up_arrow"] = False
    elif key == GLUT_KEY_DOWN:
        keys_held[b"down_arrow"] = False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Laptop Interaction Test")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.05, 1.0)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)

    print("--- Laptop Test Controls ---")
    print("W / S          : Move forward / back")
    print("A / D          : Strafe left / right")
    print("Arrow Keys     : Look left / right / up / down")
    print("E              : Interact with laptop (when close enough)")
    print("SPACE          : Dismiss screen (only once typing finishes)")
    print("ESC            : Exit")

    glutMainLoop()


if __name__ == "__main__":
    main()
