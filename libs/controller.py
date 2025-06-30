import glfw
from OpenGL.GL import *
import pyrr

class Controller:
    def __init__(self, width, height, title, camera):
        self.proj_loc = None
        self.camera = camera

        if not glfw.init():
            exit(1)

        self.window = glfw.create_window(width, height, title, None, None)

        if not self.window:
            glfw.terminate()
            exit(1)

        glfw.set_window_pos(self.window, 400, 200)
        glfw.set_window_size_callback(self.window, self.window_resize)

        glfw.make_context_current(self.window)
    
    def window_resize(self, window, width, height):
        glViewport(0, 0, width, height)
        glUniformMatrix4fv(
            self.proj_loc,
            1, 
            GL_FALSE, 
            pyrr.matrix44.create_perspective_projection_matrix(
                self.camera.fov,
                width / height,
                self.camera.near,
                self.camera.far
            )
        )
