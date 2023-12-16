def clamp(min,max,x):
    if max < x:
        return max
    if min > x:
        return min
    return x
