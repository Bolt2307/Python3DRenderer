import pygame
import math
import time
import json

# !IMPORTANT!
scene_path = "scenepath.json"
# Change this path ^ to the current path of the "scene.json" file on your system

# Class definitions

# Triple tuple representing 3d oordinates, 3d rotation, 3d movement, etc.
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
    isStatic = True

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

    def __init__ (self, id, position, orientation, origin, scale, wire_thickness, visible, transparent, vertices, faces):
        self.id = id
        self.position = position
        self.orientation = orientation
        self.origin = origin
        self.scale = scale
        self.wire_thickness = wire_thickness
        self.visible = visible
        self.transparent = transparent
        self.vertices = vertices
        self.faces = faces

    def set_color (self, color): # Set the entire object to a color
        for face in self.faces:
            face.color = color

def find_obj (id, list = None):
    if list == None:
        list = objects
    for obj in list:
        if obj.id == id:
            return list.index(obj)

def copy_obj (id, new_id, list = None, new_list = None):
    if list == None:
        list = objects
    if new_list == None:
        new_list = list
    obj = list[find_obj(id)]
    new_list.append(Object(new_id, obj.position, obj.orientation, obj.origin, obj.scale, obj.wire_thickness, obj.visible, obj.transparent, obj.vertices, obj.faces))

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

def render ():
    t0 = time.perf_counter_ns()
    zbuffer = []

    for obj in objects:
        for face in obj.faces:
            if obj.visible == True:
                show = True # The object will be rendered unless one of its vertices is out-of-scope
                points = []
                depthval = 0
                for vertex in face.indices:
                    # Scaling
                    x = vertex.x * obj.scale.x
                    y = vertex.y * obj.scale.y
                    z = vertex.z * obj.scale.z

                    # Rotation
                    x, z = rotate_point(x - obj.origin.x, z - obj.origin.z, math.radians(obj.orientation.y))
                    y, z = rotate_point(y - obj.origin.y, z - obj.origin.z, math.radians(obj.orientation.x))
                    x, y = rotate_point(x - obj.origin.x, y - obj.origin.y, math.radians(obj.orientation.z))

                    # Offset
                    x += obj.position.x
                    y += obj.position.y
                    z += obj.position.z

                    # Rotation relative to camera
                    x, y, z = x - cam.position.x, y - cam.position.y - cam.height, z - cam.position.z
                    pitch, yaw, roll = math.radians(cam.rotation.x), math.radians(cam.rotation.y), math.radians(cam.rotation.z)
                    x, z = rotate_point(x, z, yaw)
                    y, z = rotate_point(y, z, pitch)
                    x, y = rotate_point(x, y, roll)

                    if z < 0: # Do not render clipping or out-of-scope objects
                        show = False
                        break
                        
                    points.append(((x * cam.focal_length/z+screen.get_width()/2) * (screen.get_width() / Screen.fullwidth), (-y * cam.focal_length/z+screen.get_height()/2)*(screen.get_height() / Screen.fullheight)))
                    depthval += z # add z to the sum of the z values

                depthval /= len(face.indices) # depthval now stores the z of the object's center
                if show & ((shoelace(points) > 0) | obj.transparent):
                    zbuffer.append([face.color.to_tuple(), points, obj.wire_thickness, depthval]) # Store the info in zbuffer
    zbuffer.sort(key=lambda x: x[3], reverse=True) # Sort z buffer by the z distance from the camera
    for face in zbuffer: # Draw each face
        pygame.draw.polygon(screen, face[0], face[1], face[2])

    return time.perf_counter_ns() - t0
                
def gui ():
    t0 = time.perf_counter_ns()
    global crosshairspread
    global specstog
    global pause
    crosshairspread = speed * 100
    
    #crosshairs
    pygame.draw.line(screen, 'red', (screen.get_width()/2-10-crosshairspread, screen.get_height()/2), (screen.get_width()/2-crosshairspread, screen.get_height()/2)) #horizontal left
    pygame.draw.line(screen, 'red', (screen.get_width()/2+crosshairspread, screen.get_height()/2), (screen.get_width()/2+10+crosshairspread, screen.get_height()/2)) #horizontal right
    pygame.draw.line(screen, 'red', (screen.get_width()/2, screen.get_height()/2-10-crosshairspread), (screen.get_width()/2, screen.get_height()/2-crosshairspread)) #vertical top
    pygame.draw.line(screen, 'red', (screen.get_width()/2, screen.get_height()/2+crosshairspread), (screen.get_width()/2, screen.get_height()/2+10+crosshairspread)) #vertical vertical bottom
    if pause == True:
        pausetext = analytics_font.render('PAUSED', False, (200, 0, 0))
        screen.blit(pausetext, (screen.get_width()/2, 0))
    if specstog == True:
            print_elapsed_time(cntrl_time, engine_update_time, render_time_3D, render_time_2D, idle_time, measured_fps)
    return time.perf_counter_ns()-t0

def handle_control ():
    t0 = time.perf_counter_ns()
    global pausecooldown
    global specstog
    global pause
    global speed
    global running
    global place
    placecooldown = 0
    keys = pygame.key.get_pressed()

    #rotation
    rel = pygame.mouse.get_rel()
    if pause == False:
        cam.rotation.y += rel[0]*0.15
        cam.rotation.x -= rel[1]*0.15 #mouse sense

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
        if placecooldown <= 0:
            if keys[pygame.K_q] & (place == False):
                place = True
                placecooldown = 0.1
            else:
                place = False
        else:
            placecooldown -= 0.01

    #misc
    else:
        if keys[pygame.K_e]: #exits the game if e is pressed in pause
            running = False
        if keys[pygame.K_f]:
            if specstog == True:
                specstog = False
            elif specstog == False:
                specstog = True
    if pausecooldown < 0: #pauses the game on escape
        if keys[pygame.K_ESCAPE]:
            pausecooldown = 0.2
            if pause == False:
                pause = True
                pygame.mouse.set_visible(True)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif pause == True:
                pause = False
                pygame.mouse.set_visible(False)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
    else:
        pausecooldown -= 0.02 #makes sure that pause key is not held and spammed
    return time.perf_counter_ns() - t0

def update():
    global tick
    global cubenum
    t0 = time.perf_counter_ns()
    if pause == False:
        pygame.mouse.set_pos(screen.get_width()/2, screen.get_height()/2) #mouse "lock"

        if place:
            x, y, z, = 0, 0, 2
            y, z = rotate_point(y, z, -math.radians(cam.rotation.x))
            x, z = rotate_point(x, z, -math.radians(cam.rotation.y))
            x, y = rotate_point(x, y, -math.radians(cam.rotation.z))
            x, y, z = round((x + cam.position.x) / 0.5) * 0.5, round((y + cam.position.y) / 0.5) * 0.5, round((z + cam.position.z) / 0.5) * 0.5
            copy_obj("cube", "cube" + str(cubenum))
            objects[find_obj("cube" + str(cubenum))].position = Vector3(x, y, z)
            objects[find_obj("cube" + str(cubenum))].visible = True
            cubenum += 1

	    # Change position by velocity and apply drag to velocity
        cam.position.x, cam.position.y, cam.position.z = cam.position.x + cam.velocity.x, cam.position.y + cam.velocity.y, cam.position.z + cam.velocity.z
        cam.velocity.x, cam.velocity.y, cam.velocity.z = cam.velocity.x * 0.85, cam.velocity.y * 0.85, cam.velocity.z * 0.85
        tick += 1
        if cam.position.y > 0: # Apply Gravity
            cam.velocity.y -= 0.02
        else:
            cam.velocity.y = 0
            cam.position.y = 0
    return time.perf_counter_ns() - t0

# Prints data and debug information to view while running
def print_elapsed_time(cntrl_time, engine_update_time, render_time_3D, render_time_2D, idle_time, fps):
    cntrl_text = analytics_font.render('control_update: ' + str(round(cntrl_time / 1000,2)) + ' us', False, (0, 0, 0))
    engine_update_text = analytics_font.render('engine_update: ' + str(round(engine_update_time / 1000,2)) + ' us', False, (0, 0, 0))
    render_3D_text = analytics_font.render('render_time_3D: ' + str(round(render_time_3D / 1000,2)) + ' us', False, (0, 0, 0))
    render_2D_text = analytics_font.render('render_time_2D: ' + str(round(render_time_2D / 1000,2)) + ' us', False, (0, 0, 0))
    total_text = analytics_font.render('active_time: ' + str(round((render_time_2D + cntrl_time + engine_update_time + render_time_3D) / 1000000,2)) + ' ms', False, (0, 0, 0))
    idle_text = analytics_font.render('idle_time: ' + str(round(idle_time * 1000,2)) + ' ms', False, (0, 0, 0))
    fps_text = analytics_font.render('fps: ' + str(round(fps)), False, (0, 0, 0))
    tick_text = analytics_font.render('tick: ' + str(tick), False, (0, 0, 0))
    screen.blit(cntrl_text, (5,0))
    screen.blit(engine_update_text, (5,20))
    screen.blit(render_3D_text, (5,40))
    screen.blit(render_2D_text, (5,60))
    screen.blit(total_text, (5,80))
    screen.blit(idle_text, (5,100))
    screen.blit(fps_text, (5,120))
    screen.blit(tick_text, (5, 140))

# Main section

cubenum = 0
place = False
specstog = False
pause = False
pausecooldown = 0
crosshairspread = 0
speed = 0.025

pygame.init()
pygame.font.init()
analytics_font = pygame.font.SysFont('cousine', 20)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
Screen.fullwidth, Screen.fullheight = screen.get_width(), screen.get_height() #finds fullscreen dim
screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True
pygame.display.set_caption('Python (Pygame) - 3D Renderer')
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
pygame.mouse.set_visible(False)
    
# Instantiate classes
cam = Camera()

# Initiate Object Lists
objects = []

# Timing/frame_cap variables
frame = 0
frame_cap = 1000

# Load scene JSON as objects
with open(scene_path) as file:
    scene = json.load(file)
    bgcolor = tuple(scene["bg_color"])
file.close()
for objpath in scene["object_file_paths"]:
    with open(scene["folder_path"] + objpath) as file:
        obj = json.load(file)
        vertices = []
        for vertex in obj["vertices"]:
            vertices.append(Vector3(tuple(vertex)))
        faces = []
        for face in obj["faces"]:
            faces.append(Face((tuple(face[0])), RGBColor(tuple(face[1]))))
        objects.append(Object(obj["id"], Vector3(tuple(obj["position"])), Vector3(tuple(obj["orientation"])), Vector3(tuple(obj["origin"])), Vector3(tuple(obj["scale"])), obj["wire_thickness"], obj["visible"], obj["transparent"], vertices, faces))
    file.close()

# Precompiling faces
for obj in objects:
    for face in obj.faces:
        face.indices = list(face.indices)
        for index in range(len(face.indices)):
            face.indices[index] = obj.vertices[face.indices[index]]

# Measurement variables
cntrl_time = 0 # Nanoseconds
engine_update_time = 0 # Nanoseconds
render_time_3D = 0  # Nanoseconds
render_time_2D = 0 # Nanoseconds
time_elapsed = 0 # Seconds
measured_fps = 0
idle_time = 0 # Seconds
tick = 0 #ticks up 1 after every update

last_timestamp = time.perf_counter() # Seconds

while running:
    current_timestamp = time.perf_counter()
    time_elapsed += current_timestamp - last_timestamp # Add change in time to the time_elapsed
    last_timestamp = current_timestamp
    if time_elapsed > 1 / frame_cap: # Do not update unless enough time has passed
        frame += 1

        # Handle events
        for gevent in pygame.event.get():
            pass
        # Background color
        screen.fill(bgcolor)
        
        # Print elapsed time ever n frames
        if frame % 60 == 0:
            # Take user input
            cntrl_time = handle_control()

            # Update
            engine_update_time = update()
            
            # Render objects
            render_time_3D = render()

            # Render GUI
            render_time_2D = gui()

            # Update measurement variables
            measured_fps = 1/time_elapsed
            idle_time = time_elapsed

        else:
            # Take user input
            handle_control()

            # Update
            update()
            
            # Render objects
            render()

            # Render GUI
            gui()

        pygame.display.flip() # Invert screen
        pygame.display.update() # Display new render
        time_elapsed = 0 # Reset elapsed time
quit()
