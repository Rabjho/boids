from ctypes import alignment
import sys,pygame as pg
from pygame import gfxdraw
from random import randrange, uniform, choice
from auxFunctions import *


class Entity:
    def __init__(self, surface, position, radius, vLimit, rotation=pg.Vector2(0,1), antiAliasing = True):
        self.surface = surface
        self.position = position
        self.vLimit = vLimit
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


        self.trailing = False
        self.trailColor = pg.Color(150,150,150, 150)
        self.trailPoints = [(self.position, pg.time.get_ticks())]
        self.trailLength = 0.3



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


        if (pg.time.get_ticks() - self.trailPoints[0][1] > self.trailLength * 1000):
            self.trailPoints.pop(0)
        
        self.trailPoints.append((self.position, pg.time.get_ticks()))

    def movement(self):

        self.position = self.position + self.velocity * self.deltaTime   

        if (self.velocity.length() >= self.vLimit and self.vLimit != 0):
            
            self.velocity = self.velocity.normalize() * self.vLimit


        try:
            self.rotation = self.velocity.normalize()
        except:
            pass            
 
    def live(self):
        self.clock.tick()

        self.deltaTime = self.clock.get_time() / 1000

        self.draw()
        self.movement()
    
    def bounceOfWalls(self):
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

    def randomness(self, strength=0):
        return pg.Vector2(uniform(-1,1), uniform(-1,1)).normalize() * strength

    def drawTrail(self):
        if (self.trailing or self.demonstrating):
            try:
                gfxdraw.aapolygon(self.surface, (list(zip(*self.trailPoints))[0][::1]+list(zip(*self.trailPoints))[0][::-1])[::5], self.trailColor)
            except:
                pass

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

    def wind(self, direction = pg.Vector2(0,0), strength=0):
        try:
            return direction.normalize() * strength
        except:
            return direction




class Boid(Entity):
    def __init__(self, surface, radius, searchRadius, vLimit):
        super().__init__(surface, pg.Vector2(0,0), radius, vLimit)
        self.position = pg.Vector2(randrange(self.surface.get_width()), randrange(self.surface.get_height()))
        self.rotation = pg.Vector2(uniform(-1,1),uniform(-1,1)).normalize()
        self.searchRadius = searchRadius
        self.boidsInRange = []

        self.demonstrating = False
        self.demonstrateBoidColor = pg.Color(150,160,160,80)
        self.demonstratePredatorColor = pg.Color(255,120,120,20)


    def draw(self):
        self.demonstrate()

        self.drawTrail()
        super().draw()


    def movement(self):

        self.baseVelocity = pg.Vector2(0,0)

        if (len(self.boidsInRange) != 0):
            rule1 = pg.Vector2(0,0)
            rule2 = pg.Vector2(0,0)
            rule3 = pg.Vector2(0,0)

            for boid in self.boidsInRange:
                rule1 += boid[0].position * boid[1]

                if (boid[0].position.distance_to(self.position) < self.radius * 2):
                    rule2 -= boid[0].position - self.position

                rule3 += boid[0].velocity * boid[1]


            if (rule1.length() != 0):
                self.baseVelocity += pg.Vector2((rule1 / len(self.boidsInRange) - self.position)).normalize() * self.cohesionStrength

            if (rule2.length() != 0):
                self.baseVelocity += rule2.normalize() * self.seperationStrength

            if (rule3.length() != 0):
                self.baseVelocity += pg.Vector2((rule3 / len(self.boidsInRange))).normalize() * self.alignmentStrength


        if (len(self.predatorsInRange) != 0):
            predatorAvoidance = pg.Vector2(0,0)
            for predator in self.predatorsInRange:
                predatorAvoidance += predator.position

            if (predatorAvoidance.length() != 0):
                    self.baseVelocity -= pg.Vector2((predatorAvoidance / len(self.predatorsInRange) - self.position)).normalize() * self.predatorAvoidStrength


        self.activeEffects = [self.baseVelocity, self.randomness(10), self.avoidWalls(5 * self.walls), self.wind(self.windDirection, self.windStrength)]
        # self.activeEffects = [self.baseVelocity]
        for effect in self.activeEffects:
            self.velocity += effect



        super().movement()

        self.bounceOfWalls()

    def live(self, boids, predators, cohesionStrength = 3, seperationStrength = 15, alignmentStrength = 7.5, predatorAvoidStrength = 20, predatorAwarenessFactor = 2, windDirection = pg.Vector2(0,0), windStrength = 0):
        self.cohesionStrength = 3
        self.seperationStrength = 15
        self.alignmentStrength = 7.5
        self.predatorAvoidStrength = 20
        self.predatorAwarenessFactor = 2
        
        self.windDirection = windDirection
        self.windStrength = windStrength

        self.boids = boids
        self.enemies = predators

        self.boidsInRange = [(boid, boid.color == self.color) for boid in self.boids if inPie(boid.position, self.position, self.searchRadius, self.lWingVector.as_polar()[1], self.rWingVector.as_polar()[1]) and boid.position != self.position]
        self.predatorsInRange = [predator for predator in self.enemies if inPie(predator.position, self.position, self.searchRadius * self.predatorAwarenessFactor, self.lWingVector.as_polar()[1], self.rWingVector.as_polar()[1])]

        super().live()


    def demonstrate(self):
        if (self.demonstrating):
            gfxdraw.filled_polygon(self.surface, drawPie(pg.Vector2(self.position.x, self.position.y), self.searchRadius * self.predatorAwarenessFactor, self.lWingVector, self.rWingVector), self.demonstratePredatorColor)
            gfxdraw.filled_polygon(self.surface, drawPie(pg.Vector2(self.position.x, self.position.y), self.searchRadius, self.lWingVector, self.rWingVector), self.demonstrateBoidColor)



# Former functions for the three base rules of the boids algorithm. 
# They have been merged to avoid iterating through boidsInRange thrice.

    # def cohesion(self, strength=0):
    #     centerBoids = pg.Vector2(0,0)
    #     if (len(self.boidsInRange) != 0):
    #         for boid in self.boidsInRange:
    #             centerBoids += boid[0].position * boid[1]

    #         centerBoids = pg.Vector2((centerBoids / len(self.boidsInRange) - self.position))
    #         return centerBoids.normalize() * strength

    #     return centerBoids

    # def seperation(self, strength=0):
    #     avoidanceVector = pg.Vector2(0,0)
    #     if (len(self.boidsInRange) != 0):
    #         for boid in self.boidsInRange:
    #             if (boid[0].position.distance_to(self.position) < self.radius * 2):
    #                 avoidanceVector -= boid[0].position - self.position
    #         if (avoidanceVector.length() != 0):
    #             return avoidanceVector.normalize() * strength

    #     return avoidanceVector

    # def alignment(self, strength=0):
    #     directionBoids = pg.Vector2(0,0)
    #     if (len(self.boidsInRange) != 0):
    #         for boid in self.boidsInRange:
    #             directionBoids += boid[0].velocity * boid[1]

    #         directionBoids = pg.Vector2((directionBoids / len(self.boidsInRange)))
    #         if (directionBoids.length() != 0):
    #             return directionBoids.normalize() * strength

    #     return directionBoids

class Predator(Entity):
    def __init__(self, surface, radius, boids, vLimit):
        super().__init__(surface, pg.Vector2(0,0), radius, vLimit)

        self.position = pg.Vector2(randrange(self.surface.get_width()), randrange(self.surface.get_height()))
        self.rotation = pg.Vector2(uniform(-1,1),uniform(-1,1)).normalize()
        self.vLimit = vLimit
        self.color = "#000000"
        self.trackingStrength = 10

        self.boids = boids
        self.target = choice(self.boids) 
        self.timeToNewTarget = uniform(3, 8)
        self.cooldownTargetChange = pg.time.get_ticks()

    def live(self, windDirection = pg.Vector2(0,0), windStrength = 0):
        self.windDirection = windDirection
        self.windStrength = windStrength
        super().live()

    def movement(self):
        self.baseTracking = (pg.Vector2(self.target.position)-pg.Vector2(self.position)).normalize() * self.trackingStrength
        
        self.activeEffects = [self.baseTracking, self.avoidWalls(5 * self.walls), self.wind()]

        for effect in self.activeEffects:
            self.velocity += effect

        if (pg.time.get_ticks() - self.cooldownTargetChange > self.timeToNewTarget * 1000 or pg.Vector2(self.position).distance_to(pg.Vector2(self.target.position)) < 5):
            self.target = choice(self.boids)
            self.cooldownTargetChange = pg.time.get_ticks()

        super().movement()
        
        self.bounceOfWalls()

class WindPointer(Entity):
    def __init__(self, surface, radius = 15, margin = 30, rotation=pg.Vector2(0, 1), antiAliasing=True):
        vLimit = 0
        self.margin = margin
        self.surface = surface
        position = pg.Vector2(self.margin, self.surface.get_height()-self.margin)
        super().__init__(surface, position, radius, vLimit, rotation, antiAliasing)

        self.color = "#6b6b8c"

    def movement(self):
        super().movement()

        self.position = pg.Vector2(self.margin, self.surface.get_height()-self.margin)

    def live(self, windDirection = pg.Vector2(0,1)):
        self.rotation = windDirection.normalize()
        super().live()