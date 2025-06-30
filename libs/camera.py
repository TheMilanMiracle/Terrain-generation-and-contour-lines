import pyrr
import math
import glfw

class Camera:
    def __init__(self, eye, target, up, fov, near, far, win_width, win_height):
        self.pos = eye
        self.target = target
        self.up = up
        
        self.fov = fov
        self.near = near
        self.far = far
        self.projection = pyrr.matrix44.create_perspective_projection_matrix(fov, win_width/win_height, near, far)
    
    def view(self):
        self.pos = [2000 * math.cos(glfw.get_time() / 2), 2000 * math.sin(glfw.get_time() / 2), 600]
        return pyrr.matrix44.create_look_at(self.pos, self.target, self.up)