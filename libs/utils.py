import numpy as np
import math


def load_shader(path):
    with open(path, 'r') as f:
        src = f.read()
    return src

def gen_base_mesh(size, divs, color):
    r = size/2
    
    vertices = []
    indices = []
    
    vertices += [-r, -r, 0.0] + color
    vertices += [r, -r, 0.0] + color
    vertices += [r, r, 0.0] + color
    vertices += [-r, r, 0.0] + color
    
    indices += [0, 1,
                1, 2, 
                2, 3,
                3, 0]
            
    idx = 4
    for i in range(1, divs + 1):
        vertices += [-r, -r + (size/(divs + 1)) * i, 0.0] + color
        vertices += [r , -r + (size/(divs + 1)) * i, 0.0] + color
        
        indices += [idx, idx + 1]
        idx += 2
        
        vertices += [-r + (size/(divs + 1)) * i, -r , 0.0] + color
        vertices += [-r + (size/(divs + 1)) * i, r , 0.0] + color
        
        indices += [idx, idx + 1]
        idx += 2

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.int32)


def gen_terrain(terrain_size):
    vertices = []
    indices = []
    idx = 0

    for i in range(terrain_size-1):
        for j in range(terrain_size-1):
            p0 =[-terrain_size/2 + i,   -terrain_size/2 + j]
            p1 =[-terrain_size/2 + (i+1), -terrain_size/2 + j]
            p2 =[-terrain_size/2 + i,   -terrain_size/2 + (j+1)]
            p3 =[-terrain_size/2 + (i+1), -terrain_size/2 + (j+1)]

            for p in (p0, p1, p2):
                vertices += [p[0], p[1]]
                
            indices += [idx, idx+1, idx+2]
            idx += 3
            
            for p in (p2, p1, p3):
                vertices += [p[0], p[1]]
            indices += [idx, idx+1, idx+2]
            idx += 3
            
    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.int32)


def gen_sphere(cx, cy, cz, r, color, divs=16):
    vertices = []
    indices = []

    for i in range(divs + 1):
        phi = math.pi * i / divs
        for j in range(divs + 1):
            theta = 2 * math.pi * j / divs

            x = cx + r * math.sin(phi) * math.cos(theta)
            y = cy + r * math.cos(phi)
            z = cz + r * math.sin(phi) * math.sin(theta)
            vertices += [x, y, z]
            vertices += color

    for i in range(divs):
        for j in range(divs):
            first = i * (divs + 1) + j
            second = first + divs + 1

            indices += [ first, second, first + 1 ]
            indices += [ first + 1, second, second + 1 ]

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.int32)