import numpy as np

def normalize(v):
    l = np.linalg.norm(v)
    return v/l

def Identity():
    return np.array([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]], dtype=np.float32)

def Translate(a, b, c):
    return np.array([[1, 0, 0, a],
                     [0, 1, 0, b],
                     [0, 0, 1, c],
                     [0, 0, 0, 1]], dtype=np.float32)

def Rotate(angle, x, y, z):
    if x > 0:
        return np.array([[1, 0, 0, 0],
                        [0, np.cos(angle), -np.sin(angle), 0],
                        [0, np.sin(angle), np.cos(angle), 0],
                        [0, 0, 0, 1]], dtype=np.float32)
    elif y > 0:
        return np.array([[np.cos(angle), 0, np.sin(angle), 0],
                        [0, 1, 0, 0],
                        [-np.sin(angle), 0, np.cos(angle), 0],
                        [0, 0, 0, 1]], dtype=np.float32)
                        
    elif z > 0:
       return np.array([[np.cos(angle), -np.sin(angle), 0, 0],
                        [np.sin(angle), np.cos(angle), 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]], dtype=np.float32)

def Scale(x, y, z):
    return np.array([[x, 0, 0, 0],
                     [0, y, 0, 0],
                     [0, 0, z, 0],
                     [0, 0, 0, 1]], dtype=np.float32)

def LookAt(eyex, eyey, eyez, atx, aty, atz, upx, upy, upz):
    forward = np.array([atx - eyex, aty - eyey, atz - eyez], dtype=np.float32)
    up = np.array([upx, upy, upz], dtype=np.float32)
    normalize(forward)
    side = np.dot(forward, up)
    normalize(side)
    up = np.dot(side, forward)

    return np.array([
                        [side[0], up[0], -forward[0],  0],
                        [side[1], up[1], -forward[1],  0],
                        [side[2], up[2], -forward[2],  0],
                        [0      ,     0,            0, 1]
                    ], dtype=np.float32)

def Ortho(left, right, bottom, top, near, far):
    return np.array([   
                        [2/(right - left), 0, 0, -(right + left)/(right - left)],
                        [0, 2/(top - bottom), 0, -(top + bottom)/(top - bottom)],
                        [0, 0, -2/(far - near), -(far + near)/(far - near)],
                        [0, 0, 0, 1]
                    ], dtype=np.float32)

def Frustum(left, right, bottom, top, near, far):
    return np.array([
                        [2*near/(right - left), 0, (right + left)/(right - left), 0],
                        [0, 2*near/(top - bottom), (top + bottom)/(top - bottom), 0],
                        [0, 0, -(far + near)/(far - near), -2*far*near/(far - near)],
                        [0, 0, -1, 0]
                    ], dtype=np.float32)

def Perspective(fovy, aspect, near, far):
    return np.array([
                        [1/np.tan(fovy/2) * aspect, 0, 0, 0],
                        [0, 1/np.tan(fovy/2), 0, 0],
                        [0, 0, -(far + near)/(far - near), -2*near*far/(far - near)],
                        [0, 0, -1, 0]
                    ], dtype=np.float32)