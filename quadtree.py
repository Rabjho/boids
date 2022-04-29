# Defines a boundary class that can check whether an object is within its boundaries or whether another boundary intersects it
class Boundary():
    # Initializes the boundary with coords to center and total width+height
    def __init__(self, x, y, sizeX, sizeY) -> None:
        self.x = x
        self.y = y
        self.w = sizeX
        self.h = sizeY

    # Defines function that checks whether an object is within boundary
    def contains(self, object) -> bool:
        return (
            object.position.x >= self.x - self.w and 
            object.position.x <= self.x + self.w and
            object.position.y >= self.y - self.h and
            object.position.y <= self.y + self.h
        )

    # Defines funtion that checks whether another boundary (aka range) intersects the current one 
    def intersects(self, range) -> bool:
        return not (
            range.x - range.w > self.x + self.w or 
            range.x + range.w < self.x - self.w or
            range.y - range.h > self.y + self.h or
            range.y + range.h < self.y - self.h 
        )

# Defines the quadtree object
class Quadtree():
    # Defines inizialisation function that takes a boundary and a capacity of each boundary
    def __init__(self, boundary, capacity) -> None:
        self.__boundary = boundary
        self.capacity = capacity

        # Creates a list of objects within this boundary
        self._objects = []

        # Creates a boolean that ensures proper splitting
        self._divided = False

    # Defines the insertion function, where an object is placed within the quadtree
    # Also returns true if it is succesfull and false if not
    def insert(self, object) -> bool:
        # Checks if the object can be inserted into the current quadtree
        if (not self.__boundary.contains(object)):
            return False
        
        # Checks if the quadtree can hold more objects, otherwise subdivide if it isn't already.
        # If it is subdivided call the insert funtion of each quadtree
        if (len(self._objects) < self.capacity):
            self._objects.append(object)
            return True
        else:
            if (not self._divided):
                self.__subdivide()
            elif (self.__northwest.insert(object)): return True
            elif (self.__northeast.insert(object)): return True
            elif (self.__southwest.insert(object)): return True
            elif (self.__southeast.insert(object)): return True

    # Defines subdividing function that creates 4 quadtrees recursively until satisfactory. Also flags this quadtree as divided
    def __subdivide(self):
        self.__northwest = Quadtree(Boundary(self.__boundary.x - self.__boundary.w / 2, self.__boundary.y - self.__boundary.h / 2, self.__boundary.w / 2, self.__boundary.h / 2), self.capacity)
        self.__northeast = Quadtree(Boundary(self.__boundary.x + self.__boundary.w / 2, self.__boundary.y - self.__boundary.h / 2, self.__boundary.w / 2, self.__boundary.h / 2), self.capacity)
        self.__southwest = Quadtree(Boundary(self.__boundary.x - self.__boundary.w / 2, self.__boundary.y + self.__boundary.h / 2, self.__boundary.w / 2, self.__boundary.h / 2), self.capacity)
        self.__southeast = Quadtree(Boundary(self.__boundary.x + self.__boundary.w / 2, self.__boundary.y + self.__boundary.h / 2, self.__boundary.w / 2, self.__boundary.h / 2), self.capacity)
        self._divided = True

    # Defines the query function which recursively queries the quadtree for objects
    def query(self, range):
        # Starts the recursive query by making a new empty list and checking if it is intersected
        foundObjects = []
        if (not self.__boundary.intersects(range)): 
            return foundObjects

        else:
            # Adds objects of this quadtree
            for object in self._objects:
                if (range.contains(object)):
                    foundObjects.append(object)

            # Recursively queries quadtrees beneath this one which then return their contained objects.
            # These are then added to this ones list
            if (self._divided):
                foundObjects.extend(self.__northwest.query(range))
                foundObjects.extend(self.__northeast.query(range))
                foundObjects.extend(self.__southwest.query(range))
                foundObjects.extend(self.__southeast.query(range))

            # Ultimately return the found objects of this quadtree and all it's "children"
            return foundObjects
