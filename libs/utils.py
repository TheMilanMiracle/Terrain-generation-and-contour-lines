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
    heights = heights_func(terrain_size)
    vertices = []
    indices = []
    idx = 0

    for i in range(terrain_size-1):
        for j in range(terrain_size-1):
            p0 = np.array([-terrain_size/2 + i,   -terrain_size/2 + j,   heights[i][j]   * (scale * 0.2) + height])
            p1 = np.array([-terrain_size/2 + (i+1), -terrain_size/2 + j,   heights[i+1][j] * (scale * 0.2) + height])
            p2 = np.array([-terrain_size/2 + i,   -terrain_size/2 + (j+1), heights[i][j+1] * (scale * 0.2) + height])
            p3 = np.array([-terrain_size/2 + (i+1), -terrain_size/2 + (j+1), heights[i+1][j+1] * (scale * 0.2) + height])

            v1 = p1 - p0
            v2 = p2 - p0
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)

            for p in (p0, p1, p2):
                vertices += [p[0], p[1], p[2], color[0], color[1], color[2], normal[0], normal[1], normal[2]]
                
            indices += [idx, idx+1, idx+2]
            idx += 3

            v3 = p3 - p1
            v4 = p2 - p1
            normal2 = np.cross(v3, v4)
            normal2 = normal2 / np.linalg.norm(normal2)
            for p in (p2, p1, p3):
                vertices += [p[0], p[1],  p[2],  color[0],  color[1],  color[2],  normal2[0],  normal2[1],  normal2[2]]
            indices += [idx, idx+1, idx+2]
            idx += 3
            
            
    for k in range(terrain_size - 1):
        x0 = -terrain_size/2 + k
        x1 = x0 + 1
        for y, norm, side in [(-terrain_size/2, [0.0, -1.0, 0.0], 0), (terrain_size/2 - 1, [0.0, 1.0, 0.0], terrain_size - 1)]:
            h0 = heights[k][side]   * (scale * 0.2) + height
            h1 = heights[k+1][side] * (scale * 0.2) + height
            p0 = [x0, y, h0] + color + norm
            p1 = [x0, y, 0 ] + color + norm
            p2 = [x1, y, h1] + color + norm
            p3 = [x1, y, 0 ] + color + norm
            vertices += p0 + p1 + p2 + p3
            indices  += [idx, idx+1, idx+2, idx+1, idx+3, idx+2]
            idx += 4

    for k in range(terrain_size - 1):
        y0 = -terrain_size/2 + k
        y1 = y0 + 1
        for x, norm, side in [(-terrain_size/2, [-1.0, 0.0, 0.0], 0), (terrain_size/2 - 1, [1.0, 0.0, 0.0], terrain_size - 1)]:
            h0 = heights[side][k]   * (scale * 0.2) + height
            h1 = heights[side][k+1] * (scale * 0.2) + height
            p0 = [x, y0, h0] + color + norm
            p1 = [x, y0, 0 ] + color + norm
            p2 = [x, y1, h1] + color + norm
            p3 = [x, y1, 0 ] + color + norm
            vertices += p0 + p1 + p2 + p3
            indices  += [idx, idx+1, idx+2, idx+1, idx+3, idx+2]
            idx += 4
    
    down = [0.0, 0.0, -1.0]
    r = terrain_size // 2
    p0 = [-r, -r, 0] + color + down
    p1 = [r - 1, -r, 0]  + color + down
    p2 = [r - 1, r - 1, 0]   + color + down
    p3 = [-r, r - 1, 0]  + color + down
    
    vertices += p0 + p1 + p2 + p3
    indices += [
        idx, idx + 1, idx + 3,
        idx + 1, idx + 2, idx + 3  
    ]
    
    print(f"h in [{round(np.min(heights) * (scale * 0.2) + height, 4)}, {round(np.max(heights) * (scale * 0.2) + height, 4)}]")
    print(f"avg is {round(np.mean(height), 4)}")

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.int32), np.max(heights)*(scale*0.2)+height, np.min(heights)*(scale*0.2)+height, np.mean(heights)*(scale*0.2)+height


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