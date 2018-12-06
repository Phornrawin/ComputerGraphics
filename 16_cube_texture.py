from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from homework import *
import ctypes
import Image
import numpy as np

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

def load_cube_texture(filename=None, tex_unit=GL_TEXTURE0):
    try:
        im = Image.open(filename)
    except:
        print("\"{0}\" not found!".format(filename))
        sys.exit(1)
        w = im.size[0]
        h = im.size[1]
    if 3*w == 4*h:      # Horizontal Cross Cubemap
        sub_w = w // 4
        sub_h = h // 3
        box = [[2, 1], [0, 1], [1, 0], [1, 2], [1, 1], [3, 1]]
    elif 4*w == 3*h:    # Vertical Cross Cubemap
        sub_w = w // 3
        sub_h = h // 4
        box = [[2, 1], [0, 1], [1, 0], [1, 2], [1, 1], [1, 3, 180]]
    else:               # Horizonal Single Row Cubemap
        sub_w = w // 6
        sub_h = h
        box = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]]
    tex_id = glGenTextures(1)
    glActiveTexture(tex_unit)
    glBindTexture(GL_TEXTURE_CUBE_MAP, tex_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    for i in range(6):
        if (box[i][0]+1)*sub_w > w or (box[i][1]+1)*sub_h > h:
            print("Incompatible Image File Format".format(filename))
            sys.exit(1)
            image = im.crop((box[i][0]*sub_w, box[i][1]*sub_h, (box[i][0]+1)*sub_w, (box[i][1]+1)*sub_h))
        if len(box[i]) == 3:
            image = image.rotate(box[i][2])
            image = image.tobytes("raw", "RGB", 0)
            gluBuild2DMipmaps(GL_TEXTURE_CUBE_MAP_POSITIVE_X+i, GL_RGB, sub_w, sub_h, GL_RGB, GL_UNSIGNED_BYTE, image)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glEnable(GL_TEXTURE_CUBE_MAP)
    return tex_unit-GL_TEXTURE0

def drawCube():
    cube_size = 50
    cube = [[ 1, -1, -1], [1, 1, -1], [1, 1, 1], [1, -1, 1],
            [-1, -1, -1], [-1, 1, -1], [-1, 1, 1], [-1, -1, 1],
            [-1, 1, -1], [1, 1, -1], [1, 1, 1], [-1, 1, 1],
            [-1, -1, -1], [1, -1, -1], [1, -1, 1], [-1, -1, 1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]]
    glMatrixMode(GL_PROJECTION)
    glLoadMatrixf(proj_mat.T)
    glMatrixMode(GL_MODELVIEW)
    cubeview_mat = view_mat @ Scale(cube_size, cube_size, cube_size)
    glLoadMatrixf(cubeview_mat.T)
    glBegin(GL_QUADS)
    for i in range(24):
        glTexCoord3fv(cube[i])
        glVertex3fv(cube[i])
    glEnd()

def init():
    global prog_id
    vert_code = b'''
#version 150
varying vec3 color;
uniform vec3 eye_pos, light_pos, Kd, Ks, Ka, I;
uniform float shininess, refract_index;
uniform mat4 model_mat, view_mat, proj_mat;
in vec3 vPos, vNor, e_pos;
out vec3 reflectDir;
void main()
{   
    mat4 mvp = proj_mat * view_mat * model_mat;
    gl_Position = mvp * vec4(vPos, 1);
    mat4 adjunct_mat = transpose(inverse(model_mat));
    vec3 N = (adjunct_mat * vec4(vNor, 1)).xyz;
    vec3 P = (model_mat * vec4(vPos, 1)).xyz;
    vec3 L = normalize(light_pos - P);
    vec3 V = normalize(eye_pos - P);
    vec3 R = -L + 2 * max(dot(L, N), 0) * N;
    vec3 diffuse = Kd * max(dot(N, L), 0) * I;
    vec3 specular = Ks * pow(max(dot(V, R), 0), shininess) * I; 
    vec3 ambient = Ka * I;
    color = diffuse + specular + ambient;

    float eta = 1/refract_index;
    
    reflectDir = reflect(normalize(P - e_pos), N, eta);

}
                '''
    frag_code = b''' 
#version 130
uniform samplerCube cube_map;
in vec3 fCol, reflectDir;
out vec4 gl_FragColor;
void main()
{
    gl_FragColor = texture(cube_map, reflectDir);
}
                '''                
    prog_id = compile_program(vert_code, frag_code)
    glUseProgram(prog_id)
    filename = "footballfield_HCmap.jpg"
    tex_unit = load_cube_texture(filename)
    location = glGetUniformLocation(prog_id, "cube_map")
    glUniform1i(location, tex_unit)

    drawCube()



def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glUseProgram(prog_id)

    eye_pos = (0, 0, 3)
    eye_at = (0, 0, 0)
    light_pos = (0, 1, 5)
    Kd = (0, 1, 1)
    Ks = (1, 0.8, 0.5)
    Ka = (0, 0, 0)
    I = (1, 1, 1)
    shininess = 50

    view_mat = LookAt(*eye_pos, *eye_at, 0, 1, 0)
    view_mat_location = glGetUniformLocation(prog_id, "view_mat")
    glUniformMatrix4fv(view_mat_location, 1, GL_TRUE, view_mat)

    rotate = Rotate(angle, 0, 1, 0)
    model_mat = rotate
    model_mat_location = glGetUniformLocation(prog_id, "model_mat")
    glUniformMatrix4fv(model_mat_location, 1, GL_TRUE, model_mat)


    proj_mat = Perspective(45, 800/600, 0.01, 50)
    proj_mat_location = glGetUniformLocation(prog_id, "proj_mat")
    glUniformMatrix4fv(proj_mat_location, 1, GL_TRUE, proj_mat)

    eye_pos_location = glGetUniformLocation(prog_id, "eye_pos")
    glUniform3f(eye_pos_location, *eye_pos)
    light_pos_location = glGetUniformLocation(prog_id, "light_pos")
    glUniform3f(light_pos_location, *light_pos)
    Kd_location = glGetUniformLocation(prog_id, "Kd")
    glUniform3f(Kd_location, *Kd)
    Ks_location = glGetUniformLocation(prog_id, "Ks")
    glUniform3f(Ks_location, *Ks)
    Ka_location = glGetUniformLocation(prog_id, "Ka")
    glUniform3f(Ka_location, *Ka)
    I_location = glGetUniformLocation(prog_id, "I")
    glUniform3f(I_location, *I)
    shininess_location = glGetUniformLocation(prog_id, "shininess")
    glUniform1f(shininess_location, shininess)


    glColor3f(1, 1, 0)
    glutSolidTeapot(1)
    glutSwapBuffers()

def animate():
    global angle
    angle = angle + 1
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(50, 50)    
    glutCreateWindow(b"GLSL Example")
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glEnable(GL_DEPTH_TEST)
    init()
    glutMainLoop()

if __name__ == "__main__":
    main()    