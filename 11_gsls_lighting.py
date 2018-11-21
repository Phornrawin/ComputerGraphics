from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from homework import *
import ctypes

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

def init():
    global prog_id
    vert_code = b'''
#version 120
varying vec3 color;
uniform vec3 eye_pos, light_pos, Kd, Ks, Ka, I;
uniform float shininess;
uniform mat4 model_mat, view_mat, proj_mat;
void main()
{   
    gl_Position = proj_mat * view_mat * model_mat * gl_Vertex;
    mat4 adjunct_mat = model_mat;
    vec3 N = normalize((adjunct_mat * vec4(gl_Normal.xyz, 0)).xyz);
    vec3 P = (model_mat * gl_Vertex).xyz;
    vec3 L = normalize(light_pos - P);
    vec3 V = normalize(eye_pos - P);
    vec3 R = -L + 2 * max(dot(L, N), 0) * N;

    vec3 diffuse = Kd * max(dot(N, L), 0) * I;
    vec3 specular = Ks * pow(max(dot(V, R), 0), shininess) * I; 
    vec3 ambient = Ka * I;

    color = diffuse + specular + ambient;
}
                '''
    frag_code = b''' 
#version 120
varying vec3 color;
void main()
{
    gl_FragColor.rgb = color;
}
                '''                
    prog_id = compile_program(vert_code, frag_code)

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