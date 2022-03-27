import pygame as pg


# TODO rewrite using length of vector in polar coordinates
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


def pointsInArc():
    pass


class State:
    def __init__(self, modes):
        self.modes = modes
        self.current = 0
    
    def next(self):
        self.current += 1
        self.current %= self.modes
