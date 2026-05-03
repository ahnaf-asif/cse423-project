import math
import os
import sys

from game.game_manager import GameManager
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

game = GameManager()
game.setup_classroom()
last_time = 0

# Current Window Dimensions
window_width = 1000
window_height = 800

# Orbital Camera
cam_radius = 800.0
cam_angle_h = math.pi / 2 + 0.5
cam_angle_v = 0.6

# Track movement keys
key_states = {b"w": False, b"a": False, b"s": False, b"d": False}


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, window_width / window_height, 1.0, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    cam_x = cam_radius * math.cos(cam_angle_v) * math.cos(cam_angle_h)
    cam_y = cam_radius * math.cos(cam_angle_v) * math.sin(cam_angle_h)
    cam_z = cam_radius * math.sin(cam_angle_v)
    gluLookAt(cam_x, cam_y, cam_z, 0, 50, 40, 0, 0, 1)


def reshape(w, h):
    global window_width, window_height
    window_width = w if w > 0 else 1
    window_height = h if h > 0 else 1
    glViewport(0, 0, window_width, window_height)


def mouseListener(button, state, x, y):
    game.handle_mouse_click(button, state, x, y, window_width, window_height)


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
    if key in key_states:
        key_states[key] = True
        return

    # Esc key for Pausing
    if key == b"\x1b":
        if game.state == game.STATE_PLAYING:
            game.state = game.STATE_PAUSE
        elif game.state == game.STATE_PAUSE:
            game.state = game.STATE_PLAYING
        elif game.state == game.STATE_RULES:
            game.state = game.previous_state
        return

    if key == b"2":
        game.toggle_state("is_sitting")


def keyboardUpListener(key, x, y):
    if key in key_states:
        key_states[key] = False


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    if game.state == game.STATE_PLAYING:
        setupCamera()
    
    game.render(window_width, window_height)
    glutSwapBuffers()


def idle():
    global last_time
    current_time = glutGet(GLUT_ELAPSED_TIME)
    dt = (current_time - last_time) / 1000.0
    last_time = current_time

    game.update(dt, key_states)
    glutPostRedisplay()


def main():
    global last_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"Nokol Ar Hobe Na - ECS Engine")
    glEnable(GL_DEPTH_TEST)
    last_time = glutGet(GLUT_ELAPSED_TIME)

    glutDisplayFunc(showScreen)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouseListener)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(idle)

    print("--- Controls ---")
    print("WASD       : Move Student (in-game)")
    print("Arrow Keys : Orbit Camera (in-game)")
    print("Mouse      : Navigate Menus")

    glutMainLoop()


if __name__ == "__main__":
    main()
