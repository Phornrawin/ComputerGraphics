import sys
from OpenGL.GL import *
from OpenGL.GLUT import *

def display():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)

def printAndReschedule(interval):
	print("I'm printing this every %d milliseconds\n" % interval)
	glutTimerFunc(interval, printAndReschedule, interval)

def main():
	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_RGBA | GLUT_SINGLE)
	glutCreateWindow(b"glutTimerFunc Example 02")
	glutDisplayFunc(display)
	glutTimerFunc(0, printAndReschedule, 500)
	glutTimerFunc(0, printAndReschedule, 1000)
	glutTimerFunc(0, printAndReschedule, 2000)
	glutMainLoop()

if __name__ == "__main__":
	main()