import numpy as np
import sys
import pandas as pd

vert_coords = []
text_coords = []
norm_coords = []

vertex_index = []
texture_index = []
normal_index = []

params = {}

def load_model(file):
    global vertex_index, texture_index, normal_index, params
    f = file.split('.')
    if f[1] == 'obj':
        for line in open(file, 'r'):
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue
                
            if values[0] == 'v':
                vert_coords.append(values[1:4])
            if values[0] == 'vt':
                text_coords.append(values[1:3])
            if values[0] == 'vn':
                norm_coords.append(values[1:4])
                
            if values[0] == 'f':
                face_i = []
                text_i = []
                norm_i = []
                for v in values[1:4]:
                    w = v.split('/')
                    face_i.append(int(w[0])-1)
                    text_i.append(int(w[1])-1)
                    norm_i.append(int(w[2])-1)
                vertex_index.append(face_i)
                texture_index.append(text_i)
                normal_index.append(norm_i)

        vertices = map_2d_array(vertex_index, vert_coords)
        normals = map_2d_array(normal_index, norm_coords)
        texcoords = map_2d_array(texture_index, text_coords)

        centroid = vertices.mean(axis=0)
        bbox = vertices.max(axis=0) - vertices.min(axis=0)

        colors = 0.5 * (normals.astype(np.float32) + 1)

    elif f[1] == 'tri':
        df = pd.read_table(file, delim_whitespace=True, comment='#', header=None)
        centroid = df.values[:, 0:3].mean(axis=0)
        bbox = df.values[:, 0:3].max(axis=0) - df.values[:, 0:3].min(axis=0)

        vertices = np.ones((len(df.values), 3), dtype=np.float32)
        normals = np.zeros((len(df.values), 3), dtype=np.float32)
        texcoords = np.zeros((len(df.values), 2), dtype=np.float32)
        vertices[:, 0:3] = df.values[:, 0:3]
        normals[:, 0:3] = df.values[:, 3:6]
        texcoords[:, 0:2] = df.values[:, 6:8]
        colors = 0.5*(df.values[:, 3:6].astype(np.float32) + 1)

    else:
        return None


    models = {"vertices": vertices, "normals": normals, 
                    "colors": colors, "texcoords": texcoords,
                    "centroid": centroid, "bbox": bbox}
    print("Model: %s, no. of vertices: %d, no. of triangles: %d" % 
            (file, len(vertices), len(vertices)//3))
    print("Centroid:", centroid)
    print("BBox:", bbox)

    centroid = params["centroid"] = models["centroid"]
    bbox = params["bbox"] = models["bbox"]
    params["vertices"] = models["vertices"]
    params["normals"] = models["normals"]
    params["colors"] = models["colors"] 
    params["texcoords"] = models["texcoords"]
    params["eye_pos"] = np.array((centroid[0], centroid[1], centroid[2]+1.5*bbox[0]), dtype=np.float32)
    params["eye_at"] = np.array((centroid[0], centroid[1], centroid[2]), dtype=np.float32)
    params["rot_y"] = 0
    params["rot_z"] = 0

    return params

def map_2d_array(array, coords):
    a = []
    for x in array:
        arr = []
        for y in range(len(x)):
            arr.append(coords[x[y]])
        a.extend(arr)
    return np.array(a, dtype=np.float32)
