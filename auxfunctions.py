import pygame as pg
from pygame import gfxdraw
import math

def inCircle(point, circlePos, r):
    return (circlePos.x - point.x) * (circlePos.x - point.x) + (circlePos.y - point.y) * (circlePos.y - point.y) <= r*r



def inPie(point, pieCenter, r, angleStart, angleEnd):
    vector = pg.Vector2(point.x - pieCenter.x, point.y - pieCenter.y).as_polar()

    if (vector[0] > r):
        return False
    else:
        if (angleStart > angleEnd):
            return (vector[1]+180 >= angleStart+180 or vector[1]+180 <= angleEnd+180)
        else:
            return (vector[1]+180 >= angleStart+180 and vector[1]+180 <= angleEnd+180)

# TODO Rewrite this from the bottom up
def drawPie(surface, pieCenter, r, angleStart, angleEnd):
    pass
    # points = [(pieCenter.x, pieCenter.y)]
    # for n in range(int(angleStart)+180, int(angleEnd)+180):
    #     x = pieCenter.x + (r * math.cos(n * math.pi / 180))
    #     y = pieCenter.y + (r * math.sin(n * math.pi / 180))

    #     points.append((x,y))
    #     print(str(n * math.pi / 180))
    # points.append((pieCenter.x, pieCenter.y))
    # if (len(points) > 2):
    #     gfxdraw.filled_polygon(surface, points, pg.Color(150,150,150,80))
    # else:
    #     print("now")
    # return points


class State:
    def __init__(self, modes):
        self.modes = modes
        self.current = 0
    
    def next(self):
        self.current += 1
        self.current %= self.modes
