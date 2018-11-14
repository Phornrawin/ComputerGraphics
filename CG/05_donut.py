import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pandas as pd

win_w, win_h = 1024, 768
df = pd.read_table("donut.tri", delim_whitespace=True, comment='#', header=None)
centroid = df.values[:, 0:3].mean(axis=0)

def draw():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(centroid[0] + 1, centroid[1], centroid[2] + 1, centroid[0], centroid[1], centroid[2], 0, 1, 0)
    glRotatef(90, 1, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, win_w/win_h, 0.01, 10)
    glBegin(GL_TRIANGLES)
    for i in range(len(df.values)):
        glColor3fv(df.values[i, 3:6])
        glVertex3fv(df.values[i, 0:3])
    glEnd()
    glutSwapBuffers()

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(win_w, win_h)
glutCreateWindow(b"donut")
glutDisplayFunc(draw)
glEnable(GL_DEPTH_TEST)
glutMainLoop()