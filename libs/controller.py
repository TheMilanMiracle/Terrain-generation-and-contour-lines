import numpy as np
import glfw
from OpenGL.GL import *
import pyrr
import imgui
from imgui.integrations.glfw import GlfwRenderer

from libs.utils import * 

class Controller:
    def __init__(self, width, height, title, camera):
        self.camera = camera
        self.proj_loc = None
        
        self.close = False
        self.click = False
        self.rclick = False
        
        self.light_position = [0.0, 0.0, 50.0]
        self.light_speed = 2.5
        self.light_color = [0.8, 0.8, 0.4]
        self.new_light_pos = True
        
        self.new_terrain = False
        
        self.max_h, self.min_h, self.avg_h = 0.0, 0.0, 0.0
        self.heights = np.zeros(32, dtype=np.float32)
        self.colors = np.zeros((32, 3), dtype=np.float32)
        self.curves  = 0

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
        
        imgui.create_context()
        imgui.style_colors_dark()
        imgui.set_next_window_size(800, 400)
        
        self.renderer = GlfwRenderer(self.window, False)
        self.input_text = ""
        self.color_picked = [0.0, 0.0, 0.0]
        self.draw_light_src = True
        self.draw_curves = True
        self.draw_terrain = True
        
        self.io_wants_mouse = False
        self.io_wants_keyboard = False
        
        glfw.set_key_callback(self.window, self.renderer.keyboard_callback)
        glfw.set_char_callback(self.window, self.renderer.char_callback)
        glfw.set_mouse_button_callback(self.window, self.renderer.mouse_callback)
        
        glfw.set_cursor(self.window, self.cursors[int(self.click)])
        glfw.set_input_mode(self.window, glfw.CURSOR, self.cursor_modes[int(self.rclick)])
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)

        self.camera.update_mouse(*glfw.get_cursor_pos(self.window))
    
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
        
        if key == glfw.KEY_SPACE and action == glfw.PRESS:
            self.new_terrain = True
        
        if key == glfw.KEY_UP and action == glfw.PRESS:
            self.light_position[2] += self.light_speed
            self.new_light_pos = True
        
        if key == glfw.KEY_DOWN and action == glfw.PRESS:
            self.light_position[2] -= self.light_speed
            self.new_light_pos = True
    
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
        return gen_sphere(*self.light_position, 1.5, self.light_color)

    def generate_floor(self, size, divisions, color):
        return gen_base_mesh(size, divisions, color)

    def generate_terrain(self, size, height, scale, color, mode="perlin"):
        if mode == "perlin":
            v, i, self.max_h, self.min_h, self.avg_h = gen_terrain(size, height, scale, color, pnoise_heights)
        else:
            v, i, self.max_h, self.min_h, self.avg_h = gen_terrain(size, height, scale, color, diamond_square)
        return v, i
    
    def update_hud(self):
        self.renderer.process_inputs()

        imgui.new_frame()
        io = imgui.get_io()
        w, h = io.display_size

        imgui.set_next_window_position(w * 0.26, h * 0.355, imgui.ALWAYS, pivot_x=1.0, pivot_y=1.0)
        if imgui.begin("Simulation settings", flags = imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE):
            changed, self.input_text = imgui.input_text("curve height", self.input_text, 256)
            
            changed, self.color_picked = imgui.color_edit3(
                "curve color",
                *self.color_picked,
            )
            
            imgui.dummy(1, 5)
            
            if imgui.core.button("add new curve"):
                try:
                    self.heights[self.curves] = float(self.input_text)
                    self.colors[self.curves]   = self.color_picked
                    self.curves += 1
                
                    # print(self.heights[0:self.curves], self.colors[0:self.curves], self.curves)
                except:
                    pass
                
                self.input_text = ""
            
            imgui.same_line()
            
            if imgui.core.button("clear curves"):
                self.heights = np.zeros(len(self.heights))
                self.curves = 0

            imgui.dummy(1, 15)
            
            imgui.text("draw")
            
            changed, self.draw_light_src = imgui.checkbox(
                "light source", self.draw_light_src
            )
            imgui.same_line()
            changed, self.draw_curves = imgui.checkbox(
                "curves", self.draw_curves
            )
            imgui.same_line()
            changed, self.draw_terrain = imgui.checkbox(
                "terrain", self.draw_terrain
            )
            
            imgui.dummy(1, 15)
            imgui.text("generate new terrain")
            
            if imgui.core.button("with perlin noise"):
                pass
            imgui.same_line()
            if imgui.core.button("wind diamond-square"):
                pass
            
            imgui.dummy(1, 5)
            
            imgui.end()
        
        imgui.set_next_window_position(w * 0.99, h *0.05, imgui.ALWAYS, pivot_x=1.0, pivot_y=1.0)
        flags = imgui.WINDOW_NO_TITLE_BAR     | imgui.WINDOW_NO_RESIZE \
            | imgui.WINDOW_NO_MOVE          | imgui.WINDOW_NO_SCROLLBAR \
            | imgui.WINDOW_NO_BACKGROUND    | imgui.WINDOW_NO_INPUTS
            
        imgui.begin("fps", flags=flags)
        imgui.text(f"FPS: {io.framerate:.2f}")
        imgui.end()
        
        imgui.set_next_window_size(350, 20)
        imgui.set_next_window_position(w * 0.99, h * 0.99, imgui.ALWAYS, pivot_x=1.0, pivot_y=1.0)
        imgui.begin("info", flags=flags)
        imgui.text(f"height in [{round(self.min_h, 3)}, {round(self.max_h, 3)}] | avg height: {round(self.avg_h, 3)}")
        imgui.end()
        
        imgui.render()
        self.renderer.render(imgui.get_draw_data())
        
        self.io_wants_mouse = imgui.get_io().want_capture_mouse
        self.io_wants_keyboard = imgui.get_io().want_capture_keyboard