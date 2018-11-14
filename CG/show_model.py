import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
import pandas as pd

df = pd.read_table("ball.tri", delimiter=" ")
def draw():
    glClearColor(0, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_TRIANGLES)
    for i in range(len(df.values)):
        glColor3fv(0.5 * (df.values[i][3:6] + 1))
        glVertex3fv(df.values[i][0:3])
    glEnd()
    glFlush()

def idle():
    glRotate(2, 0, 1, 0)
    glutPostRedisplay()

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_SINGLE)
glutCreateWindow(b"lab02")
glutDisplayFunc(draw)
glutIdleFunc(idle)
glutMainLoop()