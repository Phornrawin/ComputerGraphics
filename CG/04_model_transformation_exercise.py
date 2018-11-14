import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pandas as pd
import math as m

win_w, win_h = 1024, 768
df = pd.read_table("bunny.tri", delim_whitespace=True, comment='#', header=None)
centroid = df.values[:, 0:3].mean(axis=0)

def reshape(w, h):
    global win_w, win_h

    win_w, win_h = w, h
    glViewport(0, 0, w, h)  
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, win_w/win_h, 0.01, 200)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(centroid[0], centroid[1], centroid[2]+50, *centroid, 0, 1, 0)

wireframe, pause = False, True
def keyboard(key, x, y):
    global wireframe, pause

    key = key.decode("utf-8")
    if key == ' ':
        pause = not pause
        glutIdleFunc(None if pause else idle)
    elif key == 'w':
        wireframe = not wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)
    elif key == 'q':
        exit(0)
    glutPostRedisplay()

tick1, tick2 = 0, 0
def idle():
    global tick1, tick2

    tick1 += 1
    tick2 += 5
    glutPostRedisplay()

def display():
    global vbo, positions, colors

    angle = tick1 / 180 * m.pi
    sin_val = m.sin(angle)
    cos_val = m.cos(angle)
    m1 = np.array([
        [cos_val, 0, sin_val, 0],
        [0, 1, 0, 0],
        [-sin_val, 0, cos_val, 0],
        [0, 0, 0, 1]
        ], dtype=np.float32)
    x_positions = (m1.dot(positions.T)).T
    glutPostRedisplay()
        
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, x_positions, GL_DYNAMIC_DRAW)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
    glBufferData(GL_ARRAY_BUFFER, colors, GL_DYNAMIC_DRAW)
    glDrawArrays(GL_TRIANGLES, 0, len(df.values))

    m2 = np.array([
        [1, 0, 0, 20],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
        ], dtype=np.float32)

    angle = tick2 / 180 * m.pi
    sin_val = m.sin(angle)
    cos_val = m.cos(angle)

    m3 = np.array([
        [cos_val, 0, -sin_val, 0],
        [0, 1, 0, 0],
        [sin_val, 0, cos_val, 0],
        [0, 0, 0, 1]
        ], dtype=np.float32)
    x_positions = (m1 @ m2 @ m3 @ positions.T).T

    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, x_positions, GL_DYNAMIC_DRAW)
    glDrawArrays(GL_TRIANGLES, 0, len(df.values))

    glutSwapBuffers()

def gl_init():
    global vbo, positions, colors, normals

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    positions = df.values[:, 0:4].astype(np.float32)
    positions[:, 3] = 1
    normals = df.values[:, 3:6].astype(np.float32)
    colors = np.copy(normals)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = glGenBuffers(3)
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, positions, GL_DYNAMIC_DRAW)
    position_loc = 0
    glVertexAttribPointer(position_loc, 4, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
    glEnableVertexAttribArray(position_loc)
    color_loc = 3
    if color_loc != -1:
        glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
        glBufferData(GL_ARRAY_BUFFER, colors, GL_DYNAMIC_DRAW)
        glVertexAttribPointer(color_loc, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(color_loc)    

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"Transformations")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    gl_init()
    glutMainLoop()

if __name__ == "__main__":
    main()