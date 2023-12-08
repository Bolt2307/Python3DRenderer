import pygame
import math
import time
import json
import os
from PIL import Image

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
    texture = -1
    shading_color = (0, 0, 0)

    def __init__(self, indices, color, texture = -1):
        self.texture = texture
        self.indices = indices
        self.color = color

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
    textures = [] # List of all textures as paths

    light_color = RGBColor(0, 0, 0)
    light_direction = Vector3(0, 0, 0)
    light_spread = 0

    def __init__ (self, id, type, position, orientation, origin, scale, wire_thickness, visible, transparent, static, vertices, faces, light_color, light_direction, light_spread, textures = []):
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
    active = True

    screen = Screen()
    objects = []

    bgcolor = (255, 255, 255)
    specstog = False
    specsHeld = False
    paused = False
    crosshairspread = 0
    speed = 0.025
    textures_path = ""

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
        self.crosshairspread = 0
        self.speed = 0.025
        self.ambient_light = RGBColor(0, 0, 0)
        self.pause_held = False

        pygame.init()
        pygame.font.init()
        self.analytics_font = pygame.font.SysFont('cousine', 20)
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen.fullwidth, self.screen.full = self.window.get_width(), self.window.get_height() #finds fullscreen dimensions
        self.window = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Python (Pygame) - 3D Renderer')
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        pygame.mouse.set_visible(False)

        self.objects = self.load_objects(rel_dir("scene_path.json"))

    # Load scene JSON as objects
    def load_objects (self, path):
        global textures_path
        objlist = []
        with open(path) as file:
            scene = json.load(file)
            self.bgcolor = tuple(scene["bg_color"])
            self.ambient_light = RGBColor(tuple(scene["ambient"]))
            folder_path = rel_dir(scene["folder_path"])
            textures_path = rel_dir(scene["textures_path"])
        file.close()
        for objpath in scene["object_file_paths"]:
            with open(folder_path + objpath) as file:
                obj = json.load(file)
                vertices = []
                for vertex in obj["vertices"]:
                    vertices.append(Vector3(tuple(vertex)))
                faces = []
                for face in obj["faces"]:
                    faces.append(Face((tuple(face[0])), RGBColor(tuple(face[1])), face[2]))
                objlist.append(Object(obj["name"], obj["type"], Vector3(tuple(obj["position"])), Vector3(tuple(obj["orientation"])), Vector3(tuple(obj["origin"])), Vector3(tuple(obj["scale"])), obj["wire_thickness"], obj["visible"], obj["transparent"], obj["static"], vertices, faces, RGBColor(tuple(obj["light"]["color"])), Vector3(tuple(obj["light"]["direction"])), obj["light"]["spread"], obj["textures"]))
            file.close()
        return objlist
    
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

    def bake_lighting (self):
        for light in self.objects:
            for face in light.faces:
                face.shading_color = (self.ambient_light.r/255, self.ambient_light.g/255, self.ambient_light.b/255)
            if light.type == "light":
                list = self.objects
                for obj in list:
                    if obj.visible & (not obj.type == "light"):
                        vertices = []
                        for vertex in obj.vertices:
                            x, y, z = vertex.x, vertex.y, vertex.z
                            if not obj.locked:

                                vert = self.apply_changes(obj, vertex)
                                x, y, z = vert.x, vert.y, vert.z

                            vertices.append(self.perspective(light.position, light.light_direction, Vector3(x, y, z)))

                        for face in obj.faces:
                            show = True
                            points = []
                            planepts = []
                            for index in face.indices:
                                x, y, z = vertices[index].x, vertices[index].y, vertices[index].z
                                if z < 0:
                                    show = False
                                points.append(((x * light.light_spread/z), (-y * light.light_spread/z)))
                                planepts.append(Vector3(x, y, z))

                            area = shoelace(points)
                            if (area > 0) & show:
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

    def render(self):
        self.window.fill(self.bgcolor)
        t0 = time.perf_counter_ns()
        zbuffer = []

        for obj in self.objects:
            cam = self.cam
            if obj.visible:
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
                        texture = textures_path + obj.textures[face.texture]
                    else:
                        texture = False
                    depthval /= len(face.indices) # depthval now stores the z of the object's center
                    if show & ((shoelace(points) > 0) | obj.transparent):
                        zbuffer.append([face.color, points, obj.wire_thickness, depthval, face.shading_color, obj.type, texture]) # Store the info in zbuffer

        zbuffer.sort(key=lambda x: x[3], reverse=True) # Sort z buffer by the z distance from the camera

        for f in zbuffer: # Draw each face
            if f[6] == False:
                if f[5] == "light":
                    r, g, b = (f[0].r, f[0].g, f[0].b)
                else:
                    r = int(f[0].r*f[4][0])
                    g = int(f[0].g*f[4][1])
                    b = int(f[0].b*f[4][2])
                    if r > 255: r = 255
                    if g > 255: g = 255
                    if b > 255: b = 255
                try:
                    pygame.draw.polygon(self.window, (r, g, b), f[1], f[2])
                except:
                    pygame.draw.polygon(self.window, f[0].to_tuple(), f[1], f[2])
            else:
                if len(f[1]) >= 4:
                    facepts = f[1]
                    facepts.sort(key=lambda x: x[1])
                    top = [facepts[0], facepts[1]]
                    bottom = [facepts[2], facepts[3]]
                    top.sort(key=lambda x: x[0])
                    bottom.sort(key=lambda x: x[0])
                    facepts = [top[0], top[1], bottom[0], bottom[1]]
                    image = Image.open(f[6], "r")
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
                            r, g, b = texture[y * image.width + x]
                            if f[5] == "light":
                                r, g, b = (f[0].r, f[0].g, f[0].b)
                            else:
                                r = int(r*f[4][0])
                                g = int(g*f[4][1])
                                b = int(b*f[4][2])
                                if r > 255: r = 255
                                if g > 255: g = 255
                                if b > 255: b = 255
                            pygame.draw.polygon(self.window, (r, g, b), pts, 0)

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
            pass
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
                    self.speed += 0.01
                if cam.focal_length > 300:
                    cam.focal_length -= 10
            else:
                if speed > 0.025:
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
            if keys[pygame.K_SPACE]:
                if cam.position.y <= 0:
                    cam.velocity.y += 1
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

    def update(self):
        t0 = time.perf_counter_ns()
        if not self.paused:
            pygame.mouse.set_pos(self.window.get_width()/2, self.window.get_height()/2) #mouse "lock"
            self.bake_lighting()
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