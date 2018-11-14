import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pandas as pd
import math as m
import time

win_w, win_h = 1024, 768
model_filenames = ["star.tri", "horse.tri"]

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

def normalize(v):
    len_v = np.linalg.norm(v)
    if len_v != 0:
        v = v * (1/len_v)
    return v

def display():
    print("%.2f fps" % (tick1/(time.time()-start_time)), tick1, tick2, end='\r')      
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    model_id = 0
    centroid = models[model_id]["centroid"]
    bbox     = models[model_id]["bbox"]
    vertices = models[model_id]["vertices"]
    normals  = models[model_id]["normals"]
    colors   = models[model_id]["colors"]

    eye_pos = np.array((centroid[model_id], centroid[1], centroid[2]+1.5*bbox[0]), dtype=np.float32)
    gluLookAt(*eye_pos, *centroid, 0, 1, 0)
    light_pos = eye_pos
    
    Kd = np.array((212/255, 175/255, 55/255), dtype=np.float32)
    Ks = np.array((0.8, 0.8, 0.8), dtype=np.float32)
    n = 50
    I = np.array((1, 1, 1), dtype=np.float32)
    # Kd = Kd.reshape(-1, 1)
    # Ks = Ks.reshape(-1, 1)
    # I = I.reshape(-1, 1)
    # light_pos = light_pos.reshape(-1, 1)
    L = light_pos - vertices
    L = L * (1/np.linalg.norm(L, axis=1)).reshape(-1, 1)
    N = normals
    NdotL = np.maximum(np.sum(N * L, axis=1), 0)
    colors[:] = Kd * NdotL.reshape(-1, 1) * I
    # ambient = np.array((0, 0, 0), dtype=np.float32)
    # diffuse = np.array((0, 0, 0), dtype=np.float32)
    # specular = np.array((0, 0, 0), dtype=np.float32)

    # for i in range(len(vertices)):
    #     L = normalize(light_pos - vertices[i])
    #     NdotL = normals[i].dot(L)
    #     diffuse = Kd * max(NdotL, 0) * I 

    #     V = normalize(eye_pos - vertices[i])
    #     H = normalize(L + V)
    #     HdotN = normals[i].dot(H)
    #     specular = Ks * m.pow(max(HdotN, 0), n) * I
    #     color = ambient + diffuse + specular
    #     colors[i, :] = color



    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glNormalPointer(GL_FLOAT, 0, normals)
    glColorPointer(3, GL_FLOAT, 0, colors)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    glutSwapBuffers()

models = []
def gl_init_models():
    global start_time

    glClearColor(0, 0, 0, 0)
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