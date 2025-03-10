import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pandas as pd
import math as m
import time
from PIL import Image
from homework import *

win_w, win_h = 1024, 768
model_filenames = ["models/bunny.tri", "models/horse.tri"]
models = []
params = {}

clicked = False
startRotation = []
currentRotation = [0, 0]
startX = 0
startY = 0

prog_id, angle = 0, 0

def print_shader_info_log(shader, prompt=""):
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetShaderInfoLog(shader).decode("utf-8")))
        return -1
    else:
        return 0

def print_program_info_log(program, prompt=""):
    result = glGetProgramiv(program, GL_LINK_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetProgramInfoLog(program).decode("utf-8")))
        return -1
    else:
        return 0

def compile_program(vertex_code, fragment_code):
    vert_id = glCreateShader(GL_VERTEX_SHADER)
    frag_id = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(vert_id, vertex_code)
    glShaderSource(frag_id, fragment_code)
    glCompileShader(vert_id)
    glCompileShader(frag_id)
    print_shader_info_log(vert_id, "Vertex Shader")
    print_shader_info_log(frag_id, "Fragment Shader")

    prog_id = glCreateProgram()
    glAttachShader(prog_id, vert_id)
    glAttachShader(prog_id, frag_id)

    glLinkProgram(prog_id)
    print_program_info_log(prog_id, "Link error")
    
    return prog_id  

def reshape(w, h):
    global win_w, win_h

    win_w, win_h = w, h
    glViewport(0, 0, w, h)  
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # gluPerspective(45, win_w/win_h, 0.01, 50)
    # glMultMatrixf(Perspective(45, win_w/win_h, 0.01, 50).T)

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

def arcball(x, y):
    global startX, startY, currentRotation
    if x == startX and y == startY:
        return
    v1 = onSphere(startX, startY)
    v2 = onSphere(x, y)
    axis = np.cross(v2, v1)
    axis = axis / np.linalg.norm(axis)
    cosTheta = np.dot(v1, v2)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotatef(-m.cos(cosTheta)/m.pi*180, axis[0], axis[1], axis[2])
    glMultMatrixf(startRotation)
    currentRotation = glGetFloatv(GL_MODELVIEW_MATRIX)

def onSphere(x, y):
    xs = 2*(x / win_w) - 1
    ys = 2*((win_h - y) / win_h) - 1
    l = xs*xs + ys*ys
    if l > 1:
        xs /= m.sqrt(l)
        ys /= m.sqrt(l)
        l = 1

    zs = m.sqrt(1 - l*l)
    return np.array((xs, ys, zs), dtype=np.float32)

def mouse(button, state, x, y):
    global startX, startY, currentRotation, clicked
    if state == GLUT_DOWN and button == GLUT_RIGHT_BUTTON:
        startRotation[:] = currentRotation
        startX = x
        startY = y
        clicked = True
    elif state == GLUT_UP and button == GLUT_RIGHT_BUTTON:
        clicked = False

def motion(x, y):
    global clicked
    if clicked:
        arcball(x,y)
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

    eye_pos   = params["eye_pos"]
    eye_at    = params["eye_at"]
    vertices  = params["vertices"]
    normals   = params["normals"]
    colors    = params["colors"]
    texcoords = params["texcoords"]
    rot_y     = params["rot_y"]
    rot_z     = params["rot_z"]
    rot_x     = params["rot_x"]

    # gluLookAt(*eye_pos, *eye_at, 0, 1, 0)
    # glMultMatrixf(LookAt(*eye_pos, *eye_at, 0, 1, 0).T)
    # glRotatef(rot_y, 0, 1, 0)
    # glRotatef(rot_z, 0, 0, 1)
    # glRotatef(rot_x, 1, 0, 0)
    # glMultMatrixf(Rotate(rot_x, 1, 0, 0).T)
    # glMultMatrixf(Rotate(rot_z, 0, 0, 1).T)
    # glMultMatrixf(Rotate(rot_y, 0, 1, 0).T)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glEnable(GL_TEXTURE_2D)

    glUseProgram(prog_id)

    view_mat = LookAt(*eye_pos, *eye_at, 0, 1, 0)
    view_mat_location = glGetUniformLocation(prog_id, "view_mat")
    glUniformMatrix4fv(view_mat_location, 1, GL_TRUE, view_mat)

    rotate_x = Rotate(rot_x, 1, 0, 0)
    rotate_y = Rotate(rot_y, 0, 1, 0)
    rotate_z = Rotate(rot_z, 0, 0, 1)
    model_mat = rotate_z @ rotate_x @ rotate_y @ Scale(1.5, 1.5, 1.5)
    model_mat_location = glGetUniformLocation(prog_id, "model_mat")
    glUniformMatrix4fv(model_mat_location, 1, GL_TRUE, model_mat)


    proj_mat = Perspective(45, win_w/win_h, 0.01, 50)
    proj_mat_location = glGetUniformLocation(prog_id, "proj_mat")
    glUniformMatrix4fv(proj_mat_location, 1, GL_TRUE, proj_mat)

    location_x = glGetUniformLocation(prog_id, "x")
    glUniform1f(location_x, 1.0)

    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glNormalPointer(GL_FLOAT, 0, normals)
    glColorPointer(3, GL_FLOAT, 0, colors)
    glTexCoordPointer(2, GL_FLOAT, 0, texcoords)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    glutSwapBuffers()

def gl_init_models():
    global start_time, prog_id

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
    params["rot_x"]     = 0
    start_time = time.time() - 0.0001

    vert_code = b'''
#version 120
uniform mat4 model_mat, view_mat, proj_mat;
uniform float x;
void main()
{ 
    gl_Position = proj_mat * view_mat * model_mat * gl_Vertex;
    gl_TexCoord[0] = gl_MultiTexCoord0;

}
                '''
    frag_code = b''' 
#version 120
uniform sampler2D texture;
void main()
{
    gl_FragColor = texture2D(texture, 20* gl_TexCoord[0].st);
}
                '''                
    prog_id = compile_program(vert_code, frag_code)

    filename = "texture_map/brick_wall_small.jpg"
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
    texture_location = glGetUniformLocation(prog_id, "texture")

    
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"GLSL Template")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutIdleFunc(idle)
    gl_init_models()
    glutMainLoop()

if __name__ == "__main__":
    main()