import math
import os
import sys

# Add the project root to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.student_desk_state import StudentDeskState
from components.transform import Transform
from game.student_desk_renderer import StudentDeskRenderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Global state for testing
transform = Transform(0, 0, 0)
desk_state = StudentDeskState()
renderer = StudentDeskRenderer()
last_time = 0

# Orbital Camera
cam_radius = 200.0
cam_angle_h = math.pi / 4
cam_angle_v = 0.5


def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 800 / 600, 0.1, 1000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    cam_x = cam_radius * math.cos(cam_angle_v) * math.cos(cam_angle_h)
    cam_y = cam_radius * math.cos(cam_angle_v) * math.sin(cam_angle_h)
    cam_z = cam_radius * math.sin(cam_angle_v)
    gluLookAt(cam_x, cam_y, cam_z, 0, 0, 20, 0, 0, 1)


def keyboard_listener(key, x, y):
    global desk_state
    if key == b"1":
        desk_state.calculator.is_visible = not desk_state.calculator.is_visible
    elif key == b"2":
        desk_state.smartphone.is_visible = not desk_state.smartphone.is_visible
    elif key == b"3":
        desk_state.calculator.is_being_inspected = (
            not desk_state.calculator.is_being_inspected
        )
    elif key == b"4":
        desk_state.smartphone.is_being_inspected = (
            not desk_state.smartphone.is_being_inspected
        )
    elif key == b"\x1b":
        sys.exit()
    glutPostRedisplay()


def special_key_listener(key, x, y):
    global cam_angle_h, cam_angle_v
    if key == GLUT_KEY_LEFT:
        cam_angle_h -= 0.1
    elif key == GLUT_KEY_RIGHT:
        cam_angle_h += 0.1
    elif key == GLUT_KEY_UP:
        cam_angle_v = min(cam_angle_v + 0.1, 1.5)
    elif key == GLUT_KEY_DOWN:
        cam_angle_v = max(cam_angle_v - 0.1, 0.1)
    glutPostRedisplay()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    setup_camera()

    # Draw floor grid
    glColor3f(0.1, 0.1, 0.1)
    glBegin(GL_LINES)
    for i in range(-150, 151, 30):
        glVertex3f(i, -150, 0)
        glVertex3f(i, 150, 0)
        glVertex3f(-150, i, 0)
        glVertex3f(150, i, 0)
    glEnd()

    renderer.render(transform, desk_state)
    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Desk Isolation Test")
    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)

    print("--- Desk Test Controls ---")
    print("1          : Toggle Calculator Visibility")
    print("2          : Toggle Smartphone Visibility")
    print("3          : Toggle Calculator Inspection")
    print("4          : Toggle Smartphone Inspection")
    print("Arrow Keys : Orbit Camera")
    print("ESC        : Exit")

    glutMainLoop()


if __name__ == "__main__":
    main()
