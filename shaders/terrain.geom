#version 330 core

layout(triangles) in;
in vec3 world_position[];

uniform mat4 projection;
uniform mat4 view;

layout(triangle_strip, max_vertices = 3) out;
out vec3 frag_normal;
out vec3 frag_position;

void main() {
    vec3 p0 = world_position[0];
    vec3 p1 = world_position[1];
    vec3 p2 = world_position[2];

    vec3 v1 = p1 - p0;
    vec3 v2 = p2 - p0;
    vec3 normal = normalize(cross(v1, v2));

    for (int i = 0; i < 3; ++i) {
        gl_Position   = projection * view * vec4(world_position[i], 1.0);

        frag_position = world_position[i];
        frag_normal   = normal;

        EmitVertex();
    }
    EndPrimitive();
}
