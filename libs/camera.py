import pyrr
import math
import numpy as np

class Camera:
    def __init__(self, r, eye, target, up, fov, near, far, win_width, win_height):
        self.r = r
        
        self.pos = eye
        self.target = target
        self.up = up
        
        self.fov = fov
        self.near = near
        self.far = far
        self.projection = pyrr.matrix44.create_perspective_projection_matrix(fov, win_width/win_height, near, far)
        
        self.xmouse = -1
        self.ymouse = -1
        self.azimuth = math.pi / 4
        self.zenith = math.pi * (3.5 / 12)
        self.horizontal_camera_speed = 0.0065 * r * 2
        self.vertical_camera_speed = 0.008 * r
        self.vertical_cap = 20
        
        self.zoom_speed = 0.05 * r
        self.zoom_in_limit = r * 0.2
        self.zoom_out_limt = r * 4
    
    def update_mouse(self, xpos, ypos):
        xdir = np.sign(xpos - self.xmouse)
        ydir = np.sign(self.ymouse - ypos)
        
        self.azimuth += math.radians(self.horizontal_camera_speed * xdir)
        self.zenith  += math.radians(self.vertical_camera_speed * ydir)
        
        if self.zenith < math.radians(self.vertical_cap):
            self.zenith = math.radians(self.vertical_cap)
        if self.zenith > math.radians(180 - self.vertical_cap):
            self.zenith = math.radians(180 - self.vertical_cap)
        
        self.xmouse = xpos
        self.ymouse = ypos
        
        
    def view(self):
        self.pos = [
            self.r * math.sin(self.azimuth) * math.sin(self.zenith) + self.target[0],
            self.r * math.cos(self.azimuth) * math.sin(self.zenith) + self.target[1], 
            self.r * math.cos(self.zenith) + self.target[2]
        ]
        
        return pyrr.matrix44.create_look_at(self.pos, self.target, self.up)

    def zoom(self, direction):
        self.r += self.zoom_speed * direction
        
        if self.r < self.zoom_in_limit:
            self.r = self.zoom_in_limit
        elif self.r > self.zoom_out_limt:
            self.r = self.zoom_out_limt
