import math
import sys

from game.game_manager import GameManager
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

game = GameManager()
game.setup_classroom()
last_time = 0

# Orbital Camera
cam_radius = 800.0  # Increased for larger room
cam_angle_h = math.pi / 2 + 0.5
cam_angle_v = 0.6

# NEW: Track which movement keys are currently being held down
key_states = {b"w": False, b"a": False, b"s": False, b"d": False}


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Near plane increased to 1.0 for better Z-buffer precision, far plane to 5000
    gluPerspective(60, 1000 / 800, 1.0, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    cam_x = cam_radius * math.cos(cam_angle_v) * math.cos(cam_angle_h)
    cam_y = cam_radius * math.cos(cam_angle_v) * math.sin(cam_angle_h)
    cam_z = cam_radius * math.sin(cam_angle_v)
    # Focus slightly in front of center
    gluLookAt(cam_x, cam_y, cam_z, 0, 50, 40, 0, 0, 1)


def specialKeyListener(key, x, y):
    global cam_angle_h, cam_angle_v
    if key == GLUT_KEY_LEFT:
        cam_angle_h -= 0.1
    elif key == GLUT_KEY_RIGHT:
        cam_angle_h += 0.1
    elif key == GLUT_KEY_UP:
        cam_angle_v = min(cam_angle_v + 0.1, 1.5)
    elif key == GLUT_KEY_DOWN:
        cam_angle_v = max(cam_angle_v - 0.1, 0.1)


def keyboardListener(key, x, y):
    # If it's a movement key, mark it as True (held down)
    if key in key_states:
        key_states[key] = True
        return

    # Otherwise, it's a toggle
    if key == b"2":
        game.toggle_state("is_sitting")
    elif key == b"3":
        game.toggle_state("is_dancing")
    elif key == b"4":
        game.toggle_state("is_alien")
    elif key == b"5":
        game.toggle_state("is_ghost")
    elif key == b"6":
        game.toggle_state("is_writing")
    elif key == b"\x1b":
        sys.exit()


# NEW: When the key is released, mark it False
def keyboardUpListener(key, x, y):
    if key in key_states:
        key_states[key] = False


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, 1000, 800)
    setupCamera()
    game.render()
    glutSwapBuffers()


def idle():
    global last_time
    current_time = glutGet(GLUT_ELAPSED_TIME)
    dt = (current_time - last_time) / 1000.0
    last_time = current_time

    # NEW: Pass the key states into the game logic!
    game.update(dt, key_states)
    glutPostRedisplay()


def main():
    global last_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"Nokol Ar Hobe Na - ECS Engine")
    glEnable(GL_DEPTH_TEST)
    last_time = glutGet(GLUT_ELAPSED_TIME)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)  # NEW: Register the key release function
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(idle)

    print("--- Controls ---")
    print("WASD       : Move Student around the map")
    print("Arrow Keys : Orbit Camera")
    print("Press 2-6  : Toggle Anomalies / States")

    glutMainLoop()


if __name__ == "__main__":
    main()
