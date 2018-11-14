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

prog_id, twisting_location, color_location, twisting = None, None, None, 0.0
wireframe = False

def create_shaders():
    global prog_id, twisting_location, color_location

    vert_id = glCreateShader(GL_VERTEX_SHADER)
    frag_id = glCreateShader(GL_FRAGMENT_SHADER)

    twisting_vert_code = b'''
#version 110
uniform float twisting;
void main()
{
    float angle = twisting * length(gl_Vertex.xy);
    float s = sin(angle);
    float c = cos(angle);
    gl_Position.x = c * gl_Vertex.x - s * gl_Vertex.y;
    gl_Position.y = s * gl_Vertex.x + c * gl_Vertex.y;
    gl_Position.z = 0.0;
    gl_Position.w = 1.0;
}'''
    twisting_frag_code = b'''
#version 110
uniform vec3 color;
void main()
{
    gl_FragColor = vec4(color, 1);
}'''
    glShaderSource(vert_id, twisting_vert_code)
    glShaderSource(frag_id, twisting_frag_code)

    glCompileShader(vert_id)
    glCompileShader(frag_id)
    print_shader_info_log(vert_id, "Vertex Shader")
    print_shader_info_log(frag_id, "Fragment Shader")

    prog_id = glCreateProgram()
    glAttachShader(prog_id, vert_id)
    glAttachShader(prog_id, frag_id)

    glLinkProgram(prog_id)
    print_program_info_log(prog_id, "Link error")
    
    twisting_location = glGetUniformLocation(prog_id, "twisting")
    color_location = glGetUniformLocation(prog_id, "color")

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-1, 1, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glUseProgram(prog_id);
    glUniform1f(twisting_location, twisting)
    glUniform3f(color_location, 0.5, 0.9, 0.5)
   
    count = 50
    size = 1.0 / count
   
    glBegin(GL_QUADS)

    for i in range(count):
        for j in range(count):
            x = -0.5 + i * size;
            y = -0.5 + j * size;

            glVertex2f(x,      y)
            glVertex2f(x+size, y)
            glVertex2f(x+size, y+size)
            glVertex2f(x,      y+size)
   
    glEnd()
    glutSwapBuffers()

def keyboard(key, x, y):
    global twisting, wireframe

    key = key.decode("utf-8")
    if key == '+':
        twisting += 0.05
    elif key == '-':
        twisting -= 0.05
    elif key.lower() == 'w':
        wireframe = not wireframe
        if wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    elif ord(key) == 27:
        exit(0)
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(512, 512)
    glutInitWindowPosition(50, 50)    
    glutCreateWindow(b"2D Twisting")
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)    
    create_shaders()
    glutMainLoop()

if __name__ == "__main__":
    main()