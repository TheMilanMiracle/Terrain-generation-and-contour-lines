import numpy as np
import random
import noise

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
    
    return vertices, indices



def gen_terrain(terrain_size, height, scale, color):
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
    
    heights = diamond_square(terrain_size)
    
    vertices = []
    for i in range(terrain_size):
        for j in range(terrain_size):
            x = -terrain_size/2 + i
            y = -terrain_size/2 + j
            z = heights[i][j]
            vertices += [x, y, z * scale + height] + color
    
    
    indices = []
    for i in range(terrain_size-1):
        for j in range(terrain_size-1):
            tl = i * terrain_size + j
            tr = i * terrain_size + (j + 1)
            bl = (i + 1) * terrain_size + j
            br = (i + 1) * terrain_size + (j + 1)

            indices += [tl, bl, tr]
            indices += [tr, bl, br]
            
    
    return vertices, indices
    
    

import numpy as np

def pnoise_heights():
    shape = (11, 11)
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