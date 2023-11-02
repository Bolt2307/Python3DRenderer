from pygame import*
from math import*

# Class definitions

# Triple tuple representing coordinates, rotation, movement, etc.
class Vector3:
    x,y,z = 0,0,0

# Represents camera controlled by the cam.velocity
class Camera:
    position = Vector3()
    rotation = Vector3() # x = rotation.y, y = rotation.x, z = roll
    velocity = Vector3()
    focal_length = 400
	
pause = False
pausecooldown = 0
crosshairspread = 0
speed = 0.025

init()
screen = display.set_mode((0,0), FULLSCREEN)
clock = time.Clock()
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

# Put these into classes with vertex data and color later
vertices = [(-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1), #cube
            (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1),
            (2, -1, -1), (4, -1, -1), (2, -1, 1), (4, -1, 1), (4, 1, -1), (2, 1, -1)] #wedge 1st=8
faces = [
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

def rotate_point(x, y, r):
  return x * cos(r) - y * sin(r), x * sin(r) + y * cos(r)

def render ():
    for face in faces:
        points = []
        for vertex in face:
            x, y, z = vertices[vertex]
            x, y, z = x - cam.position.x, y - cam.position.y, z - cam.position.z
            yaw, pitch, roll = radians(cam.rotation.x), radians(cam.rotation.y), radians(cam.rotation.z)
            x, z = rotate_point(x, z, yaw)
            y, z = rotate_point(y, z, pitch)
            x, y = rotate_point(x, y, roll)
            show = False
            if z < 100: #stops rendering from 100 units away
                if z > 0: #stops rendering when behind the camera
                    show = True
            points.append((x * cam.focal_length/z+scrn.width/2, -y * cam.focal_length/z+scrn.height/2))
        if show == True:
            draw.polygon(screen, 'black', points, 0)

def gui ():
    global crosshairspread
    crosshairspread = speed * 100
    
    #crosshairs
    draw.line(screen, 'red', (scrn.width/2-10-crosshairspread, scrn.height/2), (scrn.width/2-crosshairspread, scrn.height/2)) #horizontal left
    draw.line(screen, 'red', (scrn.width/2+crosshairspread, scrn.height/2), (scrn.width/2+10+crosshairspread, scrn.height/2)) #horizontal right
    draw.line(screen, 'red', (scrn.width/2, scrn.height/2-10-crosshairspread), (scrn.width/2, scrn.height/2-crosshairspread)) #vertical top
    draw.line(screen, 'red', (scrn.width/2, scrn.height/2+crosshairspread), (scrn.width/2, scrn.height/2+10+crosshairspread)) #vertical vertical bottom

def handle_control ():
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
            speed = 0.1
        else:
            speed = 0.025
        if keys[K_w]:
            cam.velocity.z += speed*cos(radians(cam.rotation.y))
            cam.velocity.x += speed*sin(radians(cam.rotation.y))
        if keys[K_s]:
            cam.velocity.z -= speed*cos(radians(cam.rotation.y))
            cam.velocity.x -= speed*sin(radians(cam.rotation.y))
        if keys[K_a]:
            cam.velocity.z -= speed*cos(radians(cam.rotation.y+90))
            cam.velocity.x -= speed*sin(radians(cam.rotation.y+90))
        if keys[K_d]:
            cam.velocity.z += speed*cos(radians(cam.rotation.y+90))
            cam.velocity.x += speed*sin(radians(cam.rotation.y+90))
        if keys[K_SPACE]:
            if cam.position.y <= 0:
                cam.velocity.y += 1
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
cam.position.z = -10

while running:
    # Handle events
    for gevent in event.get():
        if gevent.type == QUIT:
            running = False
    # Background color
    screen.fill('white')
    
	# Take in user input
    handle_control()
    if pause == False:
        mouse.set_pos(scrn.width/2, scrn.height/2) #mouse "lock"
	    # Change position by velocity and apply drag to velocity
        cam.position.x, cam.position.y, cam.position.z = cam.position.x + cam.velocity.x, cam.position.y + cam.velocity.y, cam.position.z + cam.velocity.z
        cam.velocity.x, cam.velocity.y, cam.velocity.z = cam.velocity.x * 0.85, cam.velocity.y * 0.85, cam.velocity.z * 0.85
        if cam.position.y > 0: # Apply Gravity
            cam.velocity.y -= 0.05
        else:
            cam.velocity.y = 0
            cam.position.y += 0.001
    
	# Render objects
    render()

    # Render GUI
    gui()
    
    display.flip() # Invert screen
    display.update() # Display new render
    clock.tick(1000) #1000 fps
quit()
