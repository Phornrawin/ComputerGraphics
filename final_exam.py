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
import ctypes

win_w, win_h = 1024, 768
model_filenames = ["bunny.tri", "horse.tri", "objects_and_walls.tri"]
models = []
params = {}

clicked = False
startRotation = []
currentRotation = [0, 0]
startX = 0
startY = 0

fog_id, angle, toon_id = 0, 0, 0

toggle = 0
vao1, vao2 = 0, 0 

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

wireframe, pause = False, True
def keyboard(key, x, y):
    global wireframe, pause, toggle

    key = key.decode("utf-8")
    if key == ' ':
        pause = not pause
        glutIdleFunc(None if pause else idle)
    elif key in ('1', '2'):
        toggle = 0
        if key == '2':
            toggle = 1
    elif key in ('4', '5'):
        angle = -1
        if key == '4':
            angle = 1
        params["rot_x"] += angle
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
    elif key in ('j', 'k'):
        move = -1
        if key == 'j':
            move = 1
        params["eye_pos"] += (0, 0, move)        
        params["eye_at"]  += (0, 0, move)      
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

    eye_pos   = params["eye_pos"]
    eye_at    = params["eye_at"]
    vertices  = params["vertices"]
    normals   = params["normals"]
    colors    = params["colors"]
    texcoords = params["texcoords"]
    rot_y     = params["rot_y"]
    rot_z     = params["rot_z"]
    rot_x     = params["rot_x"]

    if toggle == 0:
        glUseProgram(fog_id)

        view_mat = LookAt(*eye_pos, *eye_at, 0, 1, 0)
        view_mat_location = glGetUniformLocation(fog_id, "view_mat")
        glUniformMatrix4fv(view_mat_location, 1, GL_TRUE, view_mat)

        rotate_x = Rotate(rot_x, 1, 0, 0)
        rotate_y = Rotate(rot_y, 0, 1, 0)
        rotate_z = Rotate(rot_z, 0, 0, 1)
        model_mat = rotate_x @ rotate_y @ rotate_z
        model_mat_location = glGetUniformLocation(fog_id, "model_mat")
        glUniformMatrix4fv(model_mat_location, 1, GL_TRUE, model_mat)


        proj_mat = Perspective(45, win_w/win_h, 0.01, 50)
        proj_mat_location = glGetUniformLocation(fog_id, "proj_mat")
        glUniformMatrix4fv(proj_mat_location, 1, GL_TRUE, proj_mat)
    
        light_pos = (-1, 5, 20)
        eye_pos = (5, 5, 5)
        Ks = (1, 0.8, 0.5)
        Ka = (0, 0, 0)
        I = (1, 1, 1)
        shininess = 50

        eye_pos_location = glGetUniformLocation(fog_id, "eye_pos")
        glUniform3f(eye_pos_location, *eye_pos)
        light_pos_location = glGetUniformLocation(fog_id, "light_pos")
        glUniform3f(light_pos_location, *light_pos)
        Ks_location = glGetUniformLocation(fog_id, "Ks")
        glUniform3f(Ks_location, *Ks)
        Ka_location = glGetUniformLocation(fog_id, "Ka")
        glUniform3f(Ka_location, *Ka)
        I_location = glGetUniformLocation(fog_id, "I")
        glUniform3f(I_location, *I)
        shininess_location = glGetUniformLocation(fog_id, "shininess")
        glUniform1f(shininess_location, shininess)

        glBindVertexArray(vao1)
        glDrawArrays(GL_TRIANGLES, 0, len(vertices))
        glutSwapBuffers()

    else:
        glUseProgram(toon_id)

        view_mat = LookAt(*eye_pos, *eye_at, 0, 1, 0)
        view_mat_location = glGetUniformLocation(toon_id, "view_mat")
        glUniformMatrix4fv(view_mat_location, 1, GL_TRUE, view_mat)

        rotate_x = Rotate(rot_x, 1, 0, 0)
        rotate_y = Rotate(rot_y, 0, 1, 0)
        rotate_z = Rotate(rot_z, 0, 0, 1)
        model_mat = rotate_x @ rotate_y @ rotate_z
        model_mat_location = glGetUniformLocation(toon_id, "model_mat")
        glUniformMatrix4fv(model_mat_location, 1, GL_TRUE, model_mat)


        proj_mat = Perspective(45, win_w/win_h, 0.01, 50)
        proj_mat_location = glGetUniformLocation(toon_id, "proj_mat")
        glUniformMatrix4fv(proj_mat_location, 1, GL_TRUE, proj_mat)
    
        light_pos = (-1, 5, 20)
        eye_pos = (5, 5, 5)
        Ks = (1, 0.8, 0.5)
        Ka = (0, 0, 0)
        I = (1, 1, 1)
        shininess = 50

        eye_pos_location = glGetUniformLocation(toon_id, "eye_pos")
        glUniform3f(eye_pos_location, *eye_pos)
        light_pos_location = glGetUniformLocation(toon_id, "light_pos")
        glUniform3f(light_pos_location, *light_pos)
        Ks_location = glGetUniformLocation(toon_id, "Ks")
        glUniform3f(Ks_location, *Ks)
        Ka_location = glGetUniformLocation(toon_id, "Ka")
        glUniform3f(Ka_location, *Ka)
        I_location = glGetUniformLocation(toon_id, "I")
        glUniform3f(I_location, *I)
        shininess_location = glGetUniformLocation(toon_id, "shininess")
        glUniform1f(shininess_location, shininess)
        glBindVertexArray(vao2)
        glDrawArrays(GL_TRIANGLES, 0, len(vertices))
        glutSwapBuffers()


def create_vbo():
    global vao1, vao2
    vao1 = glGenVertexArrays(1)
    glBindVertexArray(vao1)

    vbo = glGenBuffers(4)
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, params["vertices"], GL_STATIC_DRAW)
    location = glGetAttribLocation(fog_id, "position")
    glVertexAttribPointer(location, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
    glEnableVertexAttribArray(location)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
    glBufferData(GL_ARRAY_BUFFER, params["normals"], GL_STATIC_DRAW)
    location = glGetAttribLocation(fog_id, "normal")
    if location != -1:
        glVertexAttribPointer(location, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(location)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[2])
    glBufferData(GL_ARRAY_BUFFER, params["colors"], GL_STATIC_DRAW)
    location = glGetAttribLocation(fog_id, "color")
    if location != -1:
        glVertexAttribPointer(location, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(location)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[3])
    glBufferData(GL_ARRAY_BUFFER, params["texcoords"], GL_STATIC_DRAW)
    location = glGetAttribLocation(fog_id, "texcoord")
    if location != -1:
        glVertexAttribPointer(location, 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(location)


    vao2 = glGenVertexArrays(1)
    glBindVertexArray(vao2)

    vbo = glGenBuffers(4)
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, params["vertices"], GL_STATIC_DRAW)
    location = glGetAttribLocation(toon_id, "position")
    glVertexAttribPointer(location, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
    glEnableVertexAttribArray(location)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
    glBufferData(GL_ARRAY_BUFFER, params["normals"], GL_STATIC_DRAW)
    location = glGetAttribLocation(toon_id, "normal")
    if location != -1:
        glVertexAttribPointer(location, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(location)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[2])
    glBufferData(GL_ARRAY_BUFFER, params["colors"], GL_STATIC_DRAW)
    location = glGetAttribLocation(toon_id, "color")
    if location != -1:
        glVertexAttribPointer(location, 3, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(location)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[3])
    glBufferData(GL_ARRAY_BUFFER, params["texcoords"], GL_STATIC_DRAW)
    location = glGetAttribLocation(toon_id, "texcoord")
    if location != -1:
        glVertexAttribPointer(location, 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glEnableVertexAttribArray(location)

def init():
    global fog_id, toon_id
    vert_code = b'''
#version 330
in vec3 position, normal, color; 
in vec2 texcoord;
uniform mat4 model_mat, view_mat, proj_mat;
out vec3 fPos, fCol, fNor;
void main()
{   
    gl_Position = proj_mat * view_mat * model_mat * vec4(position, 1);
    fPos = position;
    fCol = color;
    fNor = normal;
}
                '''
    frag_code = b''' 
#version 330
uniform vec3 eye_pos, light_pos, Ks, Ka, I;
uniform float shininess;
uniform mat4 model_mat, view_mat, proj_mat;
in vec3 fPos, fCol, fNor;
out vec4 gl_FragColor;
void main()
{
    vec3 N = normalize(fNor);
    vec3 L = normalize(light_pos - fPos);
    vec3 V = normalize(eye_pos - fPos);
    vec3 R = -L + 2 * max(dot(L, N), 0) * N;
    vec3 Kd = fCol;

    float diffuse, specular, edge;
    diffuse = max(dot(N, L), 0);
    specular = pow(max(dot(V, R), 0), shininess); 
    if (diffuse == 0)
        specular = 0;
    edge = max(dot(N, V), 0);
    vec3 diff_color, spec_color;
    if (diffuse > 0.5)
        diff_color = Kd;
    else
        diff_color = 0.5 * Kd;
    if (specular > 0.3)
        spec_color = Ks;
    else
        spec_color = vec3(0, 0, 0);
    if (edge < 0.3)
        edge = 0;
    else
        edge = 1;

    vec3 color = edge * (diff_color + spec_color) * fCol;
    gl_FragColor = vec4(clamp(color, 0, 1), 1);
}
                '''                
    toon_id = compile_program(vert_code, frag_code)

    vert_code = b'''
#version 150
in vec3 position, normal, color; 
in vec2 texcoord;
out vec3 fcolor;
uniform vec3 eye_pos, light_pos, Ks, Ka, I;
uniform float shininess;
uniform mat4 model_mat, view_mat, proj_mat;
out float Fog;
float max_distance = 100;
void main()
{   
    float distance = abs((view_mat * model_mat * vec4(position, 1)).z);
    Fog = clamp(distance, 0, max_distance);
    Fog = clamp((max_distance - Fog)/max_distance, 0, 1);
    
    gl_Position = proj_mat * view_mat * model_mat * vec4(position, 1);
    mat4 adjunct_mat = transpose(inverse(model_mat));
    vec3 N = normalize((adjunct_mat * vec4(normal, 0)).xyz);
    vec3 P = (model_mat * vec4(position, 1)).xyz;
    vec3 L = normalize(light_pos - P);
    vec3 V = normalize(eye_pos - P);
    vec3 R = -L + 2 * max(dot(L, N), 0) * N;
    vec3 Kd = color;

    vec3 diffuse = Kd * max(dot(N, L), 0) * I;
    vec3 specular = Ks * pow(max(dot(V, R), 0), shininess) * I; 
    vec3 ambient = Ka * I;

    fcolor = diffuse + specular + ambient;
    fcolor = clamp(fcolor, 0, 1);
}
                '''
    frag_code = b''' 
#version 150
in vec3 fcolor;
in float Fog;
vec4 fog_color = vec4(0.95, 1, 1, 1);
void main()
{
    gl_FragColor = mix(fog_color, vec4(fcolor, 1), Fog);
}
                '''                
    fog_id = compile_program(vert_code, frag_code)


def gl_init_models():
    global start_time

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)


    for i in range(len(model_filenames)):
        df = pd.read_table(model_filenames[i], delim_whitespace=True, comment='#', header=None)
        centroid = df.values[:, 0:3].mean(axis=0)
        bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

        vertices = np.ones((len(df.values), 3), dtype=np.float32)
        normals = np.zeros((len(df.values), 3), dtype=np.float32)
        texcoords = np.zeros((len(df.values), 2), dtype=np.float32)

        if len(df.values[0]) == 8:
            vertices[:, 0:3] = df.values[:, 0:3]
            normals[:, 0:3] = df.values[:, 3:6]
            texcoords[:, 0:2] = df.values[:, 6:8]
            colors = 0.5*(df.values[:, 3:6].astype(np.float32) + 1)
        else :
            colors = np.zeros((len(df.values), 3), dtype=np.float32)
            vertices[:, 0:3] = df.values[:, 0:3]
            colors[:, 0:3] = df.values[:, 3:6]
            normals[:, 0:3] = df.values[:, 6:9]
            texcoords[:, 0:2] = df.values[:, 9:11]


        models.append({"vertices": vertices, "normals": normals, 
                       "colors": colors, "texcoords": texcoords,
                       "centroid": centroid, "bbox": bbox})
        print("Model: %s, no. of vertices: %d, no. of triangles: %d" % 
               (model_filenames[i], len(vertices), len(vertices)//3))
        print("Centroid:", centroid)
        print("BBox:", bbox)
    model_id = 1
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
    init()
    create_vbo()
    glutMainLoop()

if __name__ == "__main__":
    main()