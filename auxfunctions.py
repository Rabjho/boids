import pygame as pg

# Defines a funtion which returns whether an object is in a circle
def inCircle(point, circlePos, r) -> bool:
    return (circlePos.x - point.x) * (circlePos.x - point.x) + (circlePos.y - point.y) * (circlePos.y - point.y) <= r*r

# Defines a funtion returning whether a point is within a pie with center, radius and polar angles of each "wing"
def inPie(point, pieCenter, r, angleStart, angleEnd) -> bool:
    vector = pg.Vector2(point.x - pieCenter.x, point.y - pieCenter.y).as_polar()

    if (vector[0] > r):
        return False
    else:
        if (angleStart > angleEnd):
            return (vector[1]+180 >= angleStart+180 or vector[1]+180 <= angleEnd+180)
        else:
            return (vector[1]+180 >= angleStart+180 and vector[1]+180 <= angleEnd+180)

# Defines a function returning the points that should be drawn as a polygon to emulate a pie.
def pointsInPie(pieCenter, r, startVector, endVector) -> list:
    # Starts list of points from the center of the pie
    points = [pieCenter]

    # Checks whether the angle is acute or obtuse
    if (startVector.as_polar()[1] < endVector.as_polar()[1]):
        pieAngle = abs(round(startVector.as_polar()[1] - endVector.as_polar()[1]))
    else:
        pass
        pieAngle = 360 - abs(round(startVector.as_polar()[1] - endVector.as_polar()[1]))

    # Adds a new point for each degree
    for i in range(pieAngle, 0, -1):
        pass
        points.append(pieCenter + startVector.rotate(i) * r)

    # Adds the center again so that the polygon returns to center
    points.append(pieCenter)

    # Assures that there is more than 2 points
    if (len(points) > 2):
        return points



# Creates a simple state machine that can loop easily through mod (%)
# Note: Should have been made with as a generator function
class State:
    # Initializes the state machine with a given number of modes (aka the maximum number of states)
    def __init__(self, modes) -> None:
        self.modes = modes
        self.current = 0
    
    def next(self) -> None:
        self.current += 1
        self.current %= self.modes

    def prior(self) -> None:
        self.current -= 1
        if (self.current < 0):
            self.current = self.modes - 1
