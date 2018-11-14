import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def draw():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glColor3f(1, 1, 1)
    glBegin(GL_POLYGON)
    glVertex3f(-0.5, -0.5, 0)
    glVertex3f(0.5, -0.5, 0)
    glVertex3f(0.5, -0.5, 0)
    glVertex3f(-0.5, 0.5, 0)
    glEnd()
    glFlush()
def reshape(w, h):
    glViewport(0, 0, w, h)
    if w == 0: w = 1
    if h == 0: h = 1

    aspect = w / h

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if w > h:
        gluOrtho2D(-aspect, aspect, -1, 1)
    else:
        gluOrtho2D(-1, 1, -1/aspect, 1/aspect)

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_SINGLE)
glutCreateWindow(b"whitespace")
glutReshapeFunc(reshape)
glutDisplayFunc(draw)
glutMainLoop()

