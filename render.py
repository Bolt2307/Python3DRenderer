from pygame import*
from math import*
vertices = [(-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1),
            (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1)]
triangles = [
    (0, 1, 2), (2, 3, 0),
    (0, 4, 5), (5, 1, 0),
    (0, 4, 3), (4, 7, 3),
    (5, 4, 7), (7, 6, 5),
    (7, 6, 3), (6, 2, 3),
    (5, 1, 2), (2, 6, 5)]

init()
screen = display.set_mode((0,0), FULLSCREEN)
clock = time.Clock()
running = True
display.set_caption('YEAH BABY!')
mouse.set_cursor(SYSTEM_CURSOR_CROSSHAIR)
mouse.set_visible(False)

class scrn:
    width = screen.get_width()
    height = screen.get_height()

class cam:
    x = 0
    y = 0
    z = -10
    pitch = 0
    yaw = 0
    roll = 0
    fov = 400

class player:
    xvel = 0
    yvel = 0
    zvel = 0

def rotate(x, y, r):
  return x * cos(r) - y * sin(r), x * sin(r) + y * cos(r)

def render ():
    for triangle in triangles:
        points = []
        for vertex in triangle:
            x, y, z = vertices[vertex]
            x, y, z = x - cam.x, y - cam.y, z - cam.z
            pitch, yaw, roll = radians(cam.pitch), radians(cam.yaw), radians(cam.roll)
            x, z = rotate(x, z, yaw)
            y, z = rotate(y, z, pitch)
            x, y = rotate(x, y, roll)
            points.append((x * cam.fov/z+scrn.width/2, -y * cam.fov/z+scrn.height/2))
        draw.polygon(screen, 'black', points, 0)

def control ():
    keys = key.get_pressed()

    #rotation
    rel = mouse.get_rel()
    cam.yaw += rel[0]/10
    cam.pitch -= rel[1]/10

    #movement
    if keys[K_w]:
        player.zvel += 0.05*cos(radians(cam.yaw))
        player.xvel += 0.05*sin(radians(cam.yaw))
    if keys[K_s]:
        player.zvel -= 0.05*cos(radians(cam.yaw))
        player.xvel -= 0.05*sin(radians(cam.yaw))
    if keys[K_a]:
        player.zvel -= 0.05*cos(radians(cam.yaw+90))
        player.xvel -= 0.05*sin(radians(cam.yaw+90))
    if keys[K_d]:
        player.zvel += 0.05*cos(radians(cam.yaw+90))
        player.xvel += 0.05*sin(radians(cam.yaw+90))
    if keys[K_SPACE]:
        if cam.y <= 0:
            player.yvel += 1

while running:
    for gevent in event.get():
        if gevent.type == QUIT:
            running = False
    screen.fill('white')
    control()
    render()
    cam.x, cam.y, cam.z = cam.x + player.xvel, cam.y + player.yvel, cam.z + player.zvel
    player.xvel, player.yvel, player.zvel = player.xvel * 0.85, player.yvel * 0.85, player.zvel * 0.85
    if cam.y > 0:
        player.yvel -= 0.1
    else:
        player.yvel = 0
        cam.y += 0.001
    display.flip()
    display.update()
    clock.tick(60)
quit()
