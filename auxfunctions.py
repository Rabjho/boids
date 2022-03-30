import pygame as pg
from pygame import gfxdraw

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

class Grid:
    def __init__(self, surface, cellSize):
        self.surface = surface
        self.cellSize = cellSize
        self.cellAmount = int(max(self.surface.get_size()) / cellSize) + 1

        self.cellAmount = 26
        self.cellSize = 50


        self.cells = [[None for cell in range(self.cellAmount)] for cell in range(self.cellAmount)]


    def addToGrid(self, object):
        cellX = int(object.position.x / self.cellSize)
        cellY = int(object.position.y / self.cellSize)

        object.prev = None
        object.next = self.cells[cellX][cellY]
        self.cells[cellX][cellY] = object

        if (object.next != None):
            object.next.prev = object

    def handleBoids(self):
        for x in range(self.cellAmount):
            for y in range(self.cellAmount):
                self.handleCell(x, y)

    def handleUnit(self, object, other):
        while (other != None):
            # if (inPie(other.position, object.position, object.searchRadius, object.lWingVector.as_polar()[1], object.rWingVector.as_polar()[1])):
            if (inCircle(other.position, object.position, object.searchRadius) and object != other):
                self.test.append((other, other.color == object.color))
                print("start")
                print(id(object))
                print(object.boidsInRange)
                object.boidsInRange.append((other, other.color == object.color))
                print(object.boidsInRange)
                pass
            other = other.next

            if (other == None):
                break

    def handleCell(self, x, y):
        object = self.cells[x][y]
        while (object != None):
            object.boidsInRange = []
            self.test = []
            self.handleUnit(object, object.next)


            # if(x > 0 and y > 0): self.handleUnit(object, self.cells[x-1][y-1])
            # if(x > 0): self.handleUnit(object, self.cells[x-1][y])
            # if(y > 0): self.handleUnit(object, self.cells[x][y-1])
            # if(x > 0 and y < self.cellAmount - 1): self.handleUnit(object, self.cells[x-1][y+1])


            object = object.next

    def move(self, object, newPos):
        oldCellX = int(object.position.x / self.cellSize)
        oldCellY = int(object.position.y / self.cellSize)

        cellX = int(newPos.x / self.cellSize)
        cellY = int(newPos.y / self.cellSize)

        if (oldCellX == cellX and oldCellY == cellY):
            return

        if (object.prev != None):
            object.prev.next = object.next

        if (object.next != None):
            object.next.prev = object.prev

        if (self.cells[oldCellX][oldCellY] == object):
            self.cells[oldCellX][oldCellY] = object.next
        
        self.addToGrid(object)

    def drawGrid(self):
        for i in range(self.cellAmount):
            gfxdraw.hline(self.surface, 0, self.surface.get_width(), i * self.cellSize, pg.Color("#000000"))
            gfxdraw.vline(self.surface, i * self.cellSize, 0, self.surface.get_height(), pg.Color("#000000"))
            