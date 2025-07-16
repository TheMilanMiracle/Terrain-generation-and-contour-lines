import numpy as np
import glfw
from OpenGL.GL import *
import pyrr
from PIL import Image

from libs.utils import * 
from libs.gui import GUI

class Controller:
    def __init__(self, width, height, title, camera, size):
        self.camera = camera
        self.size = size
        self.proj_loc = None
        
        self.close = False
        self.click = False
        self.rclick = False

        if not glfw.init():
            exit(1)

        self.window = glfw.create_window(width, height, title, None, None)

        if not self.window:
            glfw.terminate()
            exit(1)
            
        self.cursors = [
            glfw.create_standard_cursor(glfw.ARROW_CURSOR), 
            glfw.create_standard_cursor(glfw.HAND_CURSOR)
        ] 
        self.cursor_modes = [
            glfw.CURSOR_CAPTURED, 
            glfw.CURSOR_NORMAL
        ] 
            
        glfw.set_window_pos(self.window, 400, 200)
        glfw.set_window_size_callback(self.window, self.window_resize)

        glfw.make_context_current(self.window)
        glfw.swap_interval(3)
        
        self.io_wants_mouse = False
        self.io_wants_keyboard = False
        
        self.gui = GUI(self.window, self, size)
        
        glfw.set_cursor(self.window, self.cursors[int(self.click)])
        glfw.set_input_mode(self.window, glfw.CURSOR, self.cursor_modes[int(self.rclick)])
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)

        self.camera.update_mouse(*glfw.get_cursor_pos(self.window))
        
        img = Image.open("libs/icon.png").convert("RGBA")

        glfw.set_window_icon(self.window, 1, [img])
            
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
    
    def key_callback(self, window, key, scancode, action, mods):
        if self.io_wants_mouse or self.io_wants_keyboard:
            return
    
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            self.close = True
        
    
    def mouse_button_callback(self, window, button, action, mods):
        if self.io_wants_mouse or self.io_wants_keyboard:
            return
        
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            self.click = True
        
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
            self.click = False
        
        if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
            self.rclick = not self.rclick
            glfw.set_input_mode(self.window, glfw.CURSOR, self.cursor_modes[int(self.rclick)])
    
        glfw.set_cursor(self.window, self.cursors[int(self.click)])

    def cursor_pos_callback(self, window, xpos, ypos):
        if self.io_wants_mouse or self.io_wants_keyboard:
            return
        
        if not self.click:
            return

        self.camera.update_mouse(xpos, ypos)
    
    def scroll_callback(self, window, xoffset, yoffset):
        if self.io_wants_mouse or self.io_wants_keyboard:
            return
        
        if yoffset < 0:
            self.camera.zoom(1)
        elif yoffset > 0:
            self.camera.zoom(-1)
    
    def should_close(self):
        return self.close
    
    def gen_sphere(self):
        return gen_sphere(*self.gui.light_position, 1.25, [*self.gui.light_color, self.gui.light_strength])

    def generate_floor(self, size, divisions, color):
        return gen_base_mesh(size, divisions, color)

    def generate_terrain(self, size, mode="perlin"):
        if mode == "perlin":
            v, i = gen_terrain(size)
        else:
            v, i = gen_terrain(size)
        return v, i
    
    def update_hud(self):
        self.io_wants_mouse, self.io_wants_keyboard = self.gui.update()
    
    def set_shaders(self, terrain_shader, curves_shader):
        self.gui.tshader = terrain_shader
        self.gui.cshader = curves_shader
        self.gui.update_perlin_params()
    
        