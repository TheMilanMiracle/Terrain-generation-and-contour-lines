#version 330 core
layout(triangles) in;
in vec4 world_position[];

uniform mat4 projection;
uniform mat4 view;
uniform int size;
uniform float heights[32];
uniform vec3 colors[32];
uniform int curves;

layout(line_strip, max_vertices=64) out;
out vec3 frag_color;

bool is_border(vec4 p) {
    float half = float(size) / 2.0;
    float eps = 0.01;

    return abs(p.x + half) < eps || abs(p.x - (half - 1.0)) < eps ||
           abs(p.y + half) < eps || abs(p.y - (half - 1.0)) < eps;
}

void emitIfIntersect(vec4 v1, float d1, vec4 v2, float d2, vec3 color){
    if(sign(d1) * sign(d2) < 0) {
        float t = abs(d1) / (abs(d1)+abs(d2));
        vec4 v = mix(v1, v2, t);
        if (is_border(v)) return;
        frag_color = color;
        gl_Position = projection * view * v;
        EmitVertex();
    }
}

void main() {
    vec4 p1 = world_position[0], p2 = world_position[1], p3 = world_position[2];

    for (int i = 0; i < curves; i++){
        float h = heights[i];
        int bellow = int(p1.z < h) + int(p2.z < h) + int(p3.z < h);

        if (bellow == 0 || bellow == 3)
            continue; 

        float dist1 = p1.z - h;
        float dist2 = p2.z - h;
        float dist3 = p3.z - h;

        emitIfIntersect(p1, dist1, p2, dist2, colors[i]);
        emitIfIntersect(p2, dist2, p3, dist3, colors[i]);
        emitIfIntersect(p3, dist3, p1, dist1, colors[i]);
        EndPrimitive();
    }

}



