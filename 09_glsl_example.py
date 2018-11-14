from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from homework import *
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
void main()
{   vec3 light_pos = vec3(0, 1, 5);
    vec3 light_color = vec3(1, 1, 1);
    vec3 eye_pos = vec3(0, 0, 3);
    vec3 Kd = vec3(0, 1, 1);
    vec3 Ks = vec3(1, 0.8, 0.5);
    float shininess = 50;

    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    vec3 N = gl_Normal.xyz;
    vec3 L = normalize(light_pos - gl_Vertex.xyz);
    vec3 diffuse = Kd * max(dot(N, L), 0) * light_color;
    vec3 E = normalize(eye_pos - gl_Vertex.xyz);
    vec3 H = normalize(E + L);
    vec3 specular = Ks * pow(max(dot(N, H), 0), shininess) * light_color;
    color = diffuse + specular;
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
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 800/600, 0.01, 100)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 3, 0, 0, 0, 0, 1, 0)
    # glMultMatrixf(LookAt(0, 0, 3, 0, 0, 0, 0, 1, 0).T)
    glMultMatrixf(Scale(1.5, 1.5, 1.5).T)
    glUseProgram(prog_id)
    glColor3f(1, 1, 0)
    glRotatef(angle, 0, 1, 0)
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