import math
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.chair_state import ChairState
from components.transform import Transform
from game.chair_renderer import ChairRenderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# --- Global state ---
desk_transform = Transform(0, 0, 0)

# The chair is placed slightly in front of the desk (Y = 25)
# and rotated 180 degrees so it faces the desk.
chair_transform = Transform(0, 25, 0)
chair_transform.yaw = 180

chair_state = ChairState()
renderer = ChairRenderer()

# Default Third Person / Standing Camera
cam_x = 0.0
cam_y = -100.0
cam_z = 60.0
cam_yaw = 0.0
cam_pitch = -15.0

# Store previous cam position to restore when standing up
prev_cam_x = cam_x
prev_cam_y = cam_y
prev_cam_z = cam_z
prev_cam_pitch = cam_pitch

# First Person Sitting view parameters
SIT_HEIGHT = 55.0  # Slightly lower than standing height
SIT_LOOK_PITCH = 0.0  # Look straight forward, not down

MOVE_SPEED = 80.0
ROTATE_SPEED = 60.0
INTERACT_RANGE = 70.0

keys_held = {}
last_time = time.time()


def dist_to_chair():
    return math.hypot(cam_x - chair_transform.x, cam_y - chair_transform.y)


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
    """A standard desk to give the chair context."""
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

    chair_state.update(dt)

    yr = math.radians(cam_yaw)
    fwd_x = math.sin(yr)
    fwd_y = math.cos(yr)
    rgt_x = math.cos(yr)
    rgt_y = -math.sin(yr)

    # Disable movement when sitting in the chair
    if not chair_state.is_occupied:
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
    renderer.render(chair_transform, chair_state)

    # Context-sensitive prompt based on proximity and occupation status
    if dist_to_chair() < INTERACT_RANGE or chair_state.is_occupied:
        action = "Stand Up" if chair_state.is_occupied else "Sit Down"
        draw_prompt(f"[E] {action}")

    glutSwapBuffers()
    glutPostRedisplay()


def keyboard_down(key, x, y):
    global cam_x, cam_y, cam_z, cam_pitch, prev_cam_x, prev_cam_y, prev_cam_z, prev_cam_pitch
    keys_held[key] = True

    if key == b"e":
        # Check proximity to sit down, or allow standing up regardless of proximity
        if dist_to_chair() < INTERACT_RANGE or chair_state.is_occupied:
            if not chair_state.is_occupied:
                # Transition to First Person Sitting
                prev_cam_x = cam_x
                prev_cam_y = cam_y
                prev_cam_z = cam_z
                prev_cam_pitch = cam_pitch

                # Lock to chair position with eye height, looking straight ahead
                cam_x = chair_transform.x
                cam_y = chair_transform.y
                cam_z = SIT_HEIGHT
                cam_pitch = SIT_LOOK_PITCH

                chair_state.is_occupied = True
                print("[Game] Player transitioned to first-person sitting.")
            else:
                # Transition back to Third Person / standing
                cam_x = prev_cam_x
                cam_y = prev_cam_y
                cam_z = prev_cam_z
                cam_pitch = prev_cam_pitch

                chair_state.is_occupied = False
                print("[Game] Player stood up and restored third-person camera.")

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
    glutCreateWindow(b"Chair Interaction Test")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.05, 0.05, 0.05, 1.0)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)

    print("--- Chair Test Controls ---")
    print("W/A/S/D    : Move Camera (disabled when sitting)")
    print("Arrow Keys : Look")
    print("E          : Sit down (First Person) / Stand up")
    print("ESC        : Exit")

    glutMainLoop()


if __name__ == "__main__":
    main()
