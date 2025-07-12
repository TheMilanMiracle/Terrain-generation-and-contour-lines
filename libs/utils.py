import numpy as np
import random
import noise
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

def diamond_square(size, roughness=0.6):
        assert (size & (size - 1)) == 0, "size debe ser potencia de 2"
        n = size + 1
        T = np.zeros((n, n), dtype=np.float32)
        T[0,0], T[0,-1], T[-1,0], T[-1,-1] = [random.random() for _ in range(4)]
        step, scale = size, roughness
        while step > 1:
            half = step // 2
            for i in range(half, size, step):
                for j in range(half, size, step):
                    avg = (T[i-half,j-half]+T[i-half,j+half]+T[i+half,j-half]+T[i+half,j+half])*0.25
                    T[i,j] = avg + random.uniform(-scale, scale)
            for i in range(0, n, half):
                for j in range((i+half)%step, n, step):
                    pts = []
                    if i-half >= 0: pts.append(T[i-half,j])
                    if i+half < n: pts.append(T[i+half,j])
                    if j-half >= 0: pts.append(T[i,j-half])
                    if j+half < n: pts.append(T[i,j+half])
                    T[i,j] = sum(pts)/len(pts) + random.uniform(-scale, scale)
            step //= 2
            scale *= roughness
        return T
    
def pnoise_heights(n):
    shape = (n, n)
    scale = 100.0
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0

    heights = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            heights[i][j] = noise.pnoise2(i/scale, 
                                        j/scale, 
                                        octaves=octaves, 
                                        persistence=persistence, 
                                        lacunarity=lacunarity, 
                                        repeatx=shape[0], 
                                        repeaty=shape[1], 
                                        base=0)
    
    return heights


def gen_terrain(terrain_size, height, scale, color, heights_func):
    # heights = heights_func(terrain_size)
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
            
    print(f"avg is {round(np.mean(height), 4)}")

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