#version 330 core

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec3 in_color;
layout(location = 2) in vec3 in_normal;

uniform mat4 projection;
uniform mat4 view;
uniform vec3 light_position;

out vec3 frag_position;
out vec3 frag_color;
out vec3 frag_normal;

void main()
{
    gl_Position = projection * view * vec4(in_position, 1.0);

    frag_position = vec3(vec4(in_position, 1.0));
    frag_color = in_color;
    frag_normal = in_normal;
}
