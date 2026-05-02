import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

COLOR_ALIEN = (0.2, 0.9, 0.3)  # Neon green


class StudentRenderer:
    def __init__(self):
        self.quadric = gluNewQuadric()

    def draw_cube(self, w, h, d):
        """Helper to draw scaled cubes."""
        glPushMatrix()
        glScalef(w, h, d)
        glutSolidCube(1.0)
        glPopMatrix()

    def render(self, transform, anim, frame_count):
        """Extracts data from the components and draws the 3D student."""

        # 1. Colors
        face_color = (0.9, 0.7, 0.6)
        body_color = (0.2, 0.4, 0.8)
        pen_color = (1.0, 0.0, 0.0) if anim.is_writing else None
        alpha = 1.0

        # 2. Setup Ghost/Alien overrides
        if anim.is_ghost:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            alpha = 0.5 + 0.3 * math.sin(frame_count * 0.1)
            glColor4f(0.8, 0.8, 1.0, alpha)
        elif anim.is_alien:
            glColor3f(*COLOR_ALIEN)
        else:
            glColor3f(*body_color)

        glPushMatrix()

        # 3. Apply World Transform & Posture Translation
        glTranslatef(transform.x, transform.y, transform.z)
        glRotatef(transform.yaw, 0, 0, 1)

        if anim.is_sitting:
            glTranslatef(0, 0, 10)  # Hips at z=45 (fits perfectly under z=40 desk)
        elif anim.is_walking:
            glTranslatef(0, 0, 15 + abs(math.sin(frame_count * 0.15)) * 3)
        else:
            glTranslatef(0, 0, 15 + math.sin(frame_count * 0.05) * 1.5)

        # 4. Torso & Shirt
        self.draw_cube(30, 15, 40)
        glColor3f(0.9, 0.9, 0.9)
        glPushMatrix()
        glTranslatef(0, 7.6, 5)
        self.draw_cube(20, 1, 25)
        glPopMatrix()

        # 5. Head
        glPushMatrix()
        glTranslatef(0, 0, 30)
        if anim.is_dancing:
            glRotatef(30 * math.sin(frame_count * 0.2), 0, 1, 0)
        elif anim.is_walking:
            glRotatef(5 * math.sin(frame_count * 0.15), 0, 1, 0)
        elif anim.is_writing:
            glRotatef(-25, 1, 0, 0)  # Look down at the paper

        if anim.is_alien:
            glColor3f(*COLOR_ALIEN)
        elif anim.is_ghost:
            glColor4f(0.8, 0.8, 1.0, alpha)
        else:
            glColor3f(*face_color)
        gluSphere(self.quadric, 12, 12, 12)

        if not anim.is_ghost:
            glColor3f(1, 1, 1)
            for side in [-1, 1]:
                glPushMatrix()
                glTranslatef(side * 5, 10, 2)
                gluSphere(self.quadric, 2, 5, 5)
                glColor3f(0, 0, 0)
                glTranslatef(0, 1, 0)
                gluSphere(self.quadric, 1, 5, 5)
                glColor3f(1, 1, 1)
                glPopMatrix()
        glPopMatrix()

        # 6. Arms
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 18, 5, 15)  # Shoulder socket

            if anim.is_writing and side == 1:
                # NEW MATH: Realistic writing motion
                write_sweep = 8 * math.sin(frame_count * 0.15)
                write_jitter = 3 * math.cos(frame_count * 0.8)

                # Upper arm (Shoulder) - Point FORWARD toward the desk (225 degrees)
                glRotatef(225, 1, 0, 0)
                glRotatef(-15, 0, 1, 0)  # Angle slightly inward toward the paper

                if anim.is_ghost:
                    glColor4f(0.8, 0.8, 1.0, alpha)
                else:
                    glColor3f(*body_color)
                self.draw_cube(7, 7, 15)

                # Forearm (Elbow) - Bends to rest horizontally on desk
                glTranslatef(0, 0, 15)
                glRotatef(-45 + write_jitter, 1, 0, 0)  # Up/down stroke motion
                glRotatef(write_sweep, 0, 1, 0)  # Left/right wiper motion across page
                self.draw_cube(6, 6, 18)

                # Hand / Pen
                if pen_color:
                    glTranslatef(0, 0, 9)  # Move to the end of the forearm
                    glPushMatrix()

                    # Angle the pen so it looks like a natural writing grip
                    glRotatef(60, 1, 0, 0)
                    glRotatef(20, 0, 1, 0)

                    if not anim.is_ghost:
                        glColor3f(*pen_color)

                    # 1. Pen Body (Shorter, thinner cylinder)
                    gluCylinder(self.quadric, 0.6, 0.6, 8, 10, 1)

                    # 2. Pen Tip (Darker cone shape that actually touches the paper)
                    glTranslatef(0, 0, 8)
                    if not anim.is_ghost:
                        glColor3f(0.1, 0.1, 0.1)  # Black/Dark ink tip
                    gluCylinder(self.quadric, 0.6, 0.0, 2.5, 10, 1)

                    glPopMatrix()
            else:
                # Standard Arm Logic (Idle, Sit, Walk, Dance)
                base_arm = 225 if anim.is_sitting else 180

                if anim.is_walking:
                    arm_swing = 40 * math.sin(frame_count * 0.15)
                    base_arm = 180 + (arm_swing if side == 1 else -arm_swing)

                if anim.is_dancing:
                    dance_swing = 45 * math.sin(frame_count * 0.1) * side
                    glRotatef(base_arm + dance_swing, 1, 0, 0)
                else:
                    glRotatef(base_arm, 1, 0, 0)

                if anim.is_ghost:
                    glColor4f(0.8, 0.8, 1.0, alpha)
                else:
                    glColor3f(*body_color)

                self.draw_cube(7, 7, 15)
                glTranslatef(0, 0, 15)

                if anim.is_sitting:
                    glRotatef(-45, 1, 0, 0)
                elif anim.is_walking:
                    glRotatef(-20, 1, 0, 0)
                self.draw_cube(6, 6, 15)
            glPopMatrix()

        # 7. Legs
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 10, 0, -20)

            base_leg = -90 if anim.is_sitting else 180
            if anim.is_walking:
                leg_swing = 45 * math.sin(frame_count * 0.15)
                base_leg = 180 - leg_swing if side == 1 else 180 + leg_swing

            glRotatef(base_leg, 1, 0, 0)
            glTranslatef(0, 0, 10)

            if anim.is_ghost:
                glColor4f(0.8, 0.8, 1.0, alpha)
            else:
                glColor3f(*body_color)

            self.draw_cube(10, 10, 30)
            glPopMatrix()

        glPopMatrix()

        if anim.is_ghost:
            glDisable(GL_BLEND)
