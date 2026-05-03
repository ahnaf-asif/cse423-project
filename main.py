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

# Track keys
key_states = {
    b"w": False, b"a": False, b"s": False, b"d": False,
    "left": False, "right": False, "up": False, "down": False,
    b"e": False, b" ": False
}


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, window_width / window_height, 0.5, 5000)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Get player transform
    player_transform = game.player.get_component("Transform")
    
    yaw_r = math.radians(player_transform.yaw)
    pitch_r = math.radians(player_transform.pitch)

    # Direction the camera is looking (First Person)
    look_x = math.sin(yaw_r) * math.cos(pitch_r)
    look_y = math.cos(yaw_r) * math.cos(pitch_r)
    look_z = math.sin(pitch_r)

    gluLookAt(
        player_transform.x, player_transform.y, player_transform.z,
        player_transform.x + look_x, player_transform.y + look_y, player_transform.z + look_z,
        0, 0, 1
    )


def reshape(w, h):
    global window_width, window_height
    window_width = w if w > 0 else 1
    window_height = h if h > 0 else 1
    glViewport(0, 0, window_width, window_height)


def mouseListener(button, state, x, y):
    game.handle_mouse_click(button, state, x, y, window_width, window_height)


def specialKeyListener(key, x, y):
    if key == GLUT_KEY_LEFT:
        key_states["left"] = True
    elif key == GLUT_KEY_RIGHT:
        key_states["right"] = True
    elif key == GLUT_KEY_UP:
        key_states["up"] = True
    elif key == GLUT_KEY_DOWN:
        key_states["down"] = True


def specialKeyUpListener(key, x, y):
    if key == GLUT_KEY_LEFT:
        key_states["left"] = False
    elif key == GLUT_KEY_RIGHT:
        key_states["right"] = False
    elif key == GLUT_KEY_UP:
        key_states["up"] = False
    elif key == GLUT_KEY_DOWN:
        key_states["down"] = False


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

    # Actions
    if key == b"e":
        game.interact()
    elif key == b" ":
        game.dismiss_laptop()


def keyboardUpListener(key, x, y):
    if key in key_states:
        key_states[key] = False


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    if game.state == game.STATE_PLAYING:
        # Check if laptop is being used to skip 3D setup if needed
        # (Though LaptopRenderer does its own projection setup)
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
    glutSpecialUpFunc(specialKeyUpListener)
    glutIdleFunc(idle)

    print("--- Controls ---")
    print("WASD       : Move Invigilator")
    print("Arrow Keys : Look around")
    print("E          : Interact (Laptop/Students)")
    print("SPACE      : Dismiss laptop screen")
    print("ESC        : Pause")

    glutMainLoop()


if __name__ == "__main__":
    main()
