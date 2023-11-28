from typing import Self
import pygame
import math
import time
import json
import os

# Class definitions

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
    
class Screen:
    fullheight = 0
    fullwidth = 0

# Represents camera controlled by the cam.velocity
class Camera:
    position = Vector3(0,0,0)
    rotation = Vector3(0,0,0) # x = rotation.y, y = rotation.x, z = roll
    velocity = Vector3(0,0,0)
    height = 0
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

    def __init__(self, indices, color):
        self.indices = indices
        self.color = color

class Object:
    static = True
    locked = False

    id = ""
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

    def __init__ (self, id, position, orientation, origin, scale, wire_thickness, visible, transparent, static, vertices, faces):
        self.id = id
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

class Graphics:
    active = True

    screen = Screen()
    objects = []

    bgcolor = (255, 255, 255)
    specstog = False
    specsHeld = False
    paused = False
    pauseHeld = False
    crosshairspread = 0
    speed = 0.025

    analytics_font = None
    clock = None
    cam = Camera()
    window = None

    frame = 0
    frame_cap = 1000

    def __init__(self):
        self.bgcolor = (255, 255, 255)
        self.specstog = False
        self.specsHeld = False
        self.paused = False
        self.pauseHeld = False
        self.crosshairspread = 0
        self.speed = 0.025

        pygame.init()
        pygame.font.init()
        self.analytics_font = pygame.font.SysFont('cousine', 20)
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen.fullwidth, self.screen.fullheight = self.window.get_width(), self.window.get_height() #finds fullscreen dimensions
        self.window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Python (Pygame) - 3D Renderer')
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        pygame.mouse.set_visible(False)

        self.objects = self.compile(self.load_objects(rel_dir("scene_path.json")))
    
    # Load scene JSON as objects
    def load_objects (self,path):
        objlist = []
        with open(path) as file:
            scene = json.load(file)
            self.bgcolor = tuple(scene["bg_color"])
            folder_path = rel_dir(scene["folder_path"])
        file.close()
        for objpath in scene["object_file_paths"]:
            with open(folder_path + objpath) as file:
                obj = json.load(file)
                vertices = []
                for vertex in obj["vertices"]:
                    vertices.append(Vector3(tuple(vertex)))
                faces = []
                for face in obj["faces"]:
                    faces.append(Face((tuple(face[0])), RGBColor(tuple(face[1]))))
                objlist.append(Object(obj["name"], Vector3(tuple(obj["position"])), Vector3(tuple(obj["orientation"])), Vector3(tuple(obj["origin"])), Vector3(tuple(obj["scale"])), obj["wire_thickness"], obj["visible"], obj["transparent"], obj["static"], vertices, faces))
            file.close()
        return objlist

    # Precompiling faces
    def compile(self,objects):
        objlist = objects
        for obj in objlist:
            for face in obj.faces:
                face.indices = list(face.indices)
                for index in range(len(face.indices)):
                    face.indices[index] = obj.vertices[face.indices[index]]
        return objlist
    
    def render(self):
        list = self.objects
        self.window.fill(self.bgcolor)
        t0 = time.perf_counter_ns()
        zbuffer = []

        for obj in list:
            cam = self.cam
            screen = self.screen

            if obj.visible:
                locked = obj.locked
                for face in obj.faces:
                    show = True # The object will be rendered unless one of its vertices is out-of-scope
                    points = []
                    depthval = 0
                    for vertex in face.indices:
                        x, y, z = vertex.x, vertex.y, vertex.z
                        if not locked:
                            # Scaling
                            x *= obj.scale.x
                            y *= obj.scale.y
                            z *= obj.scale.z

                            # Rotation
                            x, z = rotate_point(x - obj.origin.x, z - obj.origin.z, math.radians(obj.orientation.y))
                            y, z = rotate_point(y - obj.origin.y, z - obj.origin.z, math.radians(obj.orientation.x))
                            x, y = rotate_point(x - obj.origin.x, y - obj.origin.y, math.radians(obj.orientation.z))
                            
                            # Offset
                            x += obj.position.x
                            y += obj.position.y
                            z += obj.position.z

                            # Lock Vertices For Static Objects
                            if obj.static:
                                face.indices[face.indices.index(vertex)] = Vector3(x, y, z)
                                obj.locked = True

                        # Rotation relative to camera
                        x, y, z = x - cam.position.x, y - cam.position.y - cam.height, z - cam.position.z
                        pitch, yaw, roll = math.radians(cam.rotation.x), math.radians(cam.rotation.y), math.radians(cam.rotation.z)
                        x, z = rotate_point(x, z, yaw)
                        y, z = rotate_point(y, z, pitch)
                        x, y = rotate_point(x, y, roll)

                        if z < 0: # Do not render clipping or out-of-scope objects
                            show = False
                            break

                        points.append(((x * cam.focal_length/z+self.window.get_width()/2) * (self.window.get_width() / self.screen.fullwidth), (-y * cam.focal_length/z+self.window.get_height()/2)*(self.window.get_height() / self.screen.fullheight)))
                        
                        depthval += z # add z to the sum of the z values

                    depthval /= len(face.indices) # depthval now stores the z of the object's center
                    if show & ((shoelace(points) > 0) | obj.transparent):
                        zbuffer.append([face.color.to_tuple(), points, obj.wire_thickness, depthval]) # Store the info in zbuffer

        zbuffer.sort(key=lambda x: x[3], reverse=True) # Sort z buffer by the z distance from the camera

        for f in zbuffer: # Draw each face
            pygame.draw.polygon(self.window, f[0], f[1], f[2])

        return time.perf_counter_ns() - t0
                
    def gui(self):
        t0 = time.perf_counter_ns()
        crosshairspread = self.speed * 100
        
        #crosshairs
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2-10-crosshairspread, self.window.get_height()/2), (self.window.get_width()/2-crosshairspread, self.window.get_height()/2)) #horizontal left
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2+crosshairspread, self.window.get_height()/2), (self.window.get_width()/2+10+crosshairspread, self.window.get_height()/2)) #horizontal right
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2, self.window.get_height()/2-10-crosshairspread), (self.window.get_width()/2, self.window.get_height()/2-crosshairspread)) #vertical top
        pygame.draw.line(self.window, 'red', (self.window.get_width()/2, self.window.get_height()/2+crosshairspread), (self.window.get_width()/2, self.window.get_height()/2+10+crosshairspread)) #vertical vertical bottom

        if self.paused: # Show pause menu
            pausetext = self.analytics_font.render('PAUSED', False, (200, 0, 0))
            self.window.blit(pausetext, (self.window.get_width()/2, 0))
        
        if self.specstog: # Show spects
            print('placeholder')
        return time.perf_counter_ns()-t0

    def handle_control(self):
        t0 = time.perf_counter_ns()
        keys = pygame.key.get_pressed()

        #rotation
        rel = pygame.mouse.get_rel()

        if not self.paused: # When unpaused
            cam = self.cam
            cam.rotation.y += rel[0]*0.15
            cam.rotation.x -= rel[1]*0.15 #mouse sense
            
            speed = self.speed
            #movement
            if keys[pygame.K_LSHIFT]: #sprinting
                if speed < 0.1:
                    speed += 0.01
                if cam.focal_length > 300:
                    cam.focal_length -= 10
            else:
                if speed > 0.025:
                    speed -= 0.005
                if cam.focal_length < 400:
                    cam.focal_length += 10
            if keys[pygame.K_w]:
                cam.velocity.z += speed*math.cos(math.radians(cam.rotation.y))
                cam.velocity.x += speed*math.sin(math.radians(cam.rotation.y))
            if keys[pygame.K_s]:
                cam.velocity.z -= speed*math.cos(math.radians(cam.rotation.y))
                cam.velocity.x -= speed*math.sin(math.radians(cam.rotation.y))
            if keys[pygame.K_a]:
                cam.velocity.z -= speed*math.cos(math.radians(cam.rotation.y+90))
                cam.velocity.x -= speed*math.sin(math.radians(cam.rotation.y+90))
            if keys[pygame.K_d]:
                cam.velocity.z += speed*math.cos(math.radians(cam.rotation.y+90))
                cam.velocity.x += speed*math.sin(math.radians(cam.rotation.y+90))
            if keys[pygame.K_SPACE]:
                if cam.position.y <= 0:
                    cam.velocity.y += 1
            if keys[pygame.K_LCTRL]:
                if cam.height > -1:
                    cam.height -= 0.2
            else:
                if cam.height < 0:
                    cam.height += 0.2
        else: # In pause menu
            if keys[pygame.K_e]: #exits the game if e is pressed in pause
                self.active = False

            if keys[pygame.K_f]:
                if not specsHeld:
                    specstog = not specstog
                    specsHeld = True
            else:
                specsHeld = False

        if keys[pygame.K_ESCAPE]:
            if (not self.paused) & (not self.pauseHeld): # Pause handling
                self.pauseHeld = True
                self.paused = True
                pygame.mouse.set_visible(True)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif self.paused & (not self.pauseHeld):
                self.pauseHeld = True
                self.paused = False
                pygame.mouse.set_visible(False)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        else:
            pauseHeld = False

        return time.perf_counter_ns() - t0

    def update(self):
        t0 = time.perf_counter_ns()
        if not self.paused:
            pygame.mouse.set_pos(self.window.get_width()/2, self.window.get_height()/2) #mouse "lock"
            # Change position by velocity and apply drag to velocity
            self.cam.position.x, self.cam.position.y, self.cam.position.z = self.cam.position.x + self.cam.velocity.x, self.cam.position.y + self.cam.velocity.y, self.cam.position.z + self.cam.velocity.z
            self.cam.velocity.x, self.cam.velocity.y, self.cam.velocity.z = self.cam.velocity.x * 0.85, self.cam.velocity.y * 0.85, self.cam.velocity.z * 0.85
            if self.cam.position.y > 0: # Apply Gravity
                self.cam.velocity.y -= 0.02
            else:
                self.cam.velocity.y = 0
                self.cam.position.y = 0
        return time.perf_counter_ns() - t0
    
    log_position = 0
    def log_text(self,text,font):
        text_holder = font.render(text,False,(0,0,0))
        self.screen.blit(text_holder, (5,self.log_position))
        self.log_position += 20

# Eventually put this in the engine
g = Graphics()

time_elapsed = 0
last_timestamp = time.perf_counter()
tick = 0
while g.active:
    current_timestamp = time.perf_counter()
    time_elapsed += current_timestamp - last_timestamp # Add change in time to the time_elapsed
    last_timestamp = current_timestamp
    if time_elapsed > 1 / g.frame_cap: # Do not update unless enough time has passed
        g.frame += 1

        # Handle events
        for gevent in pygame.event.get():
            pass
        
        # Print elapsed time ever n frames
        if g.frame % 60 == 0:
            # Take user input
            cntrl_time = g.handle_control()

            # Update
            g.update()
            tick += 1
            
            # Render objects
            render_time_3D = g.render()

            # Render GUI
            render_time_2D = g.gui()
        else:
            # Take user input
            g.handle_control()

            # Update
            g.update()
            
            # Render objects
            g.render()
            tick += 1

            # Render GUI
            g.gui()

        pygame.display.flip() # Invert screen
        pygame.display.update() # Display new render
        time_elapsed = 0 # Reset elapsed time
quit()
