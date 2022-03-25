from numpy import piecewise
import pygame as pg

def inCircle(point, circlePos, r):
    if ((circlePos.x - point.x) * (circlePos.x - point.x) + (circlePos.y - point.y) * (circlePos.y - point.y) >= r*r):
        return False
    else:
        return True


def inPie(point, pieCenter, r, angleStart, angleEnd):
    vector = pg.Vector2(point.x - pieCenter.x, point.y - pieCenter.y).as_polar()
    if(inCircle(point, pieCenter, r) and vector[1] >= angleStart and vector[1] <= angleEnd):
        return True
    else:
        return False