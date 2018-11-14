import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from math import pi, sin, cos
from random import uniform

INTERVAL = 50
CORNERS  = 25

class Ball:
    x = y = vx = vy = 0.0
    radius = 0.0
    r = g = b = 0.0

balls = []

def newRandomBall():
    ball = Ball()
    ball.radius = 0.03 + uniform(0, 0.08)
    ball.x = uniform(-1+ball.radius, 1-ball.radius)
    ball.y = uniform(-1+ball.radius, 1-ball.radius)
    ball.vx = 0.01 + uniform(0, 0.02)
    ball.vy = 0.01 + uniform(0, 0.02)
    ball.r = uniform(0.01, 1)
    ball.g = uniform(0.01, 1)
    ball.b = uniform(0.01, 1)
    balls.append(ball)

def keyboard(key, x, y):
    key = key.decode("utf-8")
    if key == ' ':
        newRandomBall()
        glutPostRedisplay()
    elif ord(key) == 27:
        exit(0)

def updateBall(ball):
    ball.x += ball.vx
    ball.y += ball.vy
    if ball.x + ball.radius > 1:
        ball.x = 1 - ball.radius
        ball.vx = -abs(ball.vx)

    if ball.x - ball.radius < -1:
        # handle collision with left wall
        ball.x = -1 + ball.radius
        ball.vx = abs(ball.vx)
    if ball.y + ball.radius > 1:
        # handle collision with top wall
        ball.y = 1 - ball.radius
        ball.vy = -abs(ball.vy)       
    if ball.y - ball.radius < -1:
        # handle collision with bottom wall
        ball.y = -1 + ball.radius
        ball.vy = abs(ball.vy)

def drawBall(ball):
    glColor3d(ball.r, ball.g, ball.b)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2d(ball.x, ball.y)
    for i in range(CORNERS):
        theta = 2*pi*i/CORNERS
        x = ball.x + ball.radius * cos(theta)
        y = ball.y + ball.radius * sin(theta)
        glVertex2d(x,y)
    glVertex2d(ball.x + ball.radius, ball.y)
    glEnd()

def display():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    for ball in balls:
        drawBall(ball)
    glutSwapBuffers()

def animate(param):
    for ball in balls:
        updateBall(ball)
    glutTimerFunc(INTERVAL, animate, 0)
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(600, 600)
    glutCreateWindow(b"Bouncing Balls")
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, animate, 0)

    glutMainLoop()

if __name__ == "__main__":
    main()