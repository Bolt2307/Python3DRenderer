
from math import sin, cos
import tkinter
import turtle

class Vector3: # Use this instead of triple tuples
	x = 0
	y = 0
	z = 0
	def Vector3(newX, newY, newZ):
		x = newX
		y = newY
		z = newZ

# Class definitions

class Camera: # Represents physical attributes of a camera used to render
	x = 0
	y = 0
	z = -5
	xr = 0
	yr = 0
	zr = 0
	fov = 400

# Function definitions

def anglesToVector(yaw,pitch): # Returns a Vector3 representing the direction as a 3d vector
	x = cos(yaw) * cos(pitch)
	z = sin(yaw) * cos(pitch)
	y = sin(pitch)
	return Vector3(x,y,z)

def rotate(x, y, r): # PLEASE DOCUMENt THIS MAX
  return x * cos(r) - y * sin(r), x * sin(r) + y * cos(r)

# Replace this with Vector3-composed objects
vertices = [(-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1), (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1)]
triangles = [
    (0, 1, 2), (2, 3, 0),
    (0, 4, 5), (5, 1, 0),
    (0, 4, 3), (4, 7, 3),
    (5, 4, 7), (7, 6, 5),
    (7, 6, 3), (6, 2, 3),
    (5, 1, 2), (2, 6, 5)]

# Example of class instantiation
cam = Camera()

window = turtle.Screen()
window.title("YEAH BABY!")
pointer = turtle.Turtle()
pointer.hideturtle()
turtle.tracer(0, 0)
pointer.up()

# Main loop
while True:
	pointer.clear()
	for triangle in triangles:
		points = []
		for vertex in triangle:
			x, y, z = vertices[vertex]
			x, y, z = x - cam.x, y - cam.y, z - cam.z
			xr, yr, zr = -cam.xr, -cam.yr, -cam.zr
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
