# Import necessary dependancies
import pygame as pg
from pygame import gfxdraw
from random import randrange, uniform, choice
from auxfunctions import *
from quadtree import Boundary

# The overall entity class which is inherited from
class Entity:
    # Constructor which initializes variables, some of which have hardcoded default values
    def __init__(self, surface, position, radius, vLimit = 0, rotation=pg.Vector2(0,1), antiAliasing = True) -> None:
        self._surface = surface
        self.position = position
        self.radius = radius
        self.rotation = rotation

        self.angle = 120 # Could be added to arguments that can be controlled w/ default
        self.color = "#00afb9" # Could be added to arguments that can be controlled w/ default
        self.wallMargin = 125 # Could be added to arguments that can be controlled w/ default
        self.antiAliasing = antiAliasing
        self.walls = True # Could be added to arguments that can be controlled w/ default

        self.velocity = pg.Vector2(0,0)
        self.__clock = pg.time.Clock()

        # Trail handling
        self.trailing = False
        self.trailColor = pg.Color(150,150,150, 150)
        # self.trailPoints is a list of tuples, which contain the position of each point and a timestamp
        self.trailPoints = [(self.position, pg.time.get_ticks())]
        # The length of the trail in seconds
        self.trailLength = 0.3

        # Speedlimit
        self.vLimit = vLimit

    # Live function that is run each frame in main file
    def live(self) -> None:
        # Ticks internal clock
        self.__clock.tick()
        self._deltaTime = self.__clock.get_time() / 1000

        # Defines the angle of the "wings"
        self._rWingVector = self.rotation.rotate(self.angle)
        self._lWingVector = self.rotation.rotate(-self.angle)

        # Calls movement handler
        self._movement()
        # Calls rendering handler
        self._draw()

    # Rendering handler
    def _draw(self) -> None:
        # Points in each object as a list of x and y coordinates
        self._tip = [self.position.x + self.rotation.x * self.radius, self.position.y + self.rotation.y * self.radius]

        self._rWingTip = [self.position.x + self._rWingVector.x * (self.radius / 2), self.position.y + self._rWingVector.y * (self.radius / 2)]
        self._lWingTip = [self.position.x + self._lWingVector.x * (self.radius / 2), self.position.y + self._lWingVector.y * (self.radius / 2)]
        self._points = [self._tip, self._rWingTip, self.position, self._lWingTip]

        # Layering different renders to attain toggleable anti-aliasing
        if (self.antiAliasing):
            gfxdraw.aapolygon(self._surface, self._points, pg.Color(self.color))
        gfxdraw.filled_polygon(self._surface, self._points, pg.Color(self.color))

        # Removes old points in the trail
        while (pg.time.get_ticks() - self.trailPoints[0][1] > self.trailLength * 1000):
            self.trailPoints.pop(0)
        
        # Adds the new points in the trail
        self.trailPoints.append((self.position, pg.time.get_ticks()))

    # Movement handler
    def _movement(self) -> None:
        # Updates position according to velocity
        self.position = self.position + self.velocity * self._deltaTime   

        # Ensures movement speed is below threshold
        if (self.velocity.length() >= self.vLimit and self.vLimit != 0):     
            self.velocity = self.velocity.normalize() * self.vLimit

        # Makes drawn rotation the same as movement direction
        if (self.velocity.length() != 0):
            self.rotation = self.velocity.normalize()
    
    # Movement script to both fly through walls (ie. the screen) and to bounce of them if that is turned on.
    # It checks what edge of the screen has been flown over/through and acts accordingly by teleporting to opposite side or
    # reversing velocity and keeping within screen
    def _bounceOfWalls(self) -> None:
        if (self.position.x > self._surface.get_width()):
            if (self.walls):
                self.position.x = self._surface.get_width()
                self.velocity.x *= -1
            else:
                self.position.x = 0

        if (self.position.x < 0):
            if (self.walls):
                self.position.x = 0
                self.velocity.x *= -1
            else:
                self.position.x = self._surface.get_width()
            

        if (self.position.y > self._surface.get_height()):
            if (self.walls):
                self.position.y = self._surface.get_height()
                self.velocity.y *= -1
            else:
                self.position.y = 0

        if (self.position.y < 0):
            if (self.walls):
                self.position.y = 0
                self.velocity.y *= -1
            else:
                self.position.y = self._surface.get_height()

    # Small random movement script, which makes everything feel more organic
    def _randomness(self, strength=0) -> pg.Vector2:
        return pg.Vector2(uniform(-1,1), uniform(-1,1)).normalize() * strength

    # Handler for avoiding walls in a way that resembles the entities seeing them.
    # Note that it is not directly simulated but merely and forcefully attempted to make the simulation nicer
    def _avoidWalls(self, strength=0) -> pg.Vector2:
        xBoundries = (self.wallMargin, self._surface.get_width() - self.wallMargin)
        yBoundries = (self.wallMargin, self._surface.get_height() - self.wallMargin)
        avoidanceVector = pg.Vector2(0,0)

        if (self.position.x < xBoundries[0]):
            avoidanceVector.x = 1
        elif (self.position.x > xBoundries[1]):
            avoidanceVector.x = -1
        
        if (self.position.y < yBoundries[0]):
            avoidanceVector.y = 1
        elif (self.position.y > yBoundries[1]):
            avoidanceVector.y = -1
        
        if (avoidanceVector.length() != 0):
            return avoidanceVector.normalize() * strength

        return avoidanceVector

    # Wind effect that takes a direction and a speed and returns that vector
    def _wind(self, direction = pg.Vector2(0,0), strength=0) -> pg.Vector2:
        try:
            return direction.normalize() * strength
        except:
            return direction

    # Tail renderer that is somewhat poorly made using a list of polygons that is then looped back on itself.
    # The complete list is then spliced a bit to make more efficient as it is very costly on the computer (60 fps -> 30-50 fps w/ 100 boids)
    def drawTrail(self) -> None:
        if (self.trailing or self.demonstrating):
            try:
                gfxdraw.aapolygon(self._surface, (list(zip(*self.trailPoints))[0][::1]+list(zip(*self.trailPoints))[0][::-1])[::5], self.trailColor)
            except:
                pass

# Boid class which has inherited the Entity class
class Boid(Entity):
    # Constructor which initializes variables 
    def __init__(self, surface, boidsQuadTree, predatorQuadTree, vLimit, radius, searchRadius, cohesionStrength = 3, seperationStrength = 15, alignmentStrength = 7.5, predatorAvoidStrength = 20, predatorAwarenessFactor = 2) -> None:
        # Calls the parent class constructor
        super().__init__(surface, pg.Vector2(0,0), radius)

        # Places boid at random location with random rotation
        self.position = pg.Vector2(randrange(self._surface.get_width()), randrange(self._surface.get_height()))
        self.rotation = pg.Vector2(uniform(-1,1),uniform(-1,1)).normalize()

        # Internalizes the top most quadtree and inserts itself into it
        self.__boidsQuadTree = boidsQuadTree
        self.__boidsQuadTree.insert(self)
        self.__predatorsQuadTree = predatorQuadTree

        # Default demonstration config
        self.demonstrating = False
        self.demonstrateBoidColor = pg.Color(150,160,160,80)
        self.demonstratePredatorColor = pg.Color(255,120,120,20)

        # Takes constructor arguments and makes the available class wide
        self.searchRadius = searchRadius
        self.cohesionStrength = cohesionStrength
        self.seperationStrength = seperationStrength
        self.alignmentStrength = alignmentStrength
        self.predatorAvoidStrength = predatorAvoidStrength
        self.predatorAwarenessFactor = predatorAwarenessFactor
        self.vLimit = vLimit
        
    # Modifies live method of parent
    def live(self, windDirection = pg.Vector2(0,0), windStrength = 0, wallAvoid = 5, mouseTrackingStrength = 0) -> None:
        # Takes arguments that should be updated each frame and neatly updates internally
        self._windDirection = windDirection
        self._windStrength = windStrength
        self._wallAvoid = wallAvoid
        self._mouseTracking = mouseTrackingStrength

        # Calls parent live method
        super().live()

    # Modifies draw method of parent
    def _draw(self) -> None:
        # Enables demonstration and trail drawing
        self.__demonstrate()
        self.drawTrail()

        # Calls parent draw method
        super()._draw()


    def _movement(self) -> None:
    # START This is the O(n^2) check for boids and predators in range that checks all boids
        # self.boids = boids
        # self.enemies = predators

        # boidsInRange = [(boid, boid.color == self.color) for boid in self.boids if inPie(boid.position, self.position, self.searchRadius, self.lWingVector.as_polar()[1], self.rWingVector.as_polar()[1]) and boid.position != self.position]
        # predatorsInRange = [predator for predator in self.enemies if inPie(predator.position, self.position, self.searchRadius * self.predatorAwarenessFactor, self.lWingVector.as_polar()[1], self.rWingVector.as_polar()[1])]
    # END


    # This is the O(n*log(n)) check for boids in range using quadtree
        # Queries the quadtree and finds boids in that area and for each checks whether it is visible from this boids perspective
        # makes boidsInRange a list of tuples with the visible boid and whether it is in this boids family (i.e. if they're the same colour)
        boidsInRange = [(boid, boid.color == self.color) for boid in self.__boidsQuadTree.query(Boundary(self.position.x, self.position.y, self.searchRadius * 2, self.searchRadius * 2)) if inPie(boid.position, self.position, self.searchRadius, self._lWingVector.as_polar()[1], self._rWingVector.as_polar()[1]) and boid.position != self.position]

        # Does almost the same as boids except for the family check
        predatorsInRange = [predator for predator in self.__predatorsQuadTree.query(Boundary(self.position.x, self.position.y, self.searchRadius * self.predatorAwarenessFactor * 2, self.searchRadius * self.predatorAwarenessFactor * 2)) if inPie(predator.position, self.position, self.searchRadius * self.predatorAwarenessFactor, self._lWingVector.as_polar()[1], self._rWingVector.as_polar()[1])]

        # Resets base velocity
        baseVelocity = pg.Vector2(0,0)

        # Check if there are any boids to consider
        if (len(boidsInRange) != 0):
            # Resets the three basic rules of boid flocking simulation
            rule1 = pg.Vector2(0,0)
            rule2 = pg.Vector2(0,0)
            rule3 = pg.Vector2(0,0)

            # Iterates through boidsInRange and applies the three rules
            for boid in boidsInRange:
                rule1 += boid[0].position * boid[1]

                if (boid[0].position.distance_to(self.position) < self.radius * 2):
                    rule2 -= boid[0].position - self.position

                rule3 += boid[0].velocity * boid[1]

            # Assures that the rules aren't vectors of length 0 and adds them to baseVelocity (i.e. the aforementioned basic rules)
            if (rule1.length() != 0):
                baseVelocity += (rule1 / len(boidsInRange) - self.position).normalize() * self.cohesionStrength

            if (rule2.length() != 0):
                baseVelocity += rule2.normalize() * self.seperationStrength

            if (rule3.length() != 0):
                baseVelocity += (rule3 / len(boidsInRange)).normalize() * self.alignmentStrength

        # Ensures that there are predators in range
        if (len(predatorsInRange) != 0):
            # Resets predatorAvoidance vector
            predatorAvoidance = pg.Vector2(0,0)
            # Iterates through predators in range and finds their position
            for predator in predatorsInRange:
                predatorAvoidance += predator.position

            # Ensures that there are predators in range once more
            if (predatorAvoidance.length() != 0):
                # Subtracts average position of predators in relation to this boids position
                baseVelocity -= pg.Vector2((predatorAvoidance / len(predatorsInRange) - self.position)).normalize() * self.predatorAvoidStrength

        # List of active movement effects for ease 
        self.activeEffects = [
            baseVelocity, 
            self._randomness(5), 
            self._avoidWalls(self._wallAvoid * self.walls), 
            self._wind(self._windDirection, self._windStrength),
            self._trackMouse()
        ]

        # Applies each effect
        for effect in self.activeEffects:
            self.velocity += effect

        # Calls parent movement method
        super()._movement()

        # Ensures we're within the screen after position update
        self._bounceOfWalls()
     
    # Defines a tracking function of the mouse
    def _trackMouse(self) -> pg.Vector2:
        # Checks whether we should track the mouse
        if (not bool(self._mouseTracking)):
            return pg.Vector2(0,0)

        # Attempts to return the vector towards the mouse, however that could be right on top of the boid
        # In that case it returns a zero vector
        try:
            return (pg.Vector2(pg.mouse.get_pos()) - self.position).normalize() * self._mouseTracking
        except:
            return pg.Vector2(0,0)

    # Defines demonstration drawing function 
    def __demonstrate(self) -> None:
        # Checks whether we should be demonstrating
        if (self.demonstrating):
            # Draws boid search radius
            gfxdraw.filled_polygon(self._surface, pointsInPie(pg.Vector2(self.position.x, self.position.y), self.searchRadius * self.predatorAwarenessFactor, self._lWingVector, self._rWingVector), self.demonstratePredatorColor)
            # Draws predator search radius
            gfxdraw.filled_polygon(self._surface, pointsInPie(pg.Vector2(self.position.x, self.position.y), self.searchRadius, self._lWingVector, self._rWingVector), self.demonstrateBoidColor)

# Predator class which inherits Enitity
class Predator(Entity):
    # Construtor that initializes variables
    def __init__(self, surface, qtreePredator, boids, radius, vLimit = 0) -> None:
        # Calls parent constructor
        super().__init__(surface, pg.Vector2(0,0), radius, vLimit)
        
        # Places boid at random location with random rotation
        self.position = pg.Vector2(randrange(self._surface.get_width()), randrange(self._surface.get_height()))
        self.rotation = pg.Vector2(uniform(-1,1),uniform(-1,1)).normalize()

        # Takes a list of boids and chooses a target
        self.boids = boids
        self._target = choice(self.boids) 

        # Sets cooldown to time at initialization
        self._cooldownTargetChange = pg.time.get_ticks()

        # Internalizes the top most quadtree and inserts itself into it
        self.__qtreePredator = qtreePredator
        self.__qtreePredator.insert(self)

        # Chooses the cooldown of this predator to retarget 
        self._timeToNewTarget = uniform(3, 8)

        # Creates variable that controls the range, where within that the predator should also change target
        self._targetSwitchRange = 5

        self.color = "#000000"

    # Modifies live method of parent
    def live(self, windDirection = pg.Vector2(0, 0), windStrength = 0) -> None:
        # Takes arguments that should be updated each frame and neatly updates internally
        self._windDirection = windDirection
        self._windStrength = windStrength

        # Calls parent live method
        super().live()

    # Modifies movement method of parent
    def _movement(self) -> None:
        # Resets baseTracking vector
        baseTracking = pg.Vector2(0,0)

        # Finds vector to the chosen target and ensures that it isn't of length 0
        if ((pg.Vector2(self._target.position)-pg.Vector2(self.position)).length() != 0):
            baseTracking = (self._target.position-self.position).normalize() * self.vLimit
        else:
            baseTracking = pg.Vector2(0,0)
        
        # List of active movement effects
        self.activeEffects = [
            baseTracking, 
            self._avoidWalls(5 * self.walls), 
            self._wind(self._windDirection, self._windStrength)
        ]

        # Iterates through active effects and applies them
        for effect in self.activeEffects:
            self.velocity += effect

        # Changes target if it has been too long since last change or the target is within range
        if (pg.time.get_ticks() - self._cooldownTargetChange > self._timeToNewTarget * 1000 or pg.Vector2(self.position).distance_to(pg.Vector2(self._target.position)) < self._targetSwitchRange):
            self._target = choice(self.boids)

            # Resets cooldown
            self._cooldownTargetChange = pg.time.get_ticks()

        # Calls parent movement method
        super()._movement()    

        # Ensures the predator is within the screen after movement update
        self._bounceOfWalls()

# WindPointer class (i.e. the point in the bottom left that shows the wind's direction)
# This could be done as a one off, but the entity class was able to easily draw an arrow/pointer
# The WindPointer is therefore a child of the Entity class
class WindPointer(Entity):
    # Constructor with defaults that make it stationary and a margin variable
    def __init__(self, surface, radius = 15, margin = 30, antiAliasing=True) -> None:
        # This is the number of pixels that are between the center of the pointer and the bottom and left sides
        self.margin = margin 

        # Calls parent constructor method
        super().__init__(surface, pg.Vector2(self.margin, surface.get_height()-self.margin), radius, 0, pg.Vector2(0, 1), antiAliasing)

        self.color = "#6b6b8c"

    # Modifies live method of parent
    def live(self, windDirection = pg.Vector2(0,1)) -> None:
        # Sets rotation of drawn object to the wind's direction
        self.rotation = windDirection.normalize()

        # Ensures that the position stays relative when the window changes 
        self.position = pg.Vector2(self.margin, self._surface.get_height()-self.margin)

        # Calls parent live method
        super().live()