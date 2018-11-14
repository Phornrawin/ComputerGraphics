import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

win_w, win_h = 800, 800
depth_test = False

def reshape(w, h):
    global win_w, win_h

    win_w, win_h = w, h
    glViewport(0, 0, w, h)  

def keyboard(key, x, y):
    global depth_test

    key = key.decode("utf-8")
    if key == 'd':
        depth_test = not depth_test
    elif key == 'q':
        exit(0)
    glutPostRedisplay()

def writeMessage(msg, x=20, y=20, stroke=False, color=[0,0,1], font=GLUT_BITMAP_HELVETICA_18):
    prev_mode = glGetIntegerv(GL_MATRIX_MODE)
    viewport = glGetIntegerv(GL_VIEWPORT)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, viewport[2], 0, viewport[3], -1, 1)
    glColor3fv(color)
    glRasterPos2f(x, y)
    for i in msg:
        glutBitmapCharacter(font, ord(i))
    glPopMatrix()
    glMatrixMode(prev_mode)      

def display():
    if depth_test:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        writeMessage("Depth Test is ON", stroke=True)
    else:
        glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        writeMessage("Depth Test is OFF")

    glBegin(GL_TRIANGLES)
    glColor3d(0.5, 1, 0.5)
    glVertex3d(0, 0.5, 0)
    glVertex3d(-0.5, -0.5, 0)
    glVertex3d(0.5, -0.5, 0)

    glColor3d(1, 0.5, 0.5)
    glVertex3d(0, -0.75, 1)
    glVertex3d(0.40, 0, 1)
    glVertex3d(-0.40, 0.30, -1)
    glEnd()

    glutSwapBuffers()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"Triangle Penetration")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glClearColor(1, 1, 1, 1)
    glutMainLoop()

if __name__ == "__main__":
    main()