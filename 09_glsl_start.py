import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pandas as pd
import math as m
import time

win_w, win_h = 1024, 768
model_filenames = ["models/bunny.tri", "models/horse.tri"]
models = []
parameters = {}

def reshape(w, h):
    global win_w, win_h

    win_w, win_h = w, h
    glViewport(0, 0, w, h)  
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, win_w/win_h, 0.01, 50)

wireframe, pause = False, True
def keyboard(key, x, y):
    global wireframe, pause

    key = key.decode("utf-8")
    if key == ' ':
        pause = not pause
        glutIdleFunc(None if pause else idle)
    elif key in ('6', '7'):
        angle = -1
        if key == '6':
            angle = 1
        parameters["rot_y"] += angle
    elif key in ('8', '9'):
        angle = -1
        if key == '8':
            angle = 1
        parameters["rot_z"] += angle
    elif key in ('a', 'd'):
        move = -1
        if key == 'a':
            move = 1
        parameters["eye_pos"] += (move, 0, 0)        
        parameters["eye_at"]  += (move, 0, 0)        
    elif key in ('w', 's'):
        move = -1
        if key == 's':
            move = 1
        parameters["eye_pos"] += (0, move, 0)        
        parameters["eye_at"]  += (0, move, 0)        
    elif key == 'W':
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
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    eye_pos   = parameters["eye_pos"]
    eye_at    = parameters["eye_at"]
    vertices  = parameters["vertices"]
    normals   = parameters["normals"]
    colors    = parameters["colors"]
    texcoords = parameters["texcoords"]
    rot_y     = parameters["rot_y"]
    rot_z     = parameters["rot_z"]

    gluLookAt(*eye_pos, *eye_at, 0, 1, 0)
    glRotatef(rot_y, 0, 1, 0)
    glRotatef(rot_z, 0, 0, 1)
        
    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glNormalPointer(GL_FLOAT, 0, normals)
    glColorPointer(3, GL_FLOAT, 0, colors)
    glTexCoordPointer(2, GL_FLOAT, 0, texcoords)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    glutSwapBuffers()

def gl_init_models():
    global start_time

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    for i in range(len(model_filenames)):
        df = pd.read_table(model_filenames[i], delim_whitespace=True, comment='#', header=None)
        centroid = df.values[:, 0:3].mean(axis=0)
        bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

        vertices = np.ones((len(df.values), 3), dtype=np.float32)
        normals = np.zeros((len(df.values), 3), dtype=np.float32)
        texcoords = np.zeros((len(df.values), 2), dtype=np.float32)
        vertices[:, 0:3] = df.values[:, 0:3]
        normals[:, 0:3] = df.values[:, 3:6]
        texcoords[:, 0:2] = df.values[:, 6:8]
        colors = 0.5*(df.values[:, 3:6].astype(np.float32) + 1)
        models.append({"vertices": vertices, "normals": normals, 
                       "colors": colors, "texcoords": texcoords,
                       "centroid": centroid, "bbox": bbox})
        print("Model: %s, no. of vertices: %d, no. of triangles: %d" % 
               (model_filenames[i], len(vertices), len(vertices)//3))
        print("Centroid:", centroid)
        print("BBox:", bbox)
    model_id = 0
    centroid = parameters["centroid"] = models[model_id]["centroid"]
    bbox     = parameters["bbox"]     = models[model_id]["bbox"]
    parameters["vertices"]  = models[model_id]["vertices" ]
    parameters["normals"]   = models[model_id]["normals" ]
    parameters["colors"]    = models[model_id]["colors"] 
    parameters["texcoords"] = models[model_id]["texcoords"]
    parameters["eye_pos"]   = np.array((centroid[0], centroid[1], centroid[2]+1.5*bbox[0]), dtype=np.float32)
    parameters["eye_at"]    = np.array((centroid[0], centroid[1], centroid[2]), dtype=np.float32)
    parameters["rot_y"]     = 0
    parameters["rot_z"]     = 0
    start_time = time.time() - 0.0001
    
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"GLSL Template")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    gl_init_models()
    glutMainLoop()

if __name__ == "__main__":
    main()