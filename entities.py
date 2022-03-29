import sys,pygame as pg
from pygame import gfxdraw
from random import randrange, uniform, getrandbits
from auxfunctions import *


class Entity:
    def __init__(self, surface, position, radius, rotation=pg.Vector2(0,1), antiAliasing = True):
        self.surface = surface
        self.position = position
        self.radius = radius
        self.rotation = rotation
        self.angle = 120 # Add to arguments that can be controlled w/ default
        self.color = "#00afb9" # Add to arguments that can be controlled w/ default
        self.wallMargin = 125 # Add to arguments that can be controlled w/ default
        self.antiAliasing = antiAliasing
        self.walls = True # Add to arguments that can be controlled w/ default



        self.velocity = pg.Vector2(0,0)
        self.clock = pg.time.Clock()

        self.rWingVector = self.rotation.rotate(self.angle)
        self.lWingVector = self.rotation.rotate(-self.angle)



    def draw(self):
        self.rWingVector = self.rotation.rotate(self.angle)
        self.lWingVector = self.rotation.rotate(-self.angle)
        self.tip = [self.position.x + self.rotation.x * self.radius, self.position.y + self.rotation.y * self.radius]

        self.rWingTip = [self.position.x + self.rWingVector.x * (self.radius / 2), self.position.y + self.rWingVector.y * (self.radius / 2)]
        self.lWingTip = [self.position.x + self.lWingVector.x * (self.radius / 2), self.position.y + self.lWingVector.y * (self.radius / 2)]
        self.points = [self.tip, self.rWingTip, self.position, self.lWingTip]

        if (self.antiAliasing):
            gfxdraw.aapolygon(self.surface, self.points, pg.Color(self.color))

        gfxdraw.filled_polygon(self.surface, self.points, pg.Color(self.color))



    def movement(self):

        self.position = self.position + self.velocity * self.deltaTime    


    def live(self):
        self.clock.tick()

        self.deltaTime = self.clock.get_time() / 1000

        self.draw()
        self.movement()


class Boid(Entity):
    def __init__(self, surface, radius, searchRadius = 50, vLimit = 100):
        super().__init__(surface, pg.Vector2(0,0), radius)
        self.position = pg.Vector2(randrange(self.surface.get_width()), randrange(self.surface.get_height()))
        self.rotation = pg.Vector2(uniform(-1,1),uniform(-1,1)).normalize()
        self.searchRadius = searchRadius
        self.vLimit = vLimit

    def movement(self):
        self.activeEffects = [self.cohesion(3), self.seperation(15), self.alignment(7.5), self.randomness(10), self.avoidWalls(5 * self.walls)]
        
        for effect in self.activeEffects:
            self.velocity += effect

        try:
            self.rotation = self.velocity.normalize()
        except:
            pass            

        if self.velocity.length() >= self.vLimit:
            self.velocity = self.velocity / self.velocity.length() * self.vLimit

        super().movement()

        
        if (self.position.x > self.surface.get_width()):
            if (self.walls):
                self.position.x = self.surface.get_width()
                self.velocity.x *= -1
            else:
                self.position.x = 0

        if (self.position.x < 0):
            if (self.walls):
                self.position.x = 0
                self.velocity.x *= -1
            else:
                self.position.x = self.surface.get_width()
            

        if (self.position.y > self.surface.get_height()):
            if (self.walls):
                self.position.y = self.surface.get_height()
                self.velocity.y *= -1
            else:
                self.position.y = 0

        if (self.position.y < 0):
            if (self.walls):
                self.position.y = 0
                self.velocity.y *= -1
            else:
                self.position.y = self.surface.get_height()

                
        

    def live(self, boids):
        self.boids = boids

        self.boidsInRange = [boid for boid in self.boids if inPie(boid.position,self.position, self.searchRadius, self.lWingVector.as_polar()[1], self.rWingVector.as_polar()[1]) and boid.position != self.position]
        super().live()

    def cohesion(self, strength=0):
        centerBoids = pg.Vector2(0,0)
        if (len(self.boidsInRange) != 0):
            for boid in self.boidsInRange:
                centerBoids += boid.position

            centerBoids = pg.Vector2((centerBoids / len(self.boidsInRange) - self.position))
            return centerBoids.normalize() * strength

        return centerBoids

    def seperation(self, strength=0):
        avoidanceVector = pg.Vector2(0,0)
        if (len(self.boidsInRange) != 0):
            for boid in self.boidsInRange:
                if (boid.position.distance_to(self.position) < self.radius * 2):
                    avoidanceVector -= boid.position - self.position
            if (avoidanceVector.length() != 0):
                return avoidanceVector.normalize() * strength

        return avoidanceVector

    def alignment(self, strength=0):
        directionBoids = pg.Vector2(0,0)
        if (len(self.boidsInRange) != 0):
            for boid in self.boidsInRange:
                directionBoids += boid.velocity

            directionBoids = pg.Vector2((directionBoids / len(self.boidsInRange)))
            if (directionBoids.length() != 0):
                return directionBoids.normalize() * strength

        return directionBoids


    def randomness(self, strength=0):
        return pg.Vector2(uniform(-1,1),uniform(-1,1)).normalize() * strength

    def avoidWalls(self, strength=0):
        xBoundries = (self.wallMargin, self.surface.get_width() - self.wallMargin)
        yBoundries = (self.wallMargin, self.surface.get_height() - self.wallMargin)
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

    def demonstrate(self):
        # gfxdraw.filled_circle(self.surface, round(self.position.x), round(self.position.y), self.searchRadius, pg.Color(150,150,150,80))        
        # drawPie(self.surface, pg.Vector2(self.position.x, self.position.y), self.searchRadius, self.lWingVector, self.rWingVector)
        gfxdraw.filled_polygon(self.surface, drawPie(pg.Vector2(self.position.x, self.position.y), self.searchRadius, self.lWingVector, self.rWingVector), pg.Color(150,150,150,80))

