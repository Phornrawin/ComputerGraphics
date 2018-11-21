import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from homework import *
import numpy as np
import pandas as pd
import math as m
import time

win_w, win_h = 1024, 768
model_filenames = ["bunny.tri", "horse.tri"]
models = []
params = {}

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
        params["rot_y"] += angle
    elif key in ('8', '9'):
        angle = -1
        if key == '8':
            angle = 1
        params["rot_z"] += angle
    elif key in ('a', 'd'):
        move = -1
        if key == 'a':
            move = 1
        params["eye_pos"] += (move, 0, 0)        
        params["eye_at"]  += (move, 0, 0)        
    elif key in ('w', 's'):
        move = -1
        if key == 's':
            move = 1
        params["eye_pos"] += (0, move, 0)        
        params["eye_at"]  += (0, move, 0)        
    elif key == 'W':
        wireframe = not wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)
    elif key == 'q':
        exit(0)
    glutPostRedisplay()

def mouse_func(button, state, x, y):
    params["button"] = button
    params["state"] = state
    params["prev_x"] = x
    params["prev_y"] = y

def motion_func():
    params["current_x"] = x
    params["current_y"] = y
    if params["button"] in (GLUT_LEFT_BUTTON, GLUT_MIDDLE_BUTTON):
        if params["button"] == GLUT_LEFT_BUTTON:
            params["rot_y"] += params["current_x"] - params["prev_x"]
            params["rot_x"] += params["prev_y"] - params["current_y"]
        elif params["button"] == GLUT_MIDDLE_BUTTON:
            move_x = 0.25 * (params["prev_x"] - params["current_x"])
            move_y = 0.25 * (params["current_y"] - params["prev_y"])
            params["eye_pos"] += (move_x, move_y, 0)
            params["eye_at"] += (move_x, move_y, 0)
        glutPortRedisplay()

   

tick1, tick2 = 0, 0
def idle():
    global tick1, tick2

    tick1 += 1
    tick2 += 5
    glutPostRedisplay()

def create_shaders():
    vert_id = glCreateShader(GL_VERTEX_SHADER)
    frag_id = glCreateShader(GL_FRAGMENT_SHADER)

    vert_code = b''' /nko
#version 120
varying vec3 color;
void main()
{
   gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
   gl_TexCoord[0] = gl_MultiTexCoord0;
}'''
    frag_code = b'''
#version 120
uniform sample2D texture;
void main()
{
   gl_FragColor = texture2D(texture, *20gl_TexCoord[0].st);
}'''

#ตัวแปร unifrom จะคงที่ตลอด
    glShaderSource(vert_id, vert_code)
    glShaderSource(frag_id, frag_code)

    glCompileShader(vert_id)
    glCompileShader(frag_id)
    print_shader_info_log(vert_id, "Vertex Shader")
    print_shader_info_log(frag_id, "Fragment Shader")

    prog_id = glCreateProgram()
    glAttachShader(prog_id, vert_id)
    glAttachShader(prog_id, frag_id)

    glLinkProgram(prog_id)
    print_program_info_log(prog_id, "Link error")

    if prog_id:
        glUseProgram(prog_id)
    filename = "brick_wall_small.jpg"
    try:
        im = Image.open(filename)
    except:
        print("Error:", sys.exc_info()[0])
        raise
    w = im.size[0]
    h = im.size[1]
    image = im.tobytes("raw", "RGB", 0)
    tex_id = glGenTextures(1)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

def display():
    print("%.2f fps" % (tick1/(time.time()-start_time)), tick1, tick2, end='\r')      
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    eye_pos   = params["eye_pos"]
    eye_at    = params["eye_at"]
    vertices  = params["vertices"]
    normals   = params["normals"]
    colors    = params["colors"]
    texcoords = params["texcoords"]
    rot_y     = params["rot_y"]
    rot_z     = params["rot_z"]

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
    glEnableClientState(GL_VERTEX_ARRAY) #ปลดล็อค Arrayต่างๆ
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
    centroid = params["centroid"] = models[model_id]["centroid"]
    bbox     = params["bbox"]     = models[model_id]["bbox"]
    params["vertices"]  = models[model_id]["vertices" ]
    params["normals"]   = models[model_id]["normals" ]
    params["colors"]    = models[model_id]["colors"] 
    params["texcoords"] = models[model_id]["texcoords"]
    params["eye_pos"]   = np.array((centroid[0], centroid[1], centroid[2]+1.5*bbox[0]), dtype=np.float32)
    params["eye_at"]    = np.array((centroid[0], centroid[1], centroid[2]), dtype=np.float32)
    params["rot_y"]     = 0
    params["rot_z"]     = 0
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
    create_shaders()
    glutMainLoop()

if __name__ == "__main__":
    main()