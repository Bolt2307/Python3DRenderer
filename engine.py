import math
import os
import pygame
import json
import time
import graphics
import helpers

# Function definitions
def rotate2D(x,y,r):
    return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)

# File reading
def rel_dir (str):
    if (str[0] == "/") | (str[0] == "."):
        return str
    else:
        return os.path.dirname(__file__) + "/" + str

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
    
    # Returns (x1-x2,y1-y2,z1-z2)
    def subtract_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x-v3.x,self.y-v3.y,self.z-v3.z)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1+x2,y1+y2,z1+z2)
    def add_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x+v3.x,self.y+v3.y,self.z+v3.z)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1*x2,y1*y2,z1*z2)
    def multiply_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x*v3.x,self.y*v3.y,self.z*v3.z)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1/x2,y1/y2,z1/z2)
    def divide_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x/v3.x,self.y/v3.y,self.z/v3.z)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1-n,y1-n,z1-n)
    def subtract_by_num(self,num,set_this_vector):
        v = Vector3(self.x-num,self.y-num,self.z-num)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1+n,y1+n,z1+n)
    def add_by_num(self,num,set_this_vector):
        v = Vector3(self.x+num,self.y+num,self.z+num)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1*n,y1*n,z1*n)
    def multiply_by_num(self,num,set_this_vector):
        v = Vector3(self.x*num,self.y*num,self.z*num)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    # Returns (x1/n,y1/n,z1/n)
    def divide_by_num(self,num,set_this_vector):
        v = Vector3(self.x/num,self.y/num,self.z/num)
        if set_this_vector:
            self.x,self.y,self.z = v.x,v.y,v.z
        return v
    
    def rotate_by_euler(self,rotation):
        self.y, self.z = rotate2D(self.y, self.z, rotation.x)
        self.x, self.z = rotate2D(self.x, self.z, rotation.y)
        self.x, self.y = rotate2D(self.x, self.y, rotation.z)
        


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

class BoxCollider:
    isActive = True
    isTouched = False
    collisions = []
    minvertex = Vector3(0,0,0) # opposite vertices
    maxvertex = Vector3(1,1,1)

# Represents the data of an object that the engine needs to process
class Transform:
    points = [] # List of Vector3s that represent the object's points
    position = Vector3(0,0,0)
    rotation = Vector3(0,0,0)
    origin = Vector3(0,0,0)
    collider = BoxCollider()

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

    velocity = Vector3(0, 0, 0)
    dragFactor = 1

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

class Collision:
    epicenter = Vector3(0,0,0)
    otherCollider = None

class CollisionManager:
    colliders = []

    def calculateCollisions(self):
        #  Terrible O(n^2) time complexity will optimize later
        for collider in self.colliders:
            collider.collisions = []
            # Calculate collisions
            for other in self.colliders:
                if collider == other:
                    continue

                amin = collider.minvertex
                amax = collider.maxvertex
                bmin = other.minvertex
                bmax = other.maxvertex

                # I'm genuinely sorry
                overlap = amin.x <= bmin.x & amax.x >= bmin.x & amin.y <= bmax.y & amax.y >= bmin.y & amin.x <= bmax.z & amax.z >= bmin.z

                # Like I cannot express how sorry I am
                if overlap:
                    epicenter = Vector3(0,0,0)
                    for vertex in [amin,amax,bmin,bmax]:
                        epicenter.add_by_vector(vertex,True)
                    epicenter.divide_by_num(4)

                    perspective1 = Collision()
                    perspective1.epicenter = epicenter
                    perspective1.otherCollider = other
                    collider.collisions.append(perspective1)

                    perspective2 = Collision()
                    perspective2.epicenter = epicenter
                    perspective2.otherCollider = collider
                    other.collisions.append(perspective2)

class Engine:
    # Lists
    objects = []

    # Booleans
    can_jump = True
    specstog = False
    specsHeld = False
    paused = False
    pause_held = False
    active = True

    # Numbers
    crosshairspread = 0
    speed = 0.025

    # Objects
    screen = None
    cam = None
    graphics = None
    window = None
    collision_manager = CollisionManager()

    def __init__(self, graphics):
        self.graphics = graphics
        self.cam = graphics.cam
        self.window = graphics.window

        self.specstog = False
        self.specsHeld = False
        self.paused = False
        self.crosshairspread = 0
        self.speed = 0.025
        self.pause_held = False
        self.screen = graphics.screen

        pygame.init()
        pygame.font.init()

        self.analytics_font = pygame.font.SysFont('cousine', 20)

        self.screen.fullwidth, self.screen.full = self.window.get_width(), self.window.get_height() #finds fullscreen dimensions

        self.clock = pygame.time.Clock()

        pygame.display.set_caption('Python (Pygame) - 3D Renderer')
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        pygame.mouse.set_visible(False)

        self.cam.drag = 0.8 # Actual camera drag
        self.cam.air_drag = 0.85 # Actual camera aerial drag

        self.objects = self.load_objects(rel_dir("scene_path.json"))
        self.graphics.objects = self.objects

    def load_objects (self, path):
        objlist = []
        with open(path) as file:
            scene = json.load(file)
            g.bgcolor = tuple(scene["bg_color"])
            g.ambient_light = RGBColor(tuple(scene["ambient"]))
            folder_path = rel_dir(scene["folder_path"])
            g.textures_path = rel_dir(scene["textures_path"])
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
                    #id, type, position, orientation, origin, scale, wire_thickness, visible, transparent, static, vertices, faces, light_color, light_direction, is_source, light_spread
                objlist.append(Object(obj["name"], obj["type"], Vector3(tuple(obj["position"])), Vector3(tuple(obj["orientation"])), Vector3(tuple(obj["origin"])), Vector3(tuple(obj["scale"])), obj["wire_thickness"], obj["visible"], obj["transparent"], obj["static"], vertices, faces, RGBColor(tuple(obj["light"]["color"])), Vector3(tuple(obj["light"]["direction"])), obj["light"]["spread"], obj["textures"]))
            file.close()
        return objlist

    def update(self):
        t0 = time.perf_counter_ns()
        self.collision_manager.calculateCollisions()
        cam = self.cam

        if not self.paused:
            pygame.mouse.set_pos(self.window.get_width()/2, self.window.get_height()/2) #mouse "lock"

        # Update camera
        if (cam.position.y > 0): # In air
            # Apply drag
            cam.velocity.x *= cam.air_drag
            cam.velocity.y *= cam.air_drag
            cam.velocity.z *= cam.air_drag

            # Gravity
            cam.velocity.y -= 0.1
        else: # Touching the ground
            # Apply drag
            cam.velocity.x *= cam.drag
            cam.velocity.y *= cam.drag
            cam.velocity.z *= cam.drag

            self.can_jump = True

        cam.position.x += cam.velocity.x
        cam.position.y += cam.velocity.y
        cam.position.z += cam.velocity.z

        if cam.position.y < 0:
            cam.position.y = 0

        for obj in self.objects:
            # Add to position by velocity & decrease velocity by the drag factor
            #obj.transform.position.x,obj.transform.position.y,obj.transform.position.z = obj.velocity.x * obj.dragFactor,obj.velocity.y * obj.dragFactor,obj.velocity.z * obj.dragFactor
            pass

        return time.perf_counter_ns() - t0

    def handle_control(self):
        t0 = time.perf_counter_ns()
        keys = pygame.key.get_pressed()
        cam = self.cam

        #rotation
        rel = pygame.mouse.get_rel()

        if not self.paused: # When unpaused
            cam.rotation.y += rel[0]*0.15
            cam.rotation.x -= rel[1]*0.15 #mouse sense

            cam.rotation.x = helpers.clamp(-90,90,cam.rotation.x)
            
            speed = self.speed
            #movement
            if keys[pygame.K_LSHIFT]: #sprinting
                if speed < 0.05: # Smoothen acceleration to sprint speed
                    self.speed += 0.01
                if cam.focal_length > 300:
                    cam.focal_length -= 10
            else:
                if speed > 0.02: # Smoothen decceleration to walk speed
                    self.speed -= 0.005
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
            if keys[pygame.K_SPACE] and self.can_jump:
                cam.velocity.y += 0.8
                self.can_jump = False
        else: # In pause menu
            if keys[pygame.K_e]: #exits the game if e is pressed in pause
                self.active = False

            if keys[pygame.K_f]:
                if not self.specsHeld:
                    self.specstog = not self.specstog
                    self.specsHeld = True
            else:
                self.specsHeld = False

        if keys[pygame.K_ESCAPE]:
            if not self.pause_held: # Pause handling
                self.pause_held = True
                self.paused = not self.paused
                pygame.mouse.set_visible(not pygame.mouse.get_visible())
                if self.paused:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        else:
            self.pause_held = False

        return time.perf_counter_ns() - t0

# Main
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

g = graphics.Graphics(window)
engine = Engine(g)

time_elapsed = 0 # Time since last frame
last_timestamp = time.perf_counter() # Last timestamp collected
tick = 0

debug_data = []

while engine.active:
    current_timestamp = time.perf_counter()
    time_elapsed += current_timestamp - last_timestamp # Add change in time to the time_elapsed
    last_timestamp = current_timestamp
    if time_elapsed > 1 / g.frame_cap: # Do not update unless enough time has passed
        g.frame += 1

        # Handle events
        for gevent in pygame.event.get():
            pass
        
        # Print elapsed time ever n frames
        if g.frame % 20 == 0:
            debug_data = []
            debug_data.append(("time_since_last_frame(ms)",time_elapsed * 1000))

            # Engine update
            debug_data.append(("engine:control(us)",engine.handle_control()/1000))
            debug_data.append(("engine:update(us)",engine.update()/1000))
            
            # Render objects
            debug_data.append(("graphics:render3D(us)",g.render()/1000))

            # Render GUI
            debug_data.append(("graphics:render2D(us)",g.gui()/1000))
            
            debug_data.append(("graphics:render3D:faces",g.get_rendered_faces()))
            debug_data.append(("graphics:render3D:objects",g.get_rendered_objects()))
            debug_data.append(("fps",1/time_elapsed))
        else:
            # Engine update
            engine.handle_control()
            engine.update()
            tick += 1
            
            # Render objects
            g.render()

            # Render GUI
            g.gui()

        pygame.display.flip() # Invert screen
        pygame.display.update() # Display new render
        time_elapsed = 0 # Reset elapsed time

        # Add debug texts to the graphics render buffer
        if engine.specstog:
            for pair in debug_data: # (String label, int time_difference)
                g.debug_log(pair[0] + ": " + str(round(pair[1],2)),engine.analytics_font)
quit()
