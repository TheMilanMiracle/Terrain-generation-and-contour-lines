#version 330 core

in vec2 in_position;

uniform float u_zoom;
uniform int   u_octaves;
uniform float u_persistence; 
uniform float u_lacunarity; 
uniform float u_height_offset; 
uniform vec2  u_plane_offset; 
uniform float u_scale; 
uniform int u_seed;

out vec4 world_position;

vec2 fade(vec2 t) {
    return t * t * (3.0 - 2.0 * t);
}

float grad(int hash, vec2 p) {
    // gradiente pseudo‑aleatorio
    int h = hash & 7;        // toma 3 bits
    vec2 grad = (h < 4) ? vec2(1.0,1.0) : vec2(-1.0,-1.0);
    if ((h & 1) != 0) grad.x = -grad.x;
    if ((h & 2) != 0) grad.y = -grad.y;
    return dot(grad, p);
}

int permute(int x) {
    return (((x + u_seed) * 34) + 1) * (x + u_seed) % 289;
}

float perlin2d(vec2 P) {
    // celda
    ivec2 Pi = ivec2(floor(P)) & 255;
    vec2   Pf = fract(P);
    vec2   f  = fade(Pf);

    // hashes de cuatro esquinas
    int A  = permute(Pi.x) + Pi.y;
    int AA = permute(A);
    int AB = permute(A + 1);
    int B  = permute(Pi.x + 1) + Pi.y;
    int BA = permute(B);
    int BB = permute(B + 1);

    // contribuciones
    float v00 = grad(permute(AA), Pf - vec2(0.0,0.0));
    float v10 = grad(permute(BA), Pf - vec2(1.0,0.0));
    float v01 = grad(permute(AB), Pf - vec2(0.0,1.0));
    float v11 = grad(permute(BB), Pf - vec2(1.0,1.0));

    // interpola bilinealmente
    float x1 = mix(v00, v10, f.x);
    float x2 = mix(v01, v11, f.x);
    return mix(x1, x2, f.y);
}


float fractalPerlin(vec2 P) {
    float amplitude = 1.0;
    float frequency = 1.0;
    float sum = 0.0;
    float norm = 0.0;
    for (int i = 0; i < u_octaves; i++) {
        sum += amplitude * perlin2d(P * frequency);
        norm += amplitude;
        amplitude *= u_persistence;
        frequency *= u_lacunarity;
    }
    return sum / norm;
}

void main()
{
    float h = fractalPerlin(in_position / u_zoom + u_plane_offset);

    world_position = vec4(in_position, u_height_offset + h * u_scale, 1.0);
}
