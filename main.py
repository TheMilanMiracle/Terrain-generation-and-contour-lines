import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr
import os
import sys

from libs.utils import load_shader
from libs.controller import Controller
from libs.camera import Camera

WINDOW_DIMENSIONS = (1280, 720)
WINDOW_TITLE = "t3"

if len(sys.argv) != 2:
    print("usage: python ./main.py <size>", file=sys.stderr)
    exit(1)

SIZE = int(sys.argv[1])

camera = Camera(SIZE * 1.2, [-SIZE, -SIZE, 5.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], 70, 0.1, 10000, *WINDOW_DIMENSIONS)
controller = Controller(*WINDOW_DIMENSIONS, WINDOW_TITLE, camera)

light_vertices, light_indices = controller.gen_sphere()
grid_vertices, grid_indices = controller.generate_floor(SIZE * 4, SIZE // 4, [0.1, 0.3, 0.4])
terrain_vertices, terrain_indices = controller.generate_terrain(SIZE, SIZE / 10, 200, [0.6, 0.2, 0.2])

light_shader = compileProgram(
    compileShader(load_shader(os.path.join("shaders", "light.vert")), GL_VERTEX_SHADER), 
    compileShader(load_shader(os.path.join("shaders", "light.frag")), GL_FRAGMENT_SHADER)
)
grid_shader = compileProgram(
    compileShader(load_shader(os.path.join("shaders", "grid.vert")), GL_VERTEX_SHADER), 
    compileShader(load_shader(os.path.join("shaders", "grid.frag")), GL_FRAGMENT_SHADER)
)
terrain_shader = compileProgram(
    compileShader(load_shader(os.path.join("shaders", "terrain.vert")), GL_VERTEX_SHADER), 
    compileShader(load_shader(os.path.join("shaders", "terrain.frag")), GL_FRAGMENT_SHADER),
)
curves_shader = compileProgram(
    compileShader(load_shader(os.path.join("shaders", "curves.vert")), GL_VERTEX_SHADER),
    compileShader(load_shader(os.path.join("shaders", "curves.frag")), GL_FRAGMENT_SHADER),
    compileShader(load_shader(os.path.join("shaders", "curves.geom")), GL_GEOMETRY_SHADER),
)

# light vao
light_vao = glGenVertexArrays(1)
glBindVertexArray(light_vao)

# light vbo
light_vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, light_vbo)
glBufferData(GL_ARRAY_BUFFER, light_vertices.nbytes, light_vertices, GL_STATIC_DRAW)

# light indices
light_ebo = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, light_ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, light_indices.nbytes, light_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, light_vertices.itemsize * 6, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, light_vertices.itemsize * 6, ctypes.c_void_p(12))

# grid vao
grid_vao = glGenVertexArrays(1)
glBindVertexArray(grid_vao)

# grid vertices
grid_vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, grid_vbo)
glBufferData(GL_ARRAY_BUFFER, grid_vertices.nbytes, grid_vertices, GL_STATIC_DRAW)

# grid indices
grid_ebo = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, grid_ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, grid_indices.nbytes, grid_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, grid_vertices.itemsize * 6, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, grid_vertices.itemsize * 6, ctypes.c_void_p(12))

# terrain vao
terrain_vao = glGenVertexArrays(1)
glBindVertexArray(terrain_vao)

# terrain points
terrain_vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, terrain_vbo)
glBufferData(GL_ARRAY_BUFFER, terrain_vertices.nbytes, terrain_vertices, GL_STATIC_DRAW)

# terrain indices
terrain_ebo = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, terrain_ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, terrain_indices.nbytes, terrain_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, terrain_vertices.itemsize * 9, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, terrain_vertices.itemsize * 9, ctypes.c_void_p(12))

glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, terrain_vertices.itemsize * 9, ctypes.c_void_p(24))

# light shader uniforms
glUseProgram(light_shader)
lproj_loc = glGetUniformLocation(light_shader, "projection")
lview_loc = glGetUniformLocation(light_shader, "view")

glUniformMatrix4fv(lproj_loc, 1, GL_FALSE, camera.projection)

# grid shader uniforms
glUseProgram(grid_shader)
gproj_loc = glGetUniformLocation(grid_shader, "projection")
gview_loc = glGetUniformLocation(grid_shader, "view")

glUniformMatrix4fv(lproj_loc, 1, GL_FALSE, camera.projection)

# terrain shader uniforms
glUseProgram(terrain_shader)
proj_loc = glGetUniformLocation(terrain_shader, "projection")
view_loc = glGetUniformLocation(terrain_shader, "view")
light_pos_loc = glGetUniformLocation(terrain_shader, "light_position")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, camera.projection)
controller.proj_loc = proj_loc

# curves shader uniforms
glUseProgram(curves_shader)
cproj_loc = glGetUniformLocation(curves_shader, "projection")
cview_loc = glGetUniformLocation(curves_shader, "view")

size_loc = glGetUniformLocation(curves_shader, "size")
heights_loc = glGetUniformLocation(curves_shader, "heights")
colors_loc = glGetUniformLocation(curves_shader, "colors")
curves_loc = glGetUniformLocation(curves_shader, "curves")

glUniformMatrix4fv(cproj_loc, 1, GL_FALSE, camera.projection)
glUniform1i(size_loc, SIZE)
glUniform1fv(heights_loc, 32, controller.heights)
glUniform3fv(colors_loc, 32, controller.colors)
glUniform1i(size_loc, controller.curves)

def draw_light():
    global light_indices, light_vertices
    
    if not controller.draw_light_src:
        return
    
    glBindVertexArray(light_vao)
    glUseProgram(light_shader)
    glUniformMatrix4fv(lview_loc, 1, GL_FALSE, camera.view())
    
    if controller.new_light_pos:
        light_vertices, light_indices = controller.gen_sphere()
        
        glBindBuffer(GL_ARRAY_BUFFER, light_vbo)
        glBufferData(GL_ARRAY_BUFFER, light_vertices.nbytes, light_vertices, GL_STATIC_DRAW)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, light_indices.nbytes, light_indices, GL_STATIC_DRAW)
        
        controller.new_light_pos = False
    
    glDrawElements(GL_TRIANGLES, len(light_indices), GL_UNSIGNED_INT, None)
    

def draw_grid():
    global grid_indices
    glUseProgram(grid_shader)
    glUniformMatrix4fv(gview_loc, 1, GL_FALSE, camera.view())
    
    glBindVertexArray(grid_vao)
    glDrawElements(GL_LINES, len(grid_indices), GL_UNSIGNED_INT, None)


def draw_terrain():
    global terrain_vertices, terrain_indices
    
    glUseProgram(terrain_shader)
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, camera.view())
    glUniform3fv(light_pos_loc, 1, controller.light_position)
    glBindVertexArray(terrain_vao)
    
    if controller.new_terrain:
        terrain_vertices, terrain_indices = controller.generate_terrain(SIZE, SIZE / 10, 60, [0.6, 0.2, 0.2], "esae")
        
        glBindBuffer(GL_ARRAY_BUFFER, terrain_vbo)
        glBufferData(GL_ARRAY_BUFFER, terrain_vertices.nbytes, terrain_vertices, GL_STATIC_DRAW)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, terrain_indices.nbytes, terrain_indices, GL_STATIC_DRAW)
        
        controller.new_terrain = False
        
    if not controller.draw_terrain:
        return

    glDrawElements(GL_TRIANGLES, len(terrain_indices), GL_UNSIGNED_INT, None)
    
        
def draw_curves():
    global terrain_indices
    
    if not controller.draw_curves:
        return
    
    glUseProgram(curves_shader)
    glUniformMatrix4fv(cview_loc, 1, GL_FALSE, camera.view())
    glUniform1i(size_loc, SIZE)
    glUniform1fv(heights_loc, 32, controller.heights)
    glUniform3fv(colors_loc, 32, controller.colors)
    glUniform1i(curves_loc, controller.curves)
    
    glBindVertexArray(terrain_vao)
    glDrawElements(GL_TRIANGLES, len(terrain_indices), GL_UNSIGNED_INT, None)


glClearColor(0.1, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

while not glfw.window_should_close(controller.window) and not controller.should_close():
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    draw_light()
    draw_grid()
    draw_curves()
    draw_terrain()

    controller.update_hud()
    glfw.swap_buffers(controller.window)

glfw.terminate()
