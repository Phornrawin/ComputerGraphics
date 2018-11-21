import numpy as np
import math as m

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
    sin = m.sin(angle * m.pi / 180)
    cos = m.cos(angle * m.pi / 180)
    return np.array([[x * x * (1 - cos) + cos, x * y * (1 - cos) - z * sin, x * z * (1 - cos) + y * sin, 0],
                     [y * x * (1 - cos) + z * sin, y * y * (1 - cos) + cos, y * z * (1 - cos) - x * sin, 0],
                     [x * z * (1 - cos) - y * sin, y * z * (1 - cos) + x * sin, z * z * (1 - cos) + cos, 0],
                     [0, 0, 0, 1]], dtype=np.float32)

def Scale(x, y, z):
    return np.array([[x, 0, 0, 0],
                     [0, y, 0, 0],
                     [0, 0, z, 0],
                     [0, 0, 0, 1]], dtype=np.float32)

def LookAt(eyex, eyey, eyez, atx, aty, atz, upx, upy, upz):
    eye = np.array([[eyex], [eyey], [eyez]])
    at = np.array([[atx], [aty], [atz]])
    up = np.array([[upx], [upy], [upz]])
    Z = normalize(eye - at)
    Y = normalize(up)
    X = normalize(np.cross(Y.T, Z.T))
    Y = normalize(np.cross(Z.T, X))
    Z = Z.T
    return np.array([[X[0][0], X[0][1], X[0][2], -np.dot(X, eye)],
                     [Y[0][0], Y[0][1], Y[0][2], -np.dot(Y, eye)],
                     [Z[0][0], Z[0][1], Z[0][2], -np.dot(Z, eye)],
                     [0, 0, 0, 1]], dtype=np.float32)

def Ortho(left, right, bottom, top, near, far):
    return np.array([[2/(right-left), 0, 0, -((right+left)/(right-left))],
                     [0, 2/(top-bottom), 0, -((top+bottom)/(top-bottom))],
                     [0, 0,-2/(far-near), -((far+near)/(far-near))],
                     [0, 0, 0, 1]], dtype=np.float32)

def Frustum(left, right, bottom, top, near, far):
    return np.array([[2*near/(right-left), 0, (right+left)/(right-left), 0],
                     [0, 2*near/(top-bottom), (top+bottom)/(top-bottom), 0],
                     [0, 0,-((far+near)/(far-near)), -(2*(far*near)/(far-near))],
                     [0, 0, -1, 0]], dtype=np.float32)

def Perspective(fovy, aspect, near, far):
    cot = 1 / m.tan((fovy * m.pi / 180)/ 2)
    return np.array([[cot/aspect, 0, 0, 0],
                     [0, cot, 0, 0],
                     [0, 0, -(far+near)/(far-near), (-2*near*far)/(far-near)],
                     [0, 0, -1, 0]], dtype=np.float32)

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm