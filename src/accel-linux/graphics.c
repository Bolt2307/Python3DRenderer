#include <stdio.h>
#include <string.h>
#include <vector>

// C equivalents to the python classes

struct vector3 {
    double x;
    double y;
    double z
};

struct triangleFace {
    vector3 color;
    vector3 indices;
    vector3 shading_color;
    bool texture;
}

struct object {
    bool isStatic;
    bool locked;
    
    std::string id;
    std::string type;
    
    vector3 position;
    vector3 orientation;
    vector3 origin;
    vector3 scale;

    int wire_thickness;
    vector3 wire_color;

    bool visible;
    bool transparent;

    std::vector<vector3> vertices;
    std::vector<vector3> faces;

    vector3 light_color;
    vector3 light_direction;
    float light_spread;
};

// Pass the data from python to c in an absurd fashion
object constructObject(bool isStatic, bool locked, std::string id, std::string type, int wire_thickness, bool visible, bool transparent, float light_spread) {
    object obj;
    obj.isStatic = isStatic;
    obj.locked = locked;
    obj.id = id;
    obj.type = type;
    obj.wire_thickness = wire_thickness;
    obj.visible = visible;
    obj.transparent = transparent;
    obj.light_spread = light_spread;
}

/*
    Code to replicate:

    for obj in self.objects:
            for face in obj.faces:
                    face.shading_color = (self.ambient_light.r/255, self.ambient_light.g/255, self.ambient_light.b/255)
        for light in self.objects:
            if light.type == "light":
                list = self.objects
                for obj in list:
                    if obj.visible & (obj.type != "light"):
                        vertices = []
                        for vertex in obj.vertices:
                            x, y, z = vertex.x, vertex.y, vertex.z
                            if not obj.locked:

                                vert = self.apply_changes(obj, vertex)
                                x, y, z = vert.x, vert.y, vert.z

                            vertices.append(self.perspective(light.position, light.light_direction, Vector3(x, y, z)))

                        for face in obj.faces:
                            offscreen = True
                            show = True
                            points = []
                            planepts = []
                            for index in face.indices:
                                x, y, z = vertices[index].x, vertices[index].y, vertices[index].z
                                if z < 0:
                                    show = False
                                points.append(((x * light.light_spread/z), (-y * light.light_spread/z)))
                                if (x * light.light_spread/z <= self.window.get_width()) & (y * light.light_spread/z <= self.window.get_height()):
                                    offscreen = False
                                planepts.append(Vector3(x, y, z))

                            area = shoelace(points)
                            if (area > 0) & (show & (not offscreen)):
                                dist_from_center = math.sqrt(points[0][0] * points[0][0] + points[0][1] * points[0][1])
                                distance = math.sqrt((light.position.x - planepts[0].x)*(light.position.x - planepts[0].x) + (light.position.y - planepts[0].y)*(light.position.y - planepts[0].y) + (light.position.z - planepts[0].z)*(light.position.z - planepts[0].z))
                                if dist_from_center == 0:
                                    brightness = area / distance / 999
                                else:
                                    brightness = area / distance / 10 / dist_from_center
                                r = face.shading_color[0] + (light.light_color.r/255) * brightness
                                g = face.shading_color[1] + (light.light_color.g/255) * brightness
                                b = face.shading_color[2] + (light.light_color.b/255) * brightness
                                face.shading_color = (r, g, b)
*/
void bakeLighting() {

}

// Algorithm for determining area of a polygon
// C-Implementation of the shoelace algorithm
double shoelace(double x[],double y[]) {
    // Pointer conversion magic
    size_t xSize = *(&x + 1) - x;
    size_t ySize = *(&y + 1) - y;

    if (xSize == 0 || ySize == 0) {
        return 0;
    }

    if (xSize != ySize) { // Sizes aren't equal meaning that there is an extra x or y without a pair
        printf("C_ERROR: x[] and y[] aren't equal sizes\n");
        return 0;
    }

    double area = 0.0;
    for (int i = 0; i < xSize; ++i) {
        area += x[i] * y[i+1] - y[i] * x[i+1];
    }
    area += x[xSize-1] * y[0] - y[ySize-1] * x[0];
    return area;
}