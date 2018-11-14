import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import *

def print_shader_info_log(shader, prompt=""):
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetShaderInfoLog(shader).decode("utf-8")))
        sys.exit()

def print_program_info_log(shader, prompt=""):
    result = glGetProgramiv(shader, GL_LINK_STATUS)
    if not result:
        print("%s: %s" % (prompt, glGetProgramInfoLog(shader).decode("utf-8")))
        sys.exit()

def create_shaders():
    vert_id = glCreateShader(GL_VERTEX_SHADER)
    frag_id = glCreateShader(GL_FRAGMENT_SHADER)

    vert_code = b'''
#version 120
varying vec3 color;
void main()
{
   gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
   color = vec3(1, 0, 0);
   if (gl_Vertex.x < 0) {
       color = vec3(0, 1, 0);
   } else {
       if (gl_Vertex.x > 0) {
           color = vec3(0, 0, 1);
       }
   } 
}'''
    frag_code = b'''
#version 120
varying vec3 color;
void main()
{
   gl_FragColor = vec4(color, 1);
}'''
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
 
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-1, 1, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glBegin(GL_TRIANGLES)
    glVertex3f(-0.5, -0.5, 0)
    glVertex3f( 0.5, -0.5, 0)
    glVertex3f(   0,  0.5, 0)
    glEnd()
    glutSwapBuffers()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(512, 512)
    glutInitWindowPosition(50, 50)    
    glutCreateWindow(b"Green Triangle")
    glutDisplayFunc(display)
    create_shaders()
    glutMainLoop()

if __name__ == "__main__":
    main()