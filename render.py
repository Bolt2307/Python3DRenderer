from math import sin, cos, radians
import turtle
vertices = [(-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1),
            (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1)]
triangles = [
    (0, 1, 2), (2, 3, 0),
    (0, 4, 5), (5, 1, 0),
    (0, 4, 3), (4, 7, 3),
    (5, 4, 7), (7, 6, 5),
    (7, 6, 3), (6, 2, 3),
    (5, 1, 2), (2, 6, 5)]

class cam:
	x = -5
	y = 0
	z = -5
	xr = 0
	yr = 45
	zr = 0
	fov = 400

window = turtle.Screen()
window.title("YEAH BABY!")
pointer = turtle.Turtle()
pointer.hideturtle()
turtle.tracer(0, 0)
pointer.up()

def rotate(x, y, r):
  return x * cos(r) - y * sin(r), x * sin(r) + y * cos(r)

counter = 0
while True:
	pointer.clear()
	for triangle in triangles:
		points = []
		for vertex in triangle:
			x, y, z = vertices[vertex]
			x, y, z = x - cam.x, y - cam.y, z - cam.z
			xr, yr, zr = radians(cam.xr), radians(cam.yr), radians(cam.zr)
			x, z = rotate(x, z, yr)
			y, z = rotate(y, z, xr)
			x, y = rotate(x, y, zr)
			points.append((x * cam.fov/z, y * cam.fov/z))
		pointer.goto(points[0][0], points[0][1])
		pointer.down()
		pointer.goto(points[1][0], points[1][1])
		pointer.goto(points[2][0], points[2][1])
		pointer.goto(points[0][0], points[0][1])
		pointer.up()
	turtle.update()
