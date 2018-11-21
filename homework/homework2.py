import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math as m
import time
from fileloader import *
from matrix_transform import *
from ctypes import c_void_p

win_w, win_h = 800, 600

params = {}
currentRotation = Identity()
startRotation = Identity()
mouses = {"left": False, "middle": False, "right": False}
startX = 0
startY = 0

pan_x = 0
pan_y = 0

zoom_y = 0

prog_id = 0

yellow = 0

rotate = Rotate(0, 1, 0, 0)



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
    global prog_id
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
    global win_w, win_h, zoom
    win_w, win_h = w, h
    glViewport(0, 0, w, h)  

wireframe, pause = False, True

def keyboard(key, x, y):
    global wireframe, pause, yellow

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

    elif key in ('1', '2'):
        yellow  = 1
        if key == '1':
            yellow = 0
    elif key == 'q' or key == 'Q':
        exit(0)
    glutPostRedisplay()

tick1, tick2 = 0, 0
def idle():
    global tick1, tick2

    tick1 += 1
    tick2 += 5
    glutPostRedisplay()

def arcball(x, y):
    global startX, startY, currentRotation, rotate
    if x == startX and y == startY:
        return
    v1 = onSphere(startX, startY)
    v2 = onSphere(x, y)
    axis = np.cross(v2, v1)
    normalize(axis)
    cosTheta = np.dot(v1, v2)

    try:
        angle = -m.acos(cosTheta)/m.pi * 180
        rotate = Rotate(angle, axis[0], axis[1], axis[2]) @ startRotation
        currentRotation = glGetFloatv(GL_MODELVIEW_MATRIX)
    except ValueError:
        pass

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

def pan_camera(x, y):
    global pan_x, pan_y
    if x < 0 or x > win_w: return
    if y < 0 or y > win_h: return
    x = 2*(x * 1.0 / win_h) - 1
    y = 2*((win_h - y) * 1.0 / win_h) - 1
    move = 0
    if abs(x) - abs(y) > 0:    
        if x - pan_x > 0:
            move = -0.1
        elif x - pan_x < 0:
            move = 0.1
        pan_x = x
        params["eye_pos"] += (move, 0, 0)        
        params["eye_at"]  += (move, 0, 0) 
    elif abs(x) - abs(y) < 0:
        if y - pan_y > 0:
            move = -0.1
        elif y - pan_y < 0:
            move = 0.1
        pan_y = y
        params["eye_pos"] += (0, move, 0)        
        params["eye_at"]  += (0, move, 0) 

def zoominout(x, y):
    global zoom_y
    if x < 0 or x > win_w: return
    if y < 0 or y > win_h: return
    x = 2*(x * 1.0 / win_h) - 1
    y = 2*((win_h - y) * 1.0 / win_h) - 1
    zoom = 0
    if y - zoom_y > 0:
        zoom = -0.1
    elif y - zoom_y < 0:
        zoom = 0.1
    zoom_y = y
    params["eye_pos"] += (0, 0, zoom)        
    params["eye_at"]  += (0, 0, zoom) 

def mouse(button, state, x, y):
    global startX, startY
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        startRotation[:] = currentRotation
        startX = x
        startY = y
        mouses["left"] = True
    elif button == GLUT_LEFT_BUTTON and state == GLUT_UP:
        mouses["left"] = False
    if button == GLUT_MIDDLE_BUTTON and state == GLUT_DOWN:
        mouses["middle"] = True
    elif button == GLUT_MIDDLE_BUTTON and state == GLUT_UP:
        mouses["middle"] = False
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        mouses["right"] = True
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_UP:
        mouses["right"] = False

def motion(x, y):
    if mouses["left"] == True:
        arcball(x,y)
        glutPostRedisplay()
    elif mouses["middle"] == True:
        pan_camera(x, y)
        glutPostRedisplay()
    elif mouses["right"] == True:
        zoominout(x, y)
        glutPostRedisplay()

def display():
    global currentRotation, prog_id, yellow, rotate

    print("%.2f fps" % (tick1/(time.time()-start_time)), tick1, tick2, end='\r')      
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    eye_pos   = params["eye_pos"]
    eye_at    = params["eye_at"]
    vertices  = params["vertices"]
    normals   = params["normals"]
    colors    = params["colors"]
    texcoords = params["texcoords"]
    rot_y     = params["rot_y"]
    rot_z     = params["rot_z"]

    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glNormalPointer(GL_FLOAT, 0, normals)
    glColorPointer(3, GL_FLOAT, 0, colors)
    glTexCoordPointer(2, GL_FLOAT, 0, texcoords)

    model_mat = rotate @ currentRotation
    proj_mat = Perspective(45, win_w/win_h, 0.01, 50)
    view_mat = LookAt(*eye_pos, *eye_at, 0, 1, 0)

    glUseProgram(prog_id)
    loc = glGetUniformLocation(prog_id, "color")
    glUniform3f(loc, yellow, 1, 0)
    loc = glGetUniformLocation(prog_id, "proj_mat")
    glUniformMatrix4fv(loc, 1, GL_TRUE, proj_mat)
    loc = glGetUniformLocation(prog_id, "view_mat")
    glUniformMatrix4fv(loc, 1, GL_TRUE, view_mat)
    loc = glGetUniformLocation(prog_id, "model_mat")
    glUniformMatrix4fv(loc, 1, GL_TRUE, model_mat)


    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    glutSwapBuffers()

def init():
    global prog_id
    vert_code = b'''
#version 120
uniform mat4 proj_mat, view_mat, model_mat;
void main()
{   
    gl_Position = proj_mat * view_mat * model_mat * gl_Vertex;
}
                '''
    frag_code = b''' 
#version 120
uniform vec3 color;
void main()
{
    gl_FragColor.rgb = color;
}
                '''                
    prog_id = compile_program(vert_code, frag_code)

def gl_init_models(file):
    global start_time, params

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    params = load_model(file)

    
    start_time = time.time() - 0.0001
    
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"GLSL Homework")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutIdleFunc(idle)
    gl_init_models(sys.argv[1])
    init()
    glutMainLoop()

if __name__ == "__main__":
    main()