#version 330 core

in vec3 frag_position;
in vec3 frag_color;
in vec3 frag_normal;

uniform vec3 light_position;

out vec4 out_color;

float ambient_strength = 0.4;
vec3 ambient_color = vec3(0.5, 0.5, 0.5);
vec3 diffuse_color = vec3(0.6, 0.6, 0.2);

void main()
{
    vec3 ambient = ambient_strength * ambient_color;

    vec3 norm = normalize(frag_normal);
    vec3 light_direction = normalize(light_position - frag_position);
    vec3 diffuse = max(dot(norm, light_direction), 0.0) * diffuse_color;

    out_color = vec4((ambient + diffuse) * frag_color, 1.0);
}