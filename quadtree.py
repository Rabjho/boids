

class Boundary():
    def __init__(self, x, y, sizeX, sizeY) -> None:
        self.x = x
        self.y = y
        self.w = sizeX
        self.h = sizeY


    def contains(self, object) -> bool:
        return (object.position.x >= self.x - self.w and 
            object.position.x <= self.x + self.w and
            object.position.y >= self.y - self.h and
            object.position.y <= self.y + self.h
        )

    def intersects(self, range) -> bool:
        return not (range.x - range.w > self.x + self.w or 
        range.x + range.w < self.x - self.w or
        range.y - range.h > self.y + self.h or
        range.y + range.h < self.y - self.h 
        )

class QuadTree():
    def __init__(self, boundary, capacity) -> None:
        self.boundary = boundary
        self.capacity = capacity
        self.objects = []
        self.divided = False


    def insert(self, object) -> None:

        if (not self.boundary.contains(object)):
            return False
        
        if (len(self.objects) < self.capacity):
            self.objects.append(object)
            return True
        else:
            if (not self.divided):
                self.subdivide()
            elif (self.northwest.insert(object)): return True
            elif (self.northeast.insert(object)): return True
            elif (self.southwest.insert(object)): return True
            elif (self.southeast.insert(object)): return True

    def subdivide(self):
        nw = Boundary(self.boundary.x - self.boundary.w / 2, self.boundary.y - self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        ne = Boundary(self.boundary.x + self.boundary.w / 2, self.boundary.y - self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        sw = Boundary(self.boundary.x - self.boundary.w / 2, self.boundary.y + self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        se = Boundary(self.boundary.x + self.boundary.w / 2, self.boundary.y + self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        self.northwest = QuadTree(nw, self.capacity)
        self.northeast = QuadTree(ne, self.capacity)
        self.southwest = QuadTree(sw, self.capacity)
        self.southeast = QuadTree(se, self.capacity)
        self.divided = True

    def query(self, range):
        foundObjects = []
        if (not self.boundary.intersects(range)): return foundObjects

        else:
            for object in self.objects:
                if (range.contains(object)):
                    foundObjects.append(object)

            if (self.divided):
                foundObjects.extend(self.northwest.query(range))
                foundObjects.extend(self.northeast.query(range))
                foundObjects.extend(self.southwest.query(range))
                foundObjects.extend(self.southeast.query(range))

            return foundObjects
