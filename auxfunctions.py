from tracemalloc import start
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

def drawPie(pieCenter, r, startVector, endVector):
    points = [pieCenter]

    if (startVector.as_polar()[1] < endVector.as_polar()[1]):
        pieAngle = abs(round(startVector.as_polar()[1] - endVector.as_polar()[1]))
    else:
        pass
        pieAngle = 360 - abs(round(startVector.as_polar()[1] - endVector.as_polar()[1]))

    for i in range(pieAngle, 0, -1):
        pass
        points.append(pieCenter + startVector.rotate(i) * r)

    points.append(pieCenter)

    if (len(points) > 2):
        return points
    else:  
        return (pieCenter, startVector, endVector)


class State:
    def __init__(self, modes):
        self.modes = modes
        self.current = 0
    
    def next(self):
        self.current += 1
        self.current %= self.modes
