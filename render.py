import pygame
import math
import time

# Class definitions

# Triple tuple representing 3d oordinates, 3d rotation, 3d movement, etc.
class Vector3:
    x, y, z = 0, 0, 0

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def to_tuple(self):
        return (self.x, self.y, self.z)

# Double tuple representing 2d coordinates, 2d rotation, 2d movement, etc.
class Vector2:
    x, y = 0, 0

    def __init__(self, x, y):
        self.x, self.y = x, y

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
    def __init__(self, red, green, blue):
        self.r, self.g, self.b = red, green, blue

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

    position = Vector3(0,0,0)
    orientation = Vector3(0, 0, 0)
    origin = Vector3(0, 0, 0)
    scale = Vector3(0, 0, 0)

    wire_thickness = 0
    wire_color = RGBColor(0,0,0)

    transparent = False

    vertices = [] # List of all points as Vector3 
    faces = [] # List of all faces as faces

    def __init__ (self, position, orientation, origin, scale, wire_thickness, transparent, vertices, faces):
        self.position = position
        self.orientation = orientation
        self.origin = origin
        self.scale = scale
        self.wire_thickness = wire_thickness
        self.transparent = transparent
        self.vertices = vertices
        self.faces = faces

    def set_color (self, color): # Set the entire object to a color
        for face in self.faces:
            face.color = color

def rotate_point (x, y, r):
  return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)

class FaceData:
    color = RGBColor(0,0,0)
    points = []
    wire_thickness = 0
    obj = None

    def __init__(self,color,points,wire_thickness,obj):
        self.color = color
        self.points = points
        self.wire_thickness = wire_thickness
        self.obj = obj

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

    for face in precompiled_faces:
        show = True # The object will be rendered unless one of its vertices is out-of-scope
        points = []
        depthval = 0
        for vertex in face.points:
            obj = face.obj
            # Scaling
            x = vertex.x * obj.scale.x - obj.origin.x
            y = vertex.y * obj.scale.y - obj.origin.y
            z = vertex.z * obj.scale.z - obj.origin.z

            # Rotation
            x, z = rotate_point(x, z, math.radians(obj.orientation.x))
            y, z = rotate_point(y, z, math.radians(obj.orientation.y))
            x, y = rotate_point(x, y, math.radians(obj.orientation.z))

            # Offset
            x += obj.origin.x + obj.position.x
            y += obj.origin.y + obj.position.y
            z += obj.origin.z + obj.position.z

            # Rotation relative to camera
            x, y, z = x - cam.position.x, y - cam.position.y - cam.height, z - cam.position.z
            yaw, pitch, roll = math.radians(cam.rotation.x), math.radians(cam.rotation.y), math.radians(cam.rotation.z)
            x, z = rotate_point(x, z, yaw)
            y, z = rotate_point(y, z, pitch)
            x, y = rotate_point(x, y, roll)

            if z < 0: # Do not render clipping or out-of-scope objects
                show = False
                break
                
            points.append(((x * cam.focal_length/z+screen.get_width()/2) * (screen.get_width() / Screen.fullwidth), (-y * cam.focal_length/z+screen.get_height()/2)*(screen.get_height() / Screen.fullheight)))
            depthval += z # add z to the sum of the z values

        depthval /= len(face.points) # depthval now stores the z of the object's center
        if show & (shoelace(points) > 0):
            zbuffer.append([face.color.to_tuple(), points, face.wire_thickness, depthval]) # Store the info in zbuffer
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
    keys = pygame.key.get_pressed()

    #rotation
    rel = pygame.mouse.get_rel()
    if pause == False:
        cam.rotation.x += rel[0]*0.15
        cam.rotation.y -= rel[1]*0.15 #mouse sense

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
            cam.velocity.z += speed*math.cos(math.radians(cam.rotation.x))
            cam.velocity.x += speed*math.sin(math.radians(cam.rotation.x))
        if keys[pygame.K_s]:
            cam.velocity.z -= speed*math.cos(math.radians(cam.rotation.x))
            cam.velocity.x -= speed*math.sin(math.radians(cam.rotation.x))
        if keys[pygame.K_a]:
            cam.velocity.z -= speed*math.cos(math.radians(cam.rotation.x+90))
            cam.velocity.x -= speed*math.sin(math.radians(cam.rotation.x+90))
        if keys[pygame.K_d]:
            cam.velocity.z += speed*math.cos(math.radians(cam.rotation.x+90))
            cam.velocity.x += speed*math.sin(math.radians(cam.rotation.x+90))
        if keys[pygame.K_SPACE]:
            if cam.position.y <= 0:
                cam.velocity.y += 1
        if keys[pygame.K_LCTRL]:
            if cam.height > -1:
                cam.height -= 0.2
        else:
            if cam.height < 0:
                cam.height += 0.2

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
    global objects
    global tick
    t0 = time.perf_counter_ns()
    if pause == False:
        pygame.mouse.set_pos(screen.get_width()/2, screen.get_height()/2) #mouse "lock"
	    # Change position by velocity and apply drag to velocity
        cube.position = Vector3(5*math.sin(tick/100)-10, 5*math.sin(tick/75), 5*math.sin(tick/50)+10) #position demonstration
        wedge.orientation = Vector3(tick, tick/1.5, tick/2) #orientation demonstration
        cube2.scale = Vector3(math.sin(tick/100)+2, math.sin(tick/75)+2, math.sin(tick/50)+2) #scaling demonstration
        cam.position.x, cam.position.y, cam.position.z = cam.position.x + cam.velocity.x, cam.position.y + cam.velocity.y, cam.position.z + cam.velocity.z
        cam.velocity.x, cam.velocity.y, cam.velocity.z = cam.velocity.x * 0.85, cam.velocity.y * 0.85, cam.velocity.z * 0.85
        tick += 1
        if cam.position.y > 0: # Apply Gravity
            cam.velocity.y -= 0.02
        else:
            cam.velocity.y = 0
            cam.position.y = 0
    objects = [cube, wedge, cube2]
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
    screen.blit(cntrl_text, (5,0))
    screen.blit(engine_update_text, (5,20))
    screen.blit(render_3D_text, (5,40))
    screen.blit(render_2D_text, (5,60))
    screen.blit(total_text, (5,80))
    screen.blit(idle_text, (5,100))
    screen.blit(fps_text, (5,120))

# Main section

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

objects = []
cube = Object(Vector3(0, 0, 10), Vector3(0, 0, 0), Vector3(0, 0, 0), Vector3(1, 1, 1), 0, False, [], []) #position, orientation, origin, wire thickness, visible
cube.vertices = [Vector3(-1, -1, -1), Vector3( 1, -1, -1), #vertex positions of the faces
    Vector3( 1,  1, -1), Vector3(-1,  1, -1),
    Vector3(-1, -1,  1), Vector3( 1, -1,  1),
    Vector3( 1,  1,  1), Vector3(-1,  1,  1)]
cube.faces = [Face((2, 1, 0), RGBColor(0, 200, 0)), Face((0, 3, 2), RGBColor(0, 200, 0)), #faces
    Face((5, 4, 0), RGBColor(200, 0, 0)), Face((0, 1, 5), RGBColor(200, 0, 0)),
    Face((0, 4, 3), RGBColor(0, 0, 200)), Face((4, 7, 3), RGBColor(0, 0, 200)),
    Face((7, 4, 5), RGBColor(0, 200, 0)), Face((5, 6, 7), RGBColor(0, 200, 0)),
    Face((7, 6, 3), RGBColor(200, 0, 0)), Face((6, 2, 3), RGBColor(200, 0, 0)),
    Face((5, 1, 2), RGBColor(0, 0, 200)), Face((2, 6, 5), RGBColor(0, 0, 200))]

wedge = Object(Vector3(4, 0, 4), Vector3(0, 0, 0), Vector3(0, 0, 0), Vector3(1, 1, 1), 0, False, [], [])
wedge.vertices = [Vector3(-1, -1, -1), Vector3( 1, -1, -1),
    Vector3(-1, -1,  1), Vector3( 1, -1,  1), 
    Vector3( 1,  1,  1), Vector3(-1,  1,  1)]
wedge.faces = [Face((0, 2, 5), RGBColor(0, 200, 0)), Face((4, 3, 1), RGBColor(0, 200, 0)),
    Face((0, 5, 4), RGBColor(200, 0, 0)), Face((4, 1, 0), RGBColor(200, 0, 0)),
    Face((0, 1, 3), RGBColor(0, 0, 200)), Face((3, 2, 0), RGBColor(0, 0, 200)),
    Face((5, 2, 3), RGBColor(0, 200, 200)), Face((3, 4, 5), RGBColor(0, 200, 200))]

cube2 = Object(Vector3(10, 0, 10), Vector3(0, 0, 0), Vector3(0, 0, 0), Vector3(1, 1, 1), 0, False, [], []) #position, orientation, origin, wire thickness, visible
cube2.vertices = [Vector3(-1, -1, -1), Vector3( 1, -1, -1), #vertex positions of the faces
    Vector3( 1,  1, -1), Vector3(-1,  1, -1),
    Vector3(-1, -1,  1), Vector3( 1, -1,  1),
    Vector3( 1,  1,  1), Vector3(-1,  1,  1)]
cube2.faces = [Face((2, 1, 0), RGBColor(0, 200, 0)), Face((0, 3, 2), RGBColor(0, 200, 0)), #faces
    Face((5, 4, 0), RGBColor(200, 0, 0)), Face((0, 1, 5), RGBColor(200, 0, 0)),
    Face((0, 4, 3), RGBColor(0, 0, 200)), Face((4, 7, 3), RGBColor(0, 0, 200)),
    Face((7, 4, 5), RGBColor(0, 200, 0)), Face((5, 6, 7), RGBColor(0, 200, 0)),
    Face((7, 6, 3), RGBColor(200, 0, 0)), Face((6, 2, 3), RGBColor(200, 0, 0)),
    Face((5, 1, 2), RGBColor(0, 0, 200)), Face((2, 6, 5), RGBColor(0, 0, 200))]
objects.append(cube)
objects.append(wedge)
objects.append(cube2)

bgcolor = RGBColor(255, 255, 255) #background color
# Timing/frame_cap variables
frame = 0
frame_cap = 1000

# Precompiled faces
precompiled_faces = []

for obj in objects:
    for face in obj.faces:
        points = []
        for index in face.indices:
            points.append(obj.vertices[index])
        precompiled_faces.append(FaceData(face.color,points,obj.wire_thickness,obj))

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
        screen.fill(bgcolor.to_tuple())
        
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
