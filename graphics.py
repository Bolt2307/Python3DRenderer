import pygame
import math
import time
import os
from PIL import Image

# Class definitions
def rotate2D(x,y,r):
    return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)

# Triple tuple representing 3d coordinates, 3d rotation, 3d movement, etc.
class Vector3:
    x, y, z = 0, 0, 0

    def __init__(self, x, y=0, z=0):
        if (type(x) is int) | (type(x) is float):
            self.x, self.y, self.z = x, y, z
        elif type(x) is tuple:
            self.x, self.y, self.z = x[0], x[1], x[2]

    def to_tuple(self):
        return (self.x, self.y, self.z)
    
    # Returns (x1-x2,y1-y2,z1-z2)
    def subtract_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x-v3.x,self.y-v3.y,self.z-v3.z)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1+x2,y1+y2,z1+z2)
    def add_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x+v3.x,self.y+v3.y,self.z+v3.z)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1*x2,y1*y2,z1*z2)
    def multiply_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x*v3.x,self.y*v3.y,self.z*v3.z)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1/x2,y1/y2,z1/z2)
    def divide_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x/v3.x,self.y/v3.y,self.z/v3.z)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1-n,y1-n,z1-n)
    def subtract_by_num(self,num,set_this_vector):
        v = Vector3(self.x-num,self.y-num,self.z-num)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1+n,y1+n,z1+n)
    def add_by_num(self,num,set_this_vector):
        v = Vector3(self.x+num,self.y+num,self.z+num)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1*n,y1*n,z1*n)
    def multiply_by_num(self,num,set_this_vector):
        v = Vector3(self.x*num,self.y*num,self.z*num)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1/n,y1/n,z1/n)
    def divide_by_num(self,num,set_this_vector):
        v = Vector3(self.x/num,self.y/num,self.z/num)
        if set_this_vector:
            self = v
        return v
    
    def rotate_by_euler(self,rotation):
        self.y, self.z = rotate2D(self.y, self.z, rotation.x)
        self.x, self.z = rotate2D(self.x, self.z, rotation.y)
        self.x, self.y = rotate2D(self.x, self.y, rotation.z)

    def __init__(self, x, y=0, z=0):
        if (type(x) is int) | (type(x) is float):
            self.x, self.y, self.z = x, y, z
        elif type(x) is tuple:
            self.x, self.y, self.z = x[0], x[1], x[2]

    def to_tuple(self):
        return (self.x, self.y, self.z)
    
    def magnitude (self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

# Double tuple representing 2d coordinates, 2d rotation, 2d movement, etc.
class Vector2:
    x, y = 0, 0

    def __init__(self, x, y=0):
        if (type(x) is int) | (type(x) is float):
            self.x, self.y = x, y
        elif type(x) is tuple:
            self.x, self.y = x[0], x[1]

    def to_tuple(self):
        return (self.x, self.y)
    
    def magnitude (self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    
class Screen:
    full = 0
    fullwidth = 0

# Represents camera controlled by the cam.velocity
class Camera:
    position = Vector3(0,0,0)
    rotation = Vector3(0,0,0) # x = rotation.y, y = rotation.x, z = roll
    velocity = Vector3(0,0,0)
    drag = 0.8
    air_drag = 0.8
    focal_length = 400

class RGBColor:
    r, g, b = 0, 0, 0

    def __init__(self, r, g=0, b=0):
        if type(r) is int:
            self.r, self.g, self.b = r, g, b
        elif type(r) is tuple:
            self.r, self.g, self.b = r[0], r[1], r[2]

    def to_tuple(self):
        return(self.r, self.g, self.b)

class Face:
    color = RGBColor(0, 0, 0)
    indices = (0,0,0)
    shading_color = (0, 0, 0)
    texture = False

    def __init__(self, indices, color, texture=False):
        self.indices = indices
        self.color = color
        self.texture = texture

class Object:
    static = True
    locked = False

    id = ""
    type = ""
    position = Vector3(0,0,0)
    orientation = Vector3(0, 0, 0)
    origin = Vector3(0, 0, 0)
    scale = Vector3(0, 0, 0)

    wire_thickness = 0
    wire_color = RGBColor(0,0,0)

    visible = True
    transparent = True

    vertices = [] # List of all points as Vector3 
    faces = [] # List of all faces as faces

    light_color = RGBColor(0, 0, 0)
    light_direction = Vector3(0, 0, 0)
    light_spread = 0

    def __init__ (self, id, type, position, orientation, origin, scale, wire_thickness, visible, transparent, static, vertices, faces, light_color, light_direction, light_spread, textures):
        self.id = id
        self.type = type
        self.position = position
        self.orientation = orientation
        self.origin = origin
        self.scale = scale
        self.wire_thickness = wire_thickness
        self.visible = visible
        self.transparent = transparent
        self.static = static
        self.vertices = vertices
        self.faces = faces
        self.light_color = light_color
        self.light_direction = light_direction
        self.light_spread = light_spread
        self.textures = textures

    def set_color (self, color): # Set the entire object to a color
        for face in self.faces:
            face.color = color

def rel_dir (str):
    if (str[0] == "/") | (str[0] == "."):
        return str
    else:
        return os.path.dirname(__file__) + "/" + str

def rotate_point (x, y, r):
  return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)

def shoelace (pts):
    try:
        area = 0
        point = 0
        for point in range(len(pts) - 1):
            area += pts[point][0] * pts[point + 1][1] - pts[point][1] * pts[point + 1][0]
        area += pts[len(pts) - 1][0] * pts[0][1] - pts[len(pts) - 1][1] * pts[0][0]
        return area
    except:
        return 0

def normal (points):
    ab = Vector3(points[1].x - points[0].x, points[1].y - points[0].y, points[1].z - points[0].z)
    ac = Vector3(points[2].x - points[0].x, points[2].y - points[0].y, points[2].z - points[0].z)
    return Vector3(ab.x * ac.x, ab.y * ac.y, ab.z * ac.z)

class find_obj:
        def by_id (id, list):
            for obj in list:
                if obj.id == id:
                    return list.index(obj)
                
        def by_position (pos, list, skip = []):
            for obj in list:
                if (obj.position.to_tuple() == pos.to_tuple()) & (obj.id not in skip):
                    return list.index(obj)
                
def copy_obj (id, new_id, list, new_list):
        obj = list[find_obj.by_id(id)]
        new_list.append(Object(new_id, obj.position, obj.orientation, obj.origin, obj.scale, obj.wire_thickness, obj.visible, obj.transparent, obj.static, obj.vertices, obj.faces))

class Graphics:
    rendered_faces = 0
    rendered_objects = 0
    textures_path = ""
    screen = Screen()
    objects = []
    
    bgcolor = (255, 255, 255)
    specstog = False
    specsHeld = False
    crosshairspread = 0
    speed = 0.025
    ambient_light = (0, 0, 0)

    debug_text_buffer = []

    clock = None
    cam = Camera()
    window = None

    frame = 0
    frame_cap = 60

    def __init__(self,window):
        self.window = window
    
    def apply_changes (self, obj, vertex):
        x, y, z = vertex.x, vertex.y, vertex.z
        # Scaling
        x *= obj.scale.x
        y *= obj.scale.y
        z *= obj.scale.z

        # Rotation
        y, z = rotate_point(y - obj.origin.y, z - obj.origin.z, math.radians(obj.orientation.x))
        x, z = rotate_point(x - obj.origin.x, z - obj.origin.z, math.radians(obj.orientation.y))
        x, y = rotate_point(x - obj.origin.x, y - obj.origin.y, math.radians(obj.orientation.z))
        
        # Offset
        x += obj.position.x
        y += obj.position.y
        z += obj.position.z

        return Vector3(x, y, z)
    
    def perspective (self, position, rotation, vertex):
        x, y, z = vertex.x - position.x, vertex.y - position.y, vertex.z - position.z
        pitch, yaw, roll = math.radians(rotation.x), math.radians(rotation.y), math.radians(rotation.z)
        x, z = rotate_point(x, z, yaw)
        y, z = rotate_point(y, z, pitch)
        x, y = rotate_point(x, y, roll)
        return Vector3(x, y, z)
    
    def draw_texture (self, facepts, texture, scrn, shading=(1, 1, 1)):
        facepts.sort(key=lambda x: x[1])
        top = [facepts[0], facepts[1]]
        bottom = [facepts[2], facepts[3]]
        top.sort(key=lambda x: x[0])
        bottom.sort(key=lambda x: x[0])
        facepts = [top[0], top[1], bottom[0], bottom[1]]
        image = Image.open(texture, "r")
        texture = list(image.getdata())
        for y in range(image.height): # *Interpolation Magic Below*
            for x in range(image.width):
                topcoord1 = (facepts[0][0] + (x/image.width*(facepts[1][0] - facepts[0][0])), facepts[0][1] + (x/image.width*(facepts[1][1] - facepts[0][1])))
                topcoord2 = (facepts[0][0] + ((x + 1)/image.width*(facepts[1][0] - facepts[0][0])), facepts[0][1] + ((x + 1)/image.width*(facepts[1][1] - facepts[0][1])))
                bottomcoord1 = (facepts[2][0] + (x/image.width*(facepts[3][0] - facepts[2][0])), facepts[2][1] + (x/image.width*(facepts[3][1] - facepts[2][1])))
                bottomcoord2 = (facepts[2][0] + ((x + 1)/image.width*(facepts[3][0] - facepts[2][0])), facepts[2][1] + ((x + 1)/image.width*(facepts[3][1] - facepts[2][1])))
                tl = (topcoord1[0] + (y/image.height*(bottomcoord1[0] - topcoord1[0])), topcoord1[1] + (y/image.height*(bottomcoord1[1] - topcoord1[1])))
                tr = (topcoord2[0] + (y/image.height*(bottomcoord2[0] - topcoord2[0])), topcoord2[1] + (y/image.height*(bottomcoord2[1] - topcoord2[1])))
                bl = (topcoord1[0] + ((y + 1)/image.height*(bottomcoord1[0] - topcoord1[0])), topcoord1[1] + ((y + 1)/image.height*(bottomcoord1[1] - topcoord1[1])))
                br = (topcoord2[0] + ((y + 1)/image.height*(bottomcoord2[0] - topcoord2[0])), topcoord2[1] + ((y + 1)/image.height*(bottomcoord2[1] - topcoord2[1])))
                pts = [tl, tr, br, bl]
                pixcolor = (texture[y * image.width + x][0], texture[y * image.width + x][1], texture[y * image.width + x][2])
                r = pixcolor[0]*shading[0]
                g = pixcolor[1]*shading[1]
                b = pixcolor[2]*shading[2]
                if r > 255: r = 255
                if g > 255: g = 255
                if b > 255: b = 255
                pygame.draw.polygon(scrn, (r, g, b), pts, 0)

    def bake_lighting (self):
        for obj in self.objects:
            for face in obj.faces:
                    face.shading_color = (self.ambient_light.r/255, self.ambient_light.g/255, self.ambient_light.b/255)
        for light in self.objects:
            if light.type == "light":
                list = self.objects
                for obj in list:
                    if obj.visible & (obj.type != "light"):
                        vertices = []
                        for vertex in obj.vertices:
                            x, y, z = vertex.x, vertex.y, vertex.z
                            if not obj.locked:

                                vert = self.apply_changes(obj, vertex)
                                x, y, z = vert.x, vert.y, vert.z

                            vertices.append(self.perspective(light.position, light.light_direction, Vector3(x, y, z)))

                        for face in obj.faces:
                            offscreen = True
                            show = True
                            points = []
                            planepts = []
                            for index in face.indices:
                                x, y, z = vertices[index].x, vertices[index].y, vertices[index].z
                                if z < 0:
                                    show = False
                                points.append(((x * light.light_spread/z), (-y * light.light_spread/z)))
                                if (x * light.light_spread/z <= self.window.get_width()) & (y * light.light_spread/z <= self.window.get_height()):
                                    offscreen = False
                                planepts.append(Vector3(x, y, z))

                            area = shoelace(points)
                            if (area > 0) & (show & (not offscreen)):
                                dist_from_center = math.sqrt(points[0][0] * points[0][0] + points[0][1] * points[0][1])
                                distance = math.sqrt((light.position.x - planepts[0].x)*(light.position.x - planepts[0].x) + (light.position.y - planepts[0].y)*(light.position.y - planepts[0].y) + (light.position.z - planepts[0].z)*(light.position.z - planepts[0].z))
                                if dist_from_center == 0:
                                    brightness = area / distance / 999
                                else:
                                    brightness = area / distance / 10 / dist_from_center
                                r = face.shading_color[0] + (light.light_color.r/255) * brightness
                                g = face.shading_color[1] + (light.light_color.g/255) * brightness
                                b = face.shading_color[2] + (light.light_color.b/255) * brightness
                                face.shading_color = (r, g, b)

    def get_rendered_objects(self):
        return self.rendered_objects
    
    def get_rendered_faces(self):
        return self.rendered_faces

    def render(self):
        t0 = time.perf_counter_ns()
        self.bake_lighting()
        objlist = self.objects
        self.window.fill(self.bgcolor)
        zbuffer = []

        self.rendered_objects = 0
        for obj in objlist:
            cam = self.cam
            if obj.visible:
                self.rendered_objects += 1
                locked = obj.locked
                vertices = []
                for vertex in obj.vertices:
                    x, y, z = vertex.x, vertex.y, vertex.z
                    if not locked:

                        vert = self.apply_changes(obj, vertex)
                        x, y, z = vert.x, vert.y, vert.z

                        # Lock Vertices For Static Objects
                        if obj.static:
                            obj.vertices[obj.vertices.index(vertex)] = Vector3(x, y, z)
                            obj.locked = True

                    vertices.append(self.perspective(cam.position, cam.rotation, Vector3(x, y, z)))

                self.rendered_faces = 0
                for face in obj.faces:
                    show = True
                    points = []
                    depthval = 0
                    planepts = []
                    for index in face.indices:
                        x, y, z = vertices[index].x, vertices[index].y, vertices[index].z
                        
                        if z < 0: # Do not render clipping or out-of-scope objects
                            show = False
                            break
                        points.append(((x * cam.focal_length/z+self.window.get_width()/2) * (self.window.get_width() / self.screen.fullwidth), (-y * cam.focal_length/z+self.window.get_height()/2)*(self.window.get_height() / self.screen.full)))
                        planepts.append(Vector3(x, y, z))
                        
                        depthval += z # add z to the sum of the z values

                    if len(obj.textures) > 0:
                        texture = self.textures_path + obj.textures[face.texture]
                    else:
                        texture = False

                    depthval /= len(face.indices) # depthval now stores the z of the object's center
                    if show:
                        self.rendered_faces += 1
                    if show & ((shoelace(points) > 0) | obj.transparent):
                        zbuffer.append([face.color, points, obj.wire_thickness, depthval, face.shading_color, obj.type, texture, obj.transparent])

        zbuffer.sort(key=lambda x: x[3], reverse=True) # Sort z buffer by the z distance from the camera

        for f in zbuffer: # Draw each face
            shading = f[4]
            shading = list(shading)
            if shading[0] > 1.3: shading[0] = 1.3
            if shading[1] > 1.3: shading[1] = 1.3
            if shading[2] > 1.3: shading[2] = 1.3
            shading = tuple(shading)
            if (not f[7]) | (f[6] == False):
                if f[5] == "light":
                    r, g, b = (f[0].r, f[0].g, f[0].b)
                else:
                    r = int(f[0].r*shading[0])
                    g = int(f[0].g*shading[1])
                    b = int(f[0].b*shading[2])
                    if r > 255: r = 255
                    if g > 255: g = 255
                    if b > 255: b = 255
                try:
                    pygame.draw.polygon(self.window, (r, g, b), f[1], f[2])
                except:
                    pygame.draw.polygon(self.window, f[0].to_tuple(), f[1], f[2])
            if f[6] != False:
                if len(f[1]) >= 4:
                    if f[5] == "light":
                        self.draw_texture(f[1], f[6], self.window)
                    else:
                        self.draw_texture(f[1], f[6], self.window, f[4])
        index = 0
        for text in self.debug_text_buffer:
            self.window.blit(text,(5,index * 20))
            index += 1
        self.debug_text_buffer = []
        
        return time.perf_counter_ns() - t0
    
    # Print string to the debug
    def debug_log(self,string,font):
        text = font.render(string,False,(0,0,0),(255,255,255))
        self.debug_text_buffer.append(text)

                
    def gui(self):
        t0 = time.perf_counter_ns()
        crosshairspread = self.speed * 100
        
        #crosshairs
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2-10-crosshairspread, self.window.get_height()/2), (self.window.get_width()/2-crosshairspread, self.window.get_height()/2)) #horizontal left
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2+crosshairspread, self.window.get_height()/2), (self.window.get_width()/2+10+crosshairspread, self.window.get_height()/2)) #horizontal right
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2, self.window.get_height()/2-10-crosshairspread), (self.window.get_width()/2, self.window.get_height()/2-crosshairspread)) #vertical top
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2, self.window.get_height()/2+crosshairspread), (self.window.get_width()/2, self.window.get_height()/2+10+crosshairspread)) #vertical vertical bottom
        
        if self.specstog: # Show spects
            pass
        return time.perf_counter_ns()-t0
