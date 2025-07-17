#version 330 core

in vec3 frag_position;
in vec3 frag_normal;

uniform vec3  u_light_position;
uniform vec3  u_light_color;
uniform float u_light_strength;

out vec4 out_color;

float ambient_strength = 0.2;
vec3 ambient_color = vec3(0.3, 0.3, 0.3);

float linear = 0.005;
float quadratic = 0.001;

void main()
{
    vec3 ambient = ambient_strength * ambient_color;

    vec3 norm = normalize(frag_normal);
    vec3 light_direction = normalize(u_light_position - frag_position);
    vec3 diffuse = max(dot(norm, light_direction), 0.0) * (u_light_color * u_light_strength);

    float dist = length(u_light_position - frag_position);
    float attenuation = 1.0 / (1.0 + linear * dist + quadratic * dist * dist);

    out_color = vec4((ambient + diffuse * attenuation), 1.0);
}