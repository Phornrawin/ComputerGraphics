import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import pandas as pd
from ctypes import c_void_p

df = pd.read_table("bunny.tri", delimiter=" ")
positions = np.zeros((len(df.values), 3), dtype=np.float32)
positions[:, :] = df.values[:, 0:3]

colors = np.zeros((len(df.values), 3), dtype=np.float32)
colors[:, :] = df.values[:, 3:6]


def keyboard(key, x, y):
    key = key.decode("utf-8")
    if key == 'w':
        positions[:, 1:2] = positions[:, 1:2] + vy
        glutPostRedisplay()
    elif key == 's':
        positions[:, 1:2] = positions[:, 1:2] - vy
        glutPostRedisplay()
    elif key == 'a':
        positions[:, 0:1] = positions[:, 0:1] - vx
        glutPostRedisplay()
    elif key == 'd':
        positions[:, 0:1] = positions[:, 0:1] + vx
        glutPostRedisplay()
    elif ord(key) == 27:
        exit(0)


def draw():
    global vbo
    glClearColor(0, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
    glEnableVertexAttribArray(0)
    glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
    glEnableVertexAttribArray(3)
    glBufferData(GL_ARRAY_BUFFER, colors, GL_STATIC_DRAW)

    glDrawArrays(GL_TRIANGLES, 0, len(df.values))
    glutSwapBuffers()


def reshape(w, h):
    glViewport(0, 0, w, h)
    if w == 0: w = 1
    if h == 0: h = 1

    aspect = w / h * 20

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if w > h:
        gluOrtho2D(-aspect, aspect, -20, 20)
    else:
        gluOrtho2D(-20, 20, -aspect, aspect)


def idle():
    glRotate(3, 0, 1, 0)
    glutPostRedisplay()


glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(600, 600)
glutCreateWindow(sys.argv[0].encode("utf-8"))
glutReshapeFunc(reshape)
glutDisplayFunc(draw)
# glutIdleFunc(idle)
glutKeyboardFunc(keyboard)
vbo = glGenBuffers(2)
vy = 0.2
vx = 0.2
glutMainLoop()




