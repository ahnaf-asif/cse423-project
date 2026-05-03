import math
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.timer_state import TimerState
from components.transform import Transform
from game.timer_renderer import TimerRenderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# --- Global state ---
desk_transform = Transform(0, 0, 0)
timer_state = TimerState()
renderer = TimerRenderer()

cam_x = 0.0
cam_y = -180.0
cam_z = 60.0
cam_yaw = 0.0
cam_pitch = -15.0

MOVE_SPEED = 80.0
ROTATE_SPEED = 60.0

keys_held = {}
last_time = time.time()


# ---------------------------------------------------------------------------
# Desk geometry (minimal, same as other tests)
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


def draw_floor():
    glColor3f(0.18, 0.18, 0.18)
    glBegin(GL_QUADS)
    glVertex3f(-500, -500, 0)
    glVertex3f(500, -500, 0)
    glVertex3f(500, 500, 0)
    glVertex3f(-500, 500, 0)
    glEnd()
    glColor3f(0.10, 0.10, 0.10)
    glBegin(GL_LINES)
    for i in range(-500, 501, 50):
        glVertex3f(i, -500, 0)
        glVertex3f(i, 500, 0)
        glVertex3f(-500, i, 0)
        glVertex3f(500, i, 0)
    glEnd()


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, 800 / 600, 0.5, 2000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    yr = math.radians(cam_yaw)
    pr = math.radians(cam_pitch)
    lx = math.sin(yr) * math.cos(pr)
    ly = math.cos(yr) * math.cos(pr)
    lz = math.sin(pr)
    gluLookAt(cam_x, cam_y, cam_z, cam_x + lx, cam_y + ly, cam_z + lz, 0, 0, 1)


# ---------------------------------------------------------------------------
# GLUT callbacks
# ---------------------------------------------------------------------------
def display():
    global last_time, cam_x, cam_y, cam_yaw, cam_pitch

    now = time.time()
    dt = min(now - last_time, 0.05)
    last_time = now

    timer_state.update(dt)

    yr = math.radians(cam_yaw)
    fwd_x = math.sin(yr)
    fwd_y = math.cos(yr)
    rgt_x = math.cos(yr)
    rgt_y = -math.sin(yr)

    if keys_held.get(b"w"):
        cam_x += fwd_x * MOVE_SPEED * dt
        cam_y += fwd_y * MOVE_SPEED * dt
    if keys_held.get(b"s"):
        cam_x -= fwd_x * MOVE_SPEED * dt
        cam_y -= fwd_y * MOVE_SPEED * dt
    if keys_held.get(b"a"):
        cam_x -= rgt_x * MOVE_SPEED * dt
        cam_y -= rgt_y * MOVE_SPEED * dt
    if keys_held.get(b"d"):
        cam_x += rgt_x * MOVE_SPEED * dt
        cam_y += rgt_y * MOVE_SPEED * dt
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
    draw_floor()
    draw_desk()

    # Temporarily drop the Z-height by 6.5 units before passing it to the renderer
    # so the scaled-down timer sits completely flush on the desk surface (Z=41)
    original_z = desk_transform.z
    desk_transform.z -= 6.5
    renderer.render(desk_transform, timer_state)
    desk_transform.z = original_z

    glutSwapBuffers()
    glutPostRedisplay()


def keyboard_down(key, x, y):
    keys_held[key] = True
    if key == b"m":
        timer_state.reduce_five_minutes()
        h, m, s = timer_state.get_display()
        print(f"[-5 min] Timer now: {h:02d}:{m:02d}:{s:02d}")
    elif key == b"r":
        timer_state.reset()
        print("[Reset]  Timer reset to 60:00")
    elif key == b"\x1b":
        sys.exit()
    glutPostRedisplay()


def keyboard_up(key, x, y):
    keys_held[key] = False


def special_down(key, x, y):
    mapping = {
        GLUT_KEY_LEFT: b"left_arrow",
        GLUT_KEY_RIGHT: b"right_arrow",
        GLUT_KEY_UP: b"up_arrow",
        GLUT_KEY_DOWN: b"down_arrow",
    }
    if key in mapping:
        keys_held[mapping[key]] = True


def special_up(key, x, y):
    mapping = {
        GLUT_KEY_LEFT: b"left_arrow",
        GLUT_KEY_RIGHT: b"right_arrow",
        GLUT_KEY_UP: b"up_arrow",
        GLUT_KEY_DOWN: b"down_arrow",
    }
    if key in mapping:
        keys_held[mapping[key]] = False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Timer Isolation Test")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.05, 1.0)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)

    print("--- Timer Test Controls ---")
    print("M          : Subtract 5 minutes")
    print("R          : Reset timer to 60:00")
    print("W/A/S/D    : Move")
    print("Arrow Keys : Look")
    print("ESC        : Exit")

    glutMainLoop()


if __name__ == "__main__":
    main()
