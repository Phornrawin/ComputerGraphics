import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pandas as pd
import math as m
import time

win_w, win_h = 1024, 768
model_filenames = ["bunny.tri", "horse.tri"]

def reshape(w, h):
    global win_w, win_h

    win_w, win_h = w, h
    glViewport(0, 0, w, h)  

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

    print("%.2f fps" % (tick1/(time.time()-start_time)), tick1, tick2, end='\r')      
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    model_id = 1
    vertices = models[model_id]["vertices"]
    normals  = models[model_id]["normals"]
    colors   = models[model_id]["colors"]
    centroid = models[model_id]["centroid"]
    bbox     = models[model_id]["bbox"]
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, win_w/win_h, 0.001, 100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 5, 18, 0, 0, 0, 0, 1, 0)
    glTranslatef(*(centroid))
    for i in range(6):
        glPushMatrix()
        # คำสั่งที่อยู่ใกล้ vertex ทำก่อน
        glTranslatef((i-3) * bbox[0], 0, 0)
        draw_model(model_id)
        glPopMatrix()
    glutSwapBuffers()
    # glScalef(2/bbox[0], 2/bbox[1], 2/bbox[2])

def draw_model(model_id=0):
    if model_id < 0 or model_id >= len(models):
        return
    glVertexPointer(3, GL_FLOAT, 0, models[model_id]["vertices"])
    glNormalPointer(GL_FLOAT, 0, models[model_id]["normals"])
    glColorPointer(3, GL_FLOAT, 0, models[model_id]["colors"])
    glDrawArrays(GL_TRIANGLES, 0, len(models[model_id]["vertices"]))

models = []
def gl_init_models():
    global start_time

    glClearColor(0.95, 0.95, 0.8, 0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)

    for i in range(len(model_filenames)):
        df = pd.read_table(model_filenames[i], delim_whitespace=True, comment='#', header=None)
        centroid = df.values[:, 0:3].mean(axis=0)
        bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

        vertices = np.ones((len(df.values), 3), dtype=np.float32)
        normals = np.zeros((len(df.values), 3), dtype=np.float32)
        vertices[:, 0:3] = df.values[:, 0:3]
        normals[:, 0:3] = df.values[:, 3:6]
        colors = 0.5*(df.values[:, 3:6].astype(np.float32) + 1)
        models.append({"vertices": vertices, "normals": normals, "colors": colors, 
                       "centroid": centroid, "bbox": bbox})
        print("Model: %s, no. of vertices: %d, no. of triangles: %d" % 
               (model_filenames[i], len(vertices), len(vertices)//3))
        print("Centroid:", centroid)
        print("BBox:", bbox)

    start_time = time.time() - 0.0001
    
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"OpenGL Transformations")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    gl_init_models()
    glutMainLoop()

if __name__ == "__main__":
    main()