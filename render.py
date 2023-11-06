from pygame import*
from math import*
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
    rotation = Vector3(0,0,0) # x = rotation.y, y = rotation.x, z = roll
    velocity = Vector3(0,0,0)
    height = 0
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

class Object:
    position = Vector3(0,0,0)

    wire_thickness = 0
    wire_color = RGBColor(0,0,0)

    renderable = True
    visible = True

    vertices = [] # List of all points as tuples 
    points = [] # List of all points as points

    def set_color(self,col):
        for face in self.points:
            face.col = col


pause = False
pausecooldown = 0
crosshairspread = 0
speed = 0.025

init()
font.init()
analytics_font = font.SysFont('cousine', 15)
screen = display.set_mode((0,0), FULLSCREEN)
running = True
display.set_caption('YEAH BABY!')
mouse.set_cursor(SYSTEM_CURSOR_CROSSHAIR)
mouse.set_visible(False)

# Dimensions of the screen
class Screen:
    width = screen.get_width()
    height = screen.get_height()
    
# Instantiate classes
cam = Camera()
scrn = Screen()

objects = []
cube = Object()
cube.vertices = [(-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1), #cube
            (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1),
            (2, -1, -1), (4, -1, -1), (2, -1, 1), (4, -1, 1), (4, 1, -1), (2, 1, -1)] #wedge 1st=8
cube.points = []

# I'll make functions for creating a pre-fab later
f = [
    (0, 1, 2), (2, 3, 0), #Cube
    (0, 4, 5), (5, 1, 0),
    (0, 4, 3), (4, 7, 3),
    (5, 4, 7), (7, 6, 5),
    (7, 6, 3), (6, 2, 3),
    (5, 1, 2), (2, 6, 5),
    (8, 10, 13), (9, 11, 12), #Wedge
    (8, 9, 11), (8, 10, 11),
    (8, 9, 12), (8, 13, 12),
    (13, 10, 12), (12, 11, 10)]
for v in f:
    cube.points.append(Face(v,RGBColor(random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))))


objects.append(cube)

def rotate_point(x, y, r):
  return x * cos(r) - y * sin(r), x * sin(r) + y * cos(r)

def zsort (input):
    return input[0][0][2]

def render ():
    t0 = time.process_time_ns()
    for obj in objects:
        for face in obj.points:
            show = False
            points = []
            for vertex in face.connection_vertices:
                x, y, z = obj.vertices[vertex]
                x, y, z = x - cam.position.x, y - cam.position.y - cam.height, z - cam.position.z
                yaw, pitch, roll = radians(cam.rotation.x), radians(cam.rotation.y), radians(cam.rotation.z)
                x, z = rotate_point(x, z, yaw)
                y, z = rotate_point(y, z, pitch)
                x, y = rotate_point(x, y, roll)
                if z < 100: #stops rendering from 100 units away (broken)
                    if z > 0: #stops rendering when behind the camera (broken)
                        show = True
                points.append((x * cam.focal_length/z+scrn.width/2, -y * cam.focal_length/z+scrn.height/2)) #vector3 coord
            if show == True:
                draw.polygon(screen, RGBColor.to_tuple(face.col), points, obj.wire_thickness) #shape
    return time.process_time_ns()-t0

def gui ():
    t0 = time.process_time_ns()
    global crosshairspread
    crosshairspread = speed * 100
    
    #crosshairs
    draw.line(screen, 'red', (scrn.width/2-10-crosshairspread, scrn.height/2), (scrn.width/2-crosshairspread, scrn.height/2)) #horizontal left
    draw.line(screen, 'red', (scrn.width/2+crosshairspread, scrn.height/2), (scrn.width/2+10+crosshairspread, scrn.height/2)) #horizontal right
    draw.line(screen, 'red', (scrn.width/2, scrn.height/2-10-crosshairspread), (scrn.width/2, scrn.height/2-crosshairspread)) #vertical top
    draw.line(screen, 'red', (scrn.width/2, scrn.height/2+crosshairspread), (scrn.width/2, scrn.height/2+10+crosshairspread)) #vertical vertical bottom
    return time.process_time_ns()-t0

def handle_control ():
    t0 = time.process_time_ns()
    global pausecooldown
    global pause
    global speed
    keys = key.get_pressed()

    #rotation
    rel = mouse.get_rel()
    if pause == False:
        cam.rotation.x += rel[0]*0.15
        cam.rotation.y -= rel[1]*0.15 #mouse sense

        #movement
        if keys[K_LSHIFT]: #sprinting
            if speed < 0.1:
                speed += 0.01
            if cam.focal_length > 300:
                cam.focal_length -= 10
        else:
            if speed > 0.025:
                speed -= 0.005
            if cam.focal_length < 400:
                cam.focal_length += 10
        if keys[K_w]:
            cam.velocity.z += speed*cos(radians(cam.rotation.x))
            cam.velocity.x += speed*sin(radians(cam.rotation.x))
        if keys[K_s]:
            cam.velocity.z -= speed*cos(radians(cam.rotation.x))
            cam.velocity.x -= speed*sin(radians(cam.rotation.x))
        if keys[K_a]:
            cam.velocity.z -= speed*cos(radians(cam.rotation.x+90))
            cam.velocity.x -= speed*sin(radians(cam.rotation.x+90))
        if keys[K_d]:
            cam.velocity.z += speed*cos(radians(cam.rotation.x+90))
            cam.velocity.x += speed*sin(radians(cam.rotation.x+90))
        if keys[K_SPACE]:
            if cam.position.y <= 0:
                cam.velocity.y += 1
        if keys[K_LCTRL]:
            if cam.height > -1:
                cam.height -= 0.2
        else:
            if cam.height < 0:
                cam.height += 0.2

    #misc
    else:
        if keys[K_e]: #exits the game if e is pressed in pause
            QUIT()

    if pausecooldown < 0: #pauses the game on pauseape
        if keys[K_ESCAPE]:
            pausecooldown = 0.2
            if pause == False:
                pause = True
                mouse.set_visible(True)
                mouse.set_cursor(SYSTEM_CURSOR_ARROW)
            elif pause == True:
                pause = False
                mouse.set_visible(False)
                mouse.set_cursor(SYSTEM_CURSOR_CROSSHAIR)
    else:
        pausecooldown -= 0.1 #makes sure that pauseape is not held and spammed
    return time.process_time_ns()-t0

bgcolor = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
cam.position.z = -10

def update():
    t0 = time.process_time_ns()
    if pause == False:
        mouse.set_pos(scrn.width/2, scrn.height/2) #mouse "lock"
	    # Change position by velocity and apply drag to velocity
        cam.position.x, cam.position.y, cam.position.z = cam.position.x + cam.velocity.x, cam.position.y + cam.velocity.y, cam.position.z + cam.velocity.z
        cam.velocity.x, cam.velocity.y, cam.velocity.z = cam.velocity.x * 0.85, cam.velocity.y * 0.85, cam.velocity.z * 0.85
        if cam.position.y > 0: # Apply Gravity
            cam.velocity.y -= 0.05
        else:
            cam.velocity.y = 0
            cam.position.y = 0
    return time.process_time_ns()-t0

def print_elapsed_time(cntrl_time, engine_update_time, render_time_3D, render_time_2D):
    cntrl_text = analytics_font.render('control_update: ' + str(cntrl_time / 1000) + ' us', False, (0, 0, 0))
    engine_update_text = analytics_font.render('engine_update: ' + str(engine_update_time / 1000) + ' us', False, (0, 0, 0))
    render_3D_text = analytics_font.render('render_time_3D: ' + str(render_time_3D / 1000) + ' us', False, (0, 0, 0))
    render_2D_text = analytics_font.render('render_time_2D: ' + str(render_time_2D / 1000) + ' us', False, (0, 0, 0))
    total_text = analytics_font.render('total: ' + str((render_time_2D + cntrl_time + engine_update_time + render_time_3D) / 1000000) + ' ms', False, (0, 0, 0))
    screen.blit(cntrl_text, (0,0))
    screen.blit(engine_update_text, (0,20))
    screen.blit(render_3D_text, (0,40))
    screen.blit(render_2D_text, (0,60))
    screen.blit(total_text, (0,80))

frame = 0
cntrl_time = 0
engine_update_time = 0
render_time_3D = 0
render_time_2D = 0
time_elapsed = 0
while running:
    frame += 1
    # Handle events
    for gevent in event.get():
        if gevent.type == QUIT:
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
        print_elapsed_time(cntrl_time, engine_update_time, render_time_3D, render_time_2D)
    else:
        # Take user input
        handle_control()

        # Update
        update()
        
        # Render objects
        render()

        # Render GUI
        gui()
        print_elapsed_time(cntrl_time, engine_update_time, render_time_3D, render_time_2D)

    display.flip() # Invert screen
    display.update() # Display new render
quit()
