from imgui.integrations.glfw import GlfwRenderer
import imgui
import glfw
from OpenGL.GL import *
import random
import numpy as np

class GUI:
    def __init__(self, window, size):
        imgui.create_context()
        self.renderer = GlfwRenderer(window, False)
        imgui.style_colors_dark()
        
        glfw.set_key_callback(window, self.renderer.keyboard_callback)
        glfw.set_char_callback(window, self.renderer.char_callback)
        glfw.set_mouse_button_callback(window, self.renderer.mouse_callback)
        
        self.heights = np.zeros(32, dtype=np.float32)
        self.colors = np.zeros((32, 3), dtype=np.float32)
        self.curves  = 0
        
        self.input_text = ""
        self.color_picked = [0.0, 0.0, 0.0]
        self.draw_light_src = True
        self.draw_curves = True
        self.draw_terrain = True
        
        self.tshader     = None
        self.cshader     = None
        self.zoom        = 1.25
        self.octaves     = 6
        self.persistance = 0.8
        self.lacunarity  = 2.0
        self.height_offset = 20.0
        self.plane_offset = [size, size]
        self.scale = 5
        self.seed = 23
        
        self.light_position = [0.0, 0.0, self.height_offset + 20]
        self.light_speed = 10
        self.light_color = [0.8, 0.8, 0.4]
        self.light_strength = 0.3
        self.new_light_pos = True
        
    def simulation_settings(self):
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
                    self.update_curves_params()
                    
                except:
                    pass
                
                self.input_text = ""
            
            imgui.same_line()
            
            if imgui.core.button("clear curves"):
                self.heights = np.zeros(len(self.heights))
                self.curves = 0
                self.update_curves_params()

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
            
            if imgui.core.button("new terrain"):
                self.seed = random.randint(0, 10000)
                self.update_perlin_params()
            
            imgui.dummy(1, 5)
            
            imgui.text("scale:")
            imgui.same_line()
            if imgui.core.button("-##scale"):
                self.scale = max(self.scale - 1.5, 0.0)
                self.update_perlin_params()
            imgui.same_line()
            if imgui.core.button("+##scale"):
                self.scale += 1.5
                self.update_perlin_params()
            
            
            imgui.text("octaves:")
            imgui.same_line()
            if imgui.core.button("-##octaves"):
                self.octaves = max(self.octaves - 1, 1)
                self.update_perlin_params()
            imgui.same_line()
            if imgui.core.button("+##octaves"):
                self.octaves += 1
                self.update_perlin_params()

            imgui.dummy(1, 5)
            imgui.text("light_position:")
            imgui.same_line()
            if imgui.core.button("-x##light_position"):
                self.light_position[0] -= 5
                self.new_light_pos = True
            imgui.same_line()
            if imgui.core.button("+x##light_position"):
                self.light_position[0] += 5
                self.new_light_pos = True
            imgui.same_line()
            if imgui.core.button("-y##light_position"):
                self.light_position[1] -= 5
                self.new_light_pos = True
            imgui.same_line()
            if imgui.core.button("+y##light_position"):
                self.light_position[1] += 5
                self.new_light_pos = True
            imgui.same_line()
            if imgui.core.button("-z##light_position"):
                self.light_position[2] -= 5
                self.new_light_pos = True
            imgui.same_line()
            if imgui.core.button("+z##light_position"):
                self.light_position[2] += 5
                self.new_light_pos = True
                
            changed, self.light_color = imgui.color_edit3(
                "light_color",
                *self.light_color,
            )
            
            if changed:
                self.new_light_pos = True
            
            changed, self.light_strength = imgui.slider_float(
                "light strength", self.light_strength, 0.0, 1.0, "Value: %.3f"
            )
                        
            imgui.end()
        
    def fps(self):
        w, h = imgui.get_io().display_size
        imgui.set_next_window_position(w * 0.99, h *0.05, imgui.ALWAYS, pivot_x=1.0, pivot_y=1.0)
        flags = imgui.WINDOW_NO_TITLE_BAR     | imgui.WINDOW_NO_RESIZE \
            | imgui.WINDOW_NO_MOVE          | imgui.WINDOW_NO_SCROLLBAR \
            | imgui.WINDOW_NO_BACKGROUND    | imgui.WINDOW_NO_INPUTS
            
        imgui.begin("fps", flags=flags)
        imgui.text(f"FPS: {imgui.get_io().framerate:.2f}")
        imgui.end()
    
    def info(self):
        w, h = imgui.get_io().display_size
        imgui.set_next_window_position(w * 0.99, h *0.05, imgui.ALWAYS, pivot_x=1.0, pivot_y=1.0)
        flags = imgui.WINDOW_NO_TITLE_BAR     | imgui.WINDOW_NO_RESIZE \
            | imgui.WINDOW_NO_MOVE          | imgui.WINDOW_NO_SCROLLBAR \
            | imgui.WINDOW_NO_BACKGROUND    | imgui.WINDOW_NO_INPUTS
            
        imgui.set_next_window_size(200, 20)
        imgui.set_next_window_position(w * 0.99, h * 0.99, imgui.ALWAYS, pivot_x=1.0, pivot_y=1.0)
        imgui.begin("info", flags=flags)
        imgui.text(f"heights are around {self.height_offset}")
        imgui.end()
    
    def update(self):
        
        self.renderer.process_inputs()
        imgui.new_frame()
        
        self.simulation_settings()
        self.fps()
        self.info()
        
        imgui.render()
        self.renderer.render(imgui.get_draw_data())
        
        self.update_light_params()
        
        return imgui.get_io().want_capture_mouse ,imgui.get_io().want_capture_keyboard

    def update_perlin_params(self):
        print(self.octaves)
        for shader in [self.tshader, self.cshader]:
            glUseProgram(shader)
            glUniform1f(glGetUniformLocation(shader, "u_zoom"), self.zoom)
            glUniform1i(glGetUniformLocation(shader, "u_octaves"), self.octaves)
            glUniform1f(glGetUniformLocation(shader, "u_persistence"), self.persistance)
            glUniform1f(glGetUniformLocation(shader, "u_lacunarity"), self.lacunarity)
            glUniform1f(glGetUniformLocation(shader, "u_height_offset"), self.height_offset)
            glUniform2fv(glGetUniformLocation(shader, "u_plane_offset"), 1, self.plane_offset)
            glUniform1f(glGetUniformLocation(shader, "u_scale"), self.scale)
            glUniform1i(glGetUniformLocation(shader, "u_seed"), self.seed)
    
    def update_light_params(self):
        glUseProgram(self.tshader)
        glUniform3fv(glGetUniformLocation(self.tshader, "u_light_position"), 1, self.light_position)
        glUniform3fv(glGetUniformLocation(self.tshader, "u_light_color"), 1, self.light_color)
        glUniform1f(glGetUniformLocation(self.tshader, "u_light_strength"), self.light_strength)
    
    def update_curves_params(self):
        glUseProgram(self.cshader)
        glUniform1fv(glGetUniformLocation(self.cshader, "heights"), 32, self.heights)
        glUniform3fv(glGetUniformLocation(self.cshader, "colors"), 32, self.colors)
        glUniform1i(glGetUniformLocation(self.cshader, "curves"), self.curves)