def inCircle(point, circlePos, r):
    if ((circlePos.x - point.x) * (circlePos.x - point.x) + (circlePos.y - point.y) * (circlePos.y - point.y) >= r*r):
        return False
    else:
        return True