import sys,pygame as pg
from pygame import gfxdraw
from random import randrange, uniform
from auxfunctions import *


class Entity:
    # size is the size from the center to the "tip" of the entity
    def __init__(self, surface, position, radius, rotation=pg.Vector2(0,1), antiAliasing = True):
        self.surface = surface
        self.position = position
        self.radius = radius
        self.rotation = rotation
        self.angle = 120
        self.color = "#00afb9"
        self.velocity = pg.Vector2(0,0)
        self.clock = pg.time.Clock()

        self.rWingVector = self.rotation.rotate(self.angle)
        self.lWingVector = self.rotation.rotate(-self.angle)

        self.antiAliasing = antiAliasing 


    def draw(self):
        self.tip = [self.position.x + self.rotation.x * self.radius, self.position.y + self.rotation.y * self.radius]
        self.rWingVector = self.rotation.rotate(self.angle)
        self.lWingVector = self.rotation.rotate(-self.angle)

        self.rWingTip = [self.position.x + self.rWingVector.x * self.radius / 2, self.position.y + self.rWingVector.y * self.radius / 2]
        self.lWingTip = [self.position.x + self.lWingVector.x * self.radius / 2, self.position.y + self.lWingVector.y * self.radius / 2]
        self.points = [self.tip, self.rWingTip, self.position, self.lWingTip]

        if (self.antiAliasing):
            gfxdraw.aapolygon(self.surface, self.points, pg.Color(self.color))

        gfxdraw.filled_polygon(self.surface, self.points, pg.Color(self.color))



    def movement(self):

        self.position = self.position + self.velocity * self.deltaTime

        if (self.position.x >= self.surface.get_width()):
            self.position.x = self.surface.get_width()
            self.velocity.x *= -1
        if (self.position.x <= 0):
            self.position.x = 0
            self.velocity.x *= -1

        if (self.position.y >= self.surface.get_height()):
            self.position.y = self.surface.get_height()
            self.velocity.y *= -1

        if (self.position.y <= 0):
            self.position.y = 0
            self.velocity.y *= -1
            


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
        self.activeEffects = [self.cohesion(1), self.seperation(), self.alignment(), self.randomness()]
        
        for effect in self.activeEffects:
            self.velocity += effect

        try:
            self.rotation = self.velocity.normalize()
        except:
            pass            

        if self.velocity.length() >= self.vLimit:
            self.velocity = self.velocity / self.velocity.length() * self.vLimit

        super().movement()

    def live(self, boids):
        self.boids = boids

        self.boidsInRange = [boid for boid in self.boids if inPie(boid.position,self.position, self.searchRadius, self.lWingVector.as_polar()[1], self.rWingVector.as_polar()[1]) and boid.position != self.position]
        super().live()

    def cohesion(self, strength=0):
        self.centerBoids = pg.Vector2(0,0)
        if (len(self.boidsInRange) != 0):
            for boid in self.boidsInRange:
                self.centerBoids += boid.position

            return pg.Vector2((self.centerBoids / len(self.boidsInRange) - self.position)).normalize() * strength
        else:
            return pg.Vector2(0,0)

    # Remember to normalize output
    def seperation(self, strength=0):
        return pg.Vector2(0,0)


    # Remember to normalize output
    def alignment(self, strength=0):
        return pg.Vector2(0,0)

    # Remember to normalize output
    def randomness(self, strength=0):
        return pg.Vector2(0,0)

    def demonstrate(self):
        gfxdraw.filled_circle(self.surface, round(self.position.x), round(self.position.y), self.searchRadius, pg.Color(150,150,150,80))
