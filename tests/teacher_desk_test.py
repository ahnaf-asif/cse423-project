import math
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.teacher_desk_state import TeacherDeskState
from components.transform import Transform
from game.teacher_desk_renderer import TeacherDeskRenderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# --- Global state ---
desk_transform = Transform(0, 0, 0)
desk_state = TeacherDeskState()
renderer = TeacherDeskRenderer()

cam_x = 0.0
cam_y = -180.0
cam_z = 70.0
cam_yaw = 0.0
cam_pitch = -20.0

MOVE_SPEED = 80.0
ROTATE_SPEED = 60.0
INTERACT_RANGE = 90.0  # Added from laptop test

keys_held = {}
last_time = time.time()


# ---------------------------------------------------------------------------
# Proximity helper
# ---------------------------------------------------------------------------
def dist_to_desk():
    return math.hypot(cam_x - desk_transform.x, cam_y - desk_transform.y)


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

    # Update the entire desk state (updates both timer and laptop)
    desk_state.update(dt)

    # --- Movement (only when not using laptop) ---
    if not getattr(desk_state.laptop, "is_being_used", False):
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

    # Renders the desk, and passes calls to the timer and laptop
    renderer.render(desk_transform, desk_state)

    # --- Proximity prompt for Laptop ---
    if (
        not getattr(desk_state.laptop, "is_being_used", False)
        and dist_to_desk() < INTERACT_RANGE
    ):
        draw_prompt("[E] Use Laptop")

    glutSwapBuffers()
    glutPostRedisplay()


def keyboard_down(key, x, y):
    keys_held[key] = True

    # -- Laptop Controls --
    if key == b"e":
        if (
            not getattr(desk_state.laptop, "is_being_used", False)
            and dist_to_desk() < INTERACT_RANGE
        ):
            if hasattr(desk_state.laptop, "start_work"):
                desk_state.laptop.start_work()
    elif key == b" ":
        if getattr(desk_state.laptop, "is_being_used", False) and getattr(
            desk_state.laptop, "is_work_done", False
        ):
            if hasattr(desk_state.laptop, "finish"):
                desk_state.laptop.finish()
                print("[Game] Work complete. Player returned to classroom.")

    # -- Timer Controls --
    elif key == b"m":
        if hasattr(desk_state.timer, "reduce_five_minutes"):
            desk_state.timer.reduce_five_minutes()
            h, m, s = desk_state.timer.get_display()
            print(f"[-5 min] Timer now: {h:02d}:{m:02d}:{s:02d}")
    elif key == b"r":
        if hasattr(desk_state.timer, "reset"):
            desk_state.timer.reset()
            print("[Reset] Timer reset to 60:00")

    # -- General Controls --
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


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Teacher Desk Isolation Test")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.05, 1.0)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)

    print("--- Teacher Desk Test Controls ---")
    print("W/A/S/D    : Move Camera")
    print("Arrow Keys : Look")
    print("E          : Use Laptop (when in range)")
    print("SPACE      : Dismiss laptop screen (when work finishes)")
    print("M          : Subtract 5 minutes from Timer")
    print("R          : Reset timer")
    print("ESC        : Exit")

    glutMainLoop()


if __name__ == "__main__":
    main()
