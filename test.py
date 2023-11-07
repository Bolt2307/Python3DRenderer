import pygame
import math
import random
import time

# Class definitions

# Triple tuple representing coordinates, rotation, movement, etc.
class Vector3:
    x,y,z = 0,0,0

    def __init__(self,xVal,yVal,zVal):
        x,y,z = xVal,yVal,zVal
# Represents camera controlled by the cam.velocity
class Camera:
    position = Vector3(0,0,0)
    rotation = Vector3(0,0,0) # x = yaw, y = pitch, z = roll
    velocity = Vector3(0,0,0)
    height = 0
    fov = 90
    focal_length = 400

class RGBColor:
    r = 0
    g = 0
    b = 0
    def __init__(self,red,green,blue):
        self.r,self.g,self.b = red,green,blue

    def to_tuple(self):
        return (self.r,self.g,self.b)

class Face:
    col = RGBColor(0,0,0)
    connection_vertices = (0,0,0)

    def __init__(self,vertices,color):
        self.col = color
        self.connection_vertices = vertices

class BoxCollider: # I will work on polygon colliders later
    isVisible = True
    vertices = [(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0)]

    def set_collider(self,new_vertices):
        for i in range(len(new_vertices)):
            self.vertices[i] = new_vertices[i]

class Object:
    position = Vector3(0,0,0)

    wire_thickness = 0
    wire_color = RGBColor(0,0,0)

    renderable = True
    visible = True

    collider = BoxCollider()

    on_collision = None # execute this function on a collision with another object

    vertices = [] # List of all points as tuples 
    points = [] # List of all points as points

    def set_color(self,col):
        for face in self.points:
            face.col = col


pause = False
pausecooldown = 0
crosshairspread = 0
speed = 0.025

pygame.init()
pygame.font.init()
analytics_font = pygame.font.SysFont('cousine', 20)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
running = True
pygame.display.set_caption('YEAH BABY!')
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
pygame.mouse.set_visible(False)

# Dimensions of the screen
class Screen:
    width = screen.get_width()
    height = screen.get_height()
    
# Instantiate classes
cam = Camera()
scrn = Screen()

cam.focal_length = scrn.width/2/math.tan(math.radians(cam.fov/2))
objects = []
cube = Object()
cube.vertices = [(-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1), #cube
            (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1)]
cube.points = []

# I'll make functions for creating a pre-fab later
f = [
    (0, 1, 2), (2, 3, 0), #Cube
    (0, 4, 5), (5, 1, 0),
    (0, 4, 3), (4, 7, 3),
    (5, 4, 7), (7, 6, 5),
    (7, 6, 3), (6, 2, 3),
    (5, 1, 2), (2, 6, 5),]
for v in f:
    cube.points.append(Face(v,RGBColor(random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))))

wedge = Object() 
wedge.vertices = [(2, -1, -1), (4, -1, -1), (2, -1, 1), (4, -1, 1), (4, 1, -1), (2, 1, -1)] #wedge 1st=8
wedge.points = []

# I'll make functions for creating a pre-fab later
f = [(0, 2, 5), (1, 3, 4), #Wedge
    (0, 1, 3), (0, 2, 3),
    (0, 1, 3), (0, 5, 4),
    (5, 2, 4), (4, 3, 2)]
for v in f:
    wedge.points.append(Face(v,RGBColor(random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))))

objects.append(cube)
objects.append(wedge)
cube.collider.set_collider([(-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1), (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1)])

ground = Object()
ground.vertices = [(5,-2,5),(5,-2,-5),(-5,-2,-5),(-5,-2,5)]
f = [(0,1,2)]
for v in f:
    ground.points.append(Face(v,RGBColor(random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))))
objects.append(ground)

def rotate_point(x, y, r):
  return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)

def zsort (input):
    return input[0][0][2]

def render ():
    t0 = time.perf_counter_ns()
    for obj in objects:
        for face in obj.points:
            show = False
            points = []
            #https://math.stackexchange.com/questions/2305792/3d-projection-on-a-2d-plane-weak-maths-ressources
            for vertex in face.connection_vertices:
                x, y, z = obj.vertices[vertex]
                x, y, z = x - cam.position.x, y - cam.position.y - cam.height, z - cam.position.z
                if z < 100 and z > 0: #stops rendering from 100 units away (broken)
                    show = True
                x *= cam.focal_length/z
                y *= cam.focal_length/z
                points.append((x +scrn.width/2, -y + scrn.height/2)) #vector3 coord
            if show == True:
                pygame.draw.polygon(screen, RGBColor.to_tuple(face.col), points, obj.wire_thickness) #shape
    return time.perf_counter_ns()-t0

def gui ():
    t0 = time.perf_counter_ns()
    global crosshairspread
    crosshairspread = speed * 100
    
    #crosshairs
    pygame.draw.line(screen, 'red', (scrn.width/2-10-crosshairspread, scrn.height/2), (scrn.width/2-crosshairspread, scrn.height/2)) #horizontal left
    pygame.draw.line(screen, 'red', (scrn.width/2+crosshairspread, scrn.height/2), (scrn.width/2+10+crosshairspread, scrn.height/2)) #horizontal right
    pygame.draw.line(screen, 'red', (scrn.width/2, scrn.height/2-10-crosshairspread), (scrn.width/2, scrn.height/2-crosshairspread)) #vertical top
    pygame.draw.line(screen, 'red', (scrn.width/2, scrn.height/2+crosshairspread), (scrn.width/2, scrn.height/2+10+crosshairspread)) #vertical vertical bottom
    return time.perf_counter_ns()-t0

def handle_control ():
    t0 = time.perf_counter_ns()
    global pausecooldown
    global pause
    global speed
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
                cam.velocity.y += 0.5
        if keys[pygame.K_LCTRL]:
            if cam.height > -1:
                cam.height -= 0.2
        else:
            if cam.height < 0:
                cam.height += 0.2

    #misc
    else:
        if keys[pygame.K_e]: #exits the game if e is pressed in pause
            pygame.QUIT()

    if pausecooldown < 0: #pauses the game on pauseape
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
        pausecooldown -= 0.1 #makes sure that pauseape is not held and spammed
    return time.perf_counter_ns()-t0

bgcolor = (48,244,255)#(random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
cam.position.z = -10

def update():
    t0 = time.perf_counter_ns()
    if pause == False:
        pygame.mouse.set_pos(scrn.width/2, scrn.height/2) #mouse "lock"
	    # Change position by velocity and apply drag to velocity
        cam.position.x, cam.position.y, cam.position.z = cam.position.x + cam.velocity.x, cam.position.y + cam.velocity.y, cam.position.z + cam.velocity.z
        cam.velocity.x, cam.velocity.y, cam.velocity.z = cam.velocity.x * 0.85, cam.velocity.y * 0.85, cam.velocity.z * 0.85
        if cam.position.y > 0: # Apply Gravity
            cam.velocity.y -= 0.02
        else:
            cam.velocity.y = 0
            cam.position.y = 0
    return time.perf_counter_ns()-t0

# Prints data and debug information to view while running
def print_elapsed_time(cntrl_time, engine_update_time, render_time_3D, render_time_2D, idle_time, fps):
    cntrl_text = analytics_font.render('control_update: ' + str(round(cntrl_time / 1000,2)) + ' us', False, (0, 0, 0))
    engine_update_text = analytics_font.render('engine_update: ' + str(round(engine_update_time / 1000,2)) + ' us', False, (0, 0, 0))
    render_3D_text = analytics_font.render('render_time_3D: ' + str(round(render_time_3D / 1000,2)) + ' us', False, (0, 0, 0))
    render_2D_text = analytics_font.render('render_time_2D: ' + str(round(render_time_2D / 1000,2)) + ' us', False, (0, 0, 0))
    total_text = analytics_font.render('total: ' + str(round((render_time_2D + cntrl_time + engine_update_time + render_time_3D) / 1000000,2)) + ' ms', False, (0, 0, 0))
    idle_text = analytics_font.render('idle_time: ' + str(round(idle_time * 1000,2)) + ' ms', False, (0, 0, 0))
    fps_text = analytics_font.render('fps: ' + str(round(fps)), False, (0, 0, 0))
    pos_text = analytics_font.render('pos: x: ' + str(round(cam.position.x,2)) + ' y: ' + str(round(cam.position.y,2)) + ' z: ' + str(round(cam.position.z,2)), False, (0, 0, 0))
    rot_text = analytics_font.render('yaw: ' + str(round(cam.rotation.x,2)) + ' pitch: ' + str(round(cam.rotation.y,2)) + ' roll: ' + str(round(cam.rotation.z,2)), False, (0, 0, 0))
    screen.blit(cntrl_text, (5,0))
    screen.blit(engine_update_text, (5,20))
    screen.blit(render_3D_text, (5,40))
    screen.blit(render_2D_text, (5,60))
    screen.blit(total_text, (5,80))
    screen.blit(idle_text, (5,100))
    screen.blit(fps_text, (5,120))
    screen.blit(pos_text, (5,140))
    screen.blit(rot_text, (5,160))

# Timing/frame_cap variables
frame = 0
frame_cap = 120

# Measurement variables
cntrl_time = 0 # Nanoseconds
engine_update_time = 0 # Nanoseconds
render_time_3D = 0  # Nanoseconds
render_time_2D = 0 # Nanoseconds
time_elapsed = 0 # Seconds
measured_fps = 0
idle_time = 0 # Seconds

last_timestamp = time.perf_counter() # Seconds

while running:
    current_timestamp = time.perf_counter()
    time_elapsed += current_timestamp - last_timestamp # Add change in time to the time_elapsed
    last_timestamp = current_timestamp
    if time_elapsed > 1 / frame_cap: # Do not update unless enough time has passed
        frame += 1

        # Handle events
        for gevent in pygame.event.get():
            if gevent.type == pygame.QUIT:
                running = False
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

            print_elapsed_time(cntrl_time, engine_update_time, render_time_3D, render_time_2D, time_elapsed, measured_fps)
        else:
            # Take user input
            handle_control()

            # Update
            update()
            
            # Render objects
            render()

            # Render GUI
            gui()
            print_elapsed_time(cntrl_time, engine_update_time, render_time_3D, render_time_2D, idle_time, measured_fps)

        pygame.display.update() # Display new render
        time_elapsed = 0 # Reset elapsed time
pygame.quit()
