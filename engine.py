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
    
    # Returns (x1-x2,y1-y2,z1-z2)
    def subtract_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x-v3.x,self.y-v3.y,self.z-v3.z)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1+x2,y1+y2,z1+z2)
    def add_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x+v3.x,self.y+v3.y,self.z+v3.z)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1*x2,y1*y2,z1*z2)
    def multiply_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x*v3.x,self.y*v3.y,self.z*v3.z)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1/x2,y1/y2,z1/z2)
    def divide_by_vector(self,v3,set_this_vector):
        v = Vector3(self.x/v3.x,self.y/v3.y,self.z/v3.z)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1-n,y1-n,z1-n)
    def subtract_by_num(self,num,set_this_vector):
        v = Vector3(self.x-num,self.y-num,self.z-num)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1+n,y1+n,z1+n)
    def add_by_num(self,num,set_this_vector):
        v = Vector3(self.x+num,self.y+num,self.z+num)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1*n,y1*n,z1*n)
    def multiply_by_num(self,num,set_this_vector):
        v = Vector3(self.x*num,self.y*num,self.z*num)
        if set_this_vector:
            self = v
        return v
    
    # Returns (x1/n,y1/n,z1/n)
    def divide_by_num(self,num,set_this_vector):
        v = Vector3(self.x/num,self.y/num,self.z/num)
        if set_this_vector:
            self = v
        return v
    

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
  
class BoxCollider:
    isTouched = False
    vertices = (Vector3(0,0,0),Vector3(0,0,0),Vector3(0,0,0),Vector3(0,0,0),Vector3(0,0,0),Vector3(0,0,0))

# Represents the data of an object that the engine needs to process
class Transform:
    position = Vector3(0,0,0)
    rotation = Vector3(0,0,0)
    scale = Vector3(0,0,0)
    collider = BoxCollider()

class Engine:
    transforms = []
    colliders = []

    def __init__(self):
        for t in self.transforms:
            self.colliders.append(t.collider)

    