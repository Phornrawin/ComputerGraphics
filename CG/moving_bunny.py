import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import pandas as pd

INTERVAL = 3000
df = pd.read_table("bunny.tri", delimiter=" ")

class Bunny:
    x = y = vx = vy = 0.0
    r = g = b = 0.0

bunny = Bunny()

def keyboard(key, x, y):
    key = key.decode("utf-8")
    if key == 'w':
        bunny.y += bunny.vy
        glutPostRedisplay()
    elif key == 's':
        bunny.y -= bunny.vy
        glutPostRedisplay()
    elif key == 'a':
       bunny.x -= bunny.vx
       glutPostRedisplay()
    elif key == 'd':
        bunny.x += bunny.vx
        glutPostRedisplay() # สร้าง event ของ การ display ให้ระบบไปเรียก func ที่เราผูกไว้กับ func display
    elif ord(key) == 27:
        exit(0)

def drawBunny(bunny):
    glBegin(GL_TRIANGLES)
    for i in range(len(df.values)):
        glColor3fv(0.5 * (df.values[i][3:6] + 1))
        glVertex2f(bunny.x + df.values[i][0], bunny.y + df.values[i][1])
    glEnd()

def display():
    glClearColor(0.0, 0.0, 0.0, 0.0) # clear blackground
    glClear(GL_COLOR_BUFFER_BIT) # clear framebuffer
    drawBunny(bunny)
    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, h)
    if w == 0: w = 1
    if h == 0: h = 1

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-12, 12, -12, 12)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(1400, 800)
    glutCreateWindow(b"moving bunny") #มันไม่ได้สร้างหน้าต่าง รอ glutMainLoop() สร้าง Event ของการสร้างหน้าต่าง
    glutReshapeFunc(reshape)
    glutDisplayFunc(display) #สร้าง event ในการ display
    glutKeyboardFunc(keyboard)

    bunny.vx = 0.1
    bunny.vy = 0.1

    glutMainLoop()

if __name__ == "__main__":
    main()


