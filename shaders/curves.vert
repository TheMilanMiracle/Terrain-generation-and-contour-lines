#version 330 core

layout(location = 0) in vec3 in_position;

uniform mat4 projection;
uniform mat4 view;

out vec4 world_position;

void main(){
    world_position = vec4(in_position, 1.0);
    gl_Position = projection * view * world_position;
}