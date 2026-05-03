import math
import os
import sys

# Add the project root to the sys.path so we can import from 'game' and 'components'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.student_anim_state import StudentAnimState
from components.transform import Transform
from game.student_renderer import StudentRenderer
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Global state for testing
transform = Transform(0, 0, 40)
anim = StudentAnimState()
renderer = StudentRenderer()
frame_count = 0.0
last_time = 0

# Orbital Camera
cam_radius = 150.0
cam_angle_h = math.pi / 2
cam_angle_v = 0.3


def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 800 / 600, 0.1, 1000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    cam_x = cam_radius * math.cos(cam_angle_v) * math.cos(cam_angle_h)
    cam_y = cam_radius * math.cos(cam_angle_v) * math.sin(cam_angle_h)
    cam_z = cam_radius * math.sin(cam_angle_v)
    gluLookAt(cam_x, cam_y, cam_z, 0, 0, 40, 0, 0, 1)


def keyboard_listener(key, x, y):
    global anim
    if key == b"2":
        anim.is_sitting = not anim.is_sitting
        if anim.is_sitting:
            anim.is_walking = False
    elif key == b"3":
        anim.is_dancing = not anim.is_dancing
    elif key == b"4":
        anim.is_alien = not anim.is_alien
    elif key == b"5":
        anim.is_ghost = not anim.is_ghost
    elif key == b"6":
        anim.is_writing = not anim.is_writing
    elif key == b"w":
        anim.is_walking = not anim.is_walking
        if anim.is_walking:
            anim.is_sitting = False
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

    # Draw a small reference grid
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_LINES)
    for i in range(-100, 101, 20):
        glVertex3f(i, -100, 0)
        glVertex3f(i, 100, 0)
        glVertex3f(-100, i, 0)
        glVertex3f(100, i, 0)
    glEnd()

    renderer.render(transform, anim, frame_count)
    glutSwapBuffers()


def idle():
    global last_time, frame_count
    current_time = glutGet(GLUT_ELAPSED_TIME)
    dt = (current_time - last_time) / 1000.0
    last_time = current_time
    frame_count += dt * 60.0
    glutPostRedisplay()


def main():
    global last_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Student Isolation Test")
    glEnable(GL_DEPTH_TEST)

    last_time = glutGet(GLUT_ELAPSED_TIME)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutIdleFunc(idle)

    print("--- Student Test Controls ---")
    print("W          : Toggle Walking")
    print("2          : Toggle Sitting")
    print("3          : Toggle Dancing")
    print("4          : Toggle Alien")
    print("5          : Toggle Ghost")
    print("6          : Toggle Writing")
    print("Arrow Keys : Orbit Camera")
    print("ESC        : Exit")

    glutMainLoop()


if __name__ == "__main__":
    main()
