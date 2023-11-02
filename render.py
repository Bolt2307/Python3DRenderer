from pygame import*
from math import*

# Class definitions

# Triple tuple representing coordinates, rotation, movement, etc.
class Vector3:
    x,y,z = 0,0,0

# Represents camera controlled by the player
class Camera:
    position = Vector3()
    rotation = Vector3() # x = yaw, y = pitch, z = roll
    velocity = Vector3()
    focal_length = 400
    
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

init()
screen = display.set_mode((0,0), FULLSCREEN)
clock = time.Clock()
running = True
display.set_caption('YEAH BABY!')
mouse.set_cursor(SYSTEM_CURSOR_CROSSHAIR)
mouse.set_visible(False)

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
            points.append((x * cam.focal_length/z+scrn.width/2, -y * cam.focal_length/z+scrn.height/2))
        draw.polygon(screen, 'black', points, 0)

def handle_control ():
    keys = key.get_pressed()

    #rotation
    rel = mouse.get_rel()
    cam.rotation.x += rel[0]*0.2
    cam.rotation.y -= rel[1]*0.2

    #movement
    if keys[K_w]:
        cam.velocity.z += 0.05*cos(radians(cam.rotation.x))
        cam.velocity.x += 0.05*sin(radians(cam.rotation.x))
    if keys[K_s]:
        cam.velocity.z -= 0.05*cos(radians(cam.rotation.x))
        cam.velocity.x -= 0.05*sin(radians(cam.rotation.x))
    if keys[K_a]:
        cam.velocity.z -= 0.05*cos(radians(cam.rotation.x+90))
        cam.velocity.x -= 0.05*sin(radians(cam.rotation.x+90))
    if keys[K_d]:
        cam.velocity.z += 0.05*cos(radians(cam.rotation.x+90))
        cam.velocity.x += 0.05*sin(radians(cam.rotation.x+90))
    if keys[K_SPACE]:
        if cam.position.y <= 0:
            cam.velocity.y += 1

while running:
    # Handle events
    for gevent in event.get():
        if gevent.type == QUIT:
            running = False
    # Background color
    screen.fill('white')
    
	# Take in user input
    handle_control()
    
	# Render objects
    render()
    
	# Change position by velocity and apply drag to velocity
    cam.position.x, cam.position.y, cam.position.z = cam.position.x + cam.velocity.x, cam.position.y + cam.velocity.y, cam.position.z + cam.velocity.z
    cam.velocity.x, cam.velocity.y, cam.velocity.z = cam.velocity.x * 0.85, cam.velocity.y * 0.85, cam.velocity.z * 0.85
    if cam.position.y > 0: # Apply Gravity
        cam.velocity.y -= 0.05
    else:
        cam.velocity.y = 0
        cam.position.y += 0.001
    display.flip() # Invert screen
    display.update() # Display new render
    clock.tick(60)
quit()
