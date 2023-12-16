#include <stdio.h>

// Algorithm for determining area of a polygon
// C-Implementation of the shoelace algorithm
double shoelace(double x[],double y[]) {
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