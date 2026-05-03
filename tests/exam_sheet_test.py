import math
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.exam_sheet_state import ExamSheetState
from components.transform import Transform
from game.exam_sheet_renderer import ExamSheetRenderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# --- Global state ---
desk_transform = Transform(0, 0, 0)

# Pass the custom test strings into the state here!
exam_state = ExamSheetState(extra_logs=["ID: xyzabc", "name: kuddus"])
renderer = ExamSheetRenderer()

cam_x = 0.0
cam_y = -120.0
cam_z = 60.0
cam_yaw = 0.0
cam_pitch = -15.0

MOVE_SPEED = 80.0
ROTATE_SPEED = 60.0
INTERACT_RANGE = 90.0

keys_held = {}
last_time = time.time()


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


def display():
    global last_time, cam_x, cam_y, cam_yaw, cam_pitch

    now = time.time()
    dt = min(now - last_time, 0.05)
    last_time = now

    exam_state.update(dt)

    # Only allow movement if not actively inspecting the object
    if not exam_state.is_being_inspected:
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
    renderer.render(desk_transform, exam_state)

    if not exam_state.is_being_inspected and dist_to_desk() < INTERACT_RANGE:
        draw_prompt("[E] Inspect Exam")

    glutSwapBuffers()
    glutPostRedisplay()


def keyboard_down(key, x, y):
    keys_held[key] = True

    if key == b"e":
        if not exam_state.is_being_inspected and dist_to_desk() < INTERACT_RANGE:
            exam_state.inspect()
            print("[Game] Inspecting Exam Sheet.")
    elif key == b" ":
        if exam_state.is_being_inspected:
            exam_state.release()
            print("[Game] Exam Sheet returned to desk.")
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
    glutCreateWindow(b"Exam Sheet Interaction Test")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.05, 1.0)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)

    print("--- Exam Sheet Test Controls ---")
    print("W/A/S/D    : Move Camera")
    print("Arrow Keys : Look")
    print("E          : Inspect exam (when close)")
    print("SPACE      : Stop inspecting")
    print("ESC        : Exit")

    glutMainLoop()


if __name__ == "__main__":
    main()
