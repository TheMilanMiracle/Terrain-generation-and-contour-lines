import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr
import os

from libs.utils import *
from libs.controller import Controller
from libs.camera import Camera

WINDOW_DIMENSIONS = (1280, 720)
WINDOW_TITLE = "t3"
# SIZE = 16_384
SIZE = 128

camera = Camera([-SIZE, -SIZE, 5.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], 70, 0.1, 10000, *WINDOW_DIMENSIONS)
controller = Controller(*WINDOW_DIMENSIONS, WINDOW_TITLE, camera)

base_vertices, base_indices = gen_base_mesh(SIZE + 1, 20, [0.2, 0.5, 0.5])
terrain_vertices, terrain_indices = gen_terrain(SIZE, 15, 30, [0.6, 0.2, 0.2])

base_vertices = np.array(base_vertices, dtype=np.float32)
base_indices = np.array(base_indices, dtype=np.uint32)
terrain_vertices = np.array(terrain_vertices, dtype=np.float32)
terrain_indices = np.array(terrain_indices, dtype=np.uint32)

shader = compileProgram(
    compileShader(load_shader(os.path.join("shaders", "shader.vert")), GL_VERTEX_SHADER), 
    compileShader(load_shader(os.path.join("shaders", "shader.frag")), GL_FRAGMENT_SHADER)
)

# base vao
base_vao = glGenVertexArrays(1)
glBindVertexArray(base_vao)

# base vertices
base_vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, base_vbo)
glBufferData(GL_ARRAY_BUFFER, base_vertices.nbytes, base_vertices, GL_STATIC_DRAW)

# base indices
base_ebo = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, base_ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, base_indices.nbytes, base_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, base_vertices.itemsize * 6, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, base_vertices.itemsize * 6, ctypes.c_void_p(12))

# terrain vao
terrain_vao = glGenVertexArrays(1)
glBindVertexArray(terrain_vao)

# terrain points
terrain_vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, terrain_vbo)
glBufferData(GL_ARRAY_BUFFER, terrain_vertices.nbytes, terrain_vertices, GL_STATIC_DRAW)

for i in range(12):
    print(terrain_vertices[3 * i], terrain_vertices[3 * i +1], terrain_vertices[3 * i + 2])
# terrain indices
terrain_ebo = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, terrain_ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, terrain_indices.nbytes, terrain_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, terrain_indices.itemsize * 9, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, terrain_indices.itemsize * 9, ctypes.c_void_p(12))

glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, terrain_indices.itemsize * 9, ctypes.c_void_p(24))

glUseProgram(shader)
glClearColor(0.1, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)

translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, camera.projection)
glUniformMatrix4fv(model_loc, 1, GL_FALSE, translation)

controller.proj_loc = proj_loc
while not glfw.window_should_close(controller.window):
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUniformMatrix4fv(view_loc, 1, GL_FALSE, camera.view())

    glBindVertexArray(base_vao)
    glDrawElements(GL_LINES, len(base_indices), GL_UNSIGNED_INT, None)
    
    glBindVertexArray(terrain_vao)
    glDrawElements(GL_TRIANGLES, len(terrain_indices), GL_UNSIGNED_INT, None)

    glfw.swap_buffers(controller.window)

glfw.terminate()
