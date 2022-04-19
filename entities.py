from ctypes import alignment
import pygame as pg
from pygame import gfxdraw
from random import randrange, uniform, choice
from auxfunctions import *
from quadtree import Boundary


class Entity:
    def __init__(self, surface, position, radius, vLimit = 0, rotation=pg.Vector2(0,1), antiAliasing = True) -> None:
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

        self.trailing = False
        self.trailColor = pg.Color(150,150,150, 150)
        self.trailPoints = [(self.position, pg.time.get_ticks())]
        self.trailLength = 0.3

        self.vLimit = vLimit

    def live(self) -> None:
        self.clock.tick()
        self.deltaTime = self.clock.get_time() / 1000

        self.rWingVector = self.rotation.rotate(self.angle)
        self.lWingVector = self.rotation.rotate(-self.angle)

        self.draw()
        self.movement()
        self.draw()

    def draw(self) -> None:
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


    def movement(self) -> None:
        self.position = self.position + self.velocity * self.deltaTime   

        if (self.velocity.length() >= self.vLimit and self.vLimit != 0):     
            self.velocity = self.velocity.normalize() * self.vLimit

        if (self.velocity.length() != 0):
            self.rotation = self.velocity.normalize()
    
    def bounceOfWalls(self) -> None:
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

    def randomness(self, strength=0) -> pg.Vector2:
        return pg.Vector2(uniform(-1,1), uniform(-1,1)).normalize() * strength


    def avoidWalls(self, strength=0) -> pg.Vector2:
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

    def wind(self, direction = pg.Vector2(0,0), strength=0) -> pg.Vector2:
        try:
            return direction.normalize() * strength
        except:
            return direction

# TODO Recode draw tail using individual line segments. This is just a quick and done version that takes fps from 60 to 30-50 w/ 100 boids
    def drawTrail(self) -> None:
        if (self.trailing or self.demonstrating):
            try:
                gfxdraw.aapolygon(self.surface, (list(zip(*self.trailPoints))[0][::1]+list(zip(*self.trailPoints))[0][::-1])[::5], self.trailColor)
            except:
                pass

class Boid(Entity):
    def __init__(self, surface, boidsQuadTree, predatorQuadTree, vLimit, radius, searchRadius, cohesionStrength = 3, seperationStrength = 15, alignmentStrength = 7.5, predatorAvoidStrength = 20, predatorAwarenessFactor = 2) -> None:
        super().__init__(surface, pg.Vector2(0,0), radius)
        self.position = pg.Vector2(randrange(self.surface.get_width()), randrange(self.surface.get_height()))
        self.rotation = pg.Vector2(uniform(-1,1),uniform(-1,1)).normalize()

        self.boidsQuadTree = boidsQuadTree
        self.boidsQuadTree.insert(self)
        self.predatorsQuadTree = predatorQuadTree

        self.demonstrating = False
        self.demonstrateBoidColor = pg.Color(150,160,160,80)
        self.demonstratePredatorColor = pg.Color(255,120,120,20)


        self.searchRadius = searchRadius
        self.cohesionStrength = cohesionStrength
        self.seperationStrength = seperationStrength
        self.alignmentStrength = alignmentStrength
        self.predatorAvoidStrength = predatorAvoidStrength
        self.predatorAwarenessFactor = predatorAwarenessFactor
        self.vLimit = vLimit
        

    def live(self, windDirection = pg.Vector2(0,0), windStrength = 0, wallAvoid = 5, mouseTrackingStrength = 0) -> None:

        self.windDirection = windDirection
        self.windStrength = windStrength
        self.wallAvoid = wallAvoid
        self.mouseTracking = mouseTrackingStrength

        super().live()

    def draw(self) -> None:
        self.demonstrate()
        self.drawTrail()
        super().draw()


    def movement(self) -> None:
# This is the O(n^2) check for boids and predators in range that checks all boids
        # self.boids = boids
        # self.enemies = predators

        # boidsInRange = [(boid, boid.color == self.color) for boid in self.boids if inPie(boid.position, self.position, self.searchRadius, self.lWingVector.as_polar()[1], self.rWingVector.as_polar()[1]) and boid.position != self.position]
        # predatorsInRange = [predator for predator in self.enemies if inPie(predator.position, self.position, self.searchRadius * self.predatorAwarenessFactor, self.lWingVector.as_polar()[1], self.rWingVector.as_polar()[1])]

# This is the O(n*log(n)) check for boids in range using quadtree
        boidsInRange = [(boid, boid.color == self.color) for boid in self.boidsQuadTree.query(Boundary(self.position.x, self.position.y, self.searchRadius * 2, self.searchRadius * 2)) if inPie(boid.position, self.position, self.searchRadius, self.lWingVector.as_polar()[1], self.rWingVector.as_polar()[1]) and boid.position != self.position]
        predatorsInRange = [predator for predator in self.predatorsQuadTree.query(Boundary(self.position.x, self.position.y, self.searchRadius * self.predatorAwarenessFactor * 2, self.searchRadius * self.predatorAwarenessFactor * 2)) if inPie(predator.position, self.position, self.searchRadius * self.predatorAwarenessFactor, self.lWingVector.as_polar()[1], self.rWingVector.as_polar()[1])]

        baseVelocity = pg.Vector2(0,0)

        if (len(boidsInRange) != 0):
            rule1 = pg.Vector2(0,0)
            rule2 = pg.Vector2(0,0)
            rule3 = pg.Vector2(0,0)

            for boid in boidsInRange:
                rule1 += boid[0].position * boid[1]

                if (boid[0].position.distance_to(self.position) < self.radius * 2):
                    rule2 -= boid[0].position - self.position

                rule3 += boid[0].velocity * boid[1]


            if (rule1.length() != 0):
                baseVelocity += pg.Vector2((rule1 / len(boidsInRange) - self.position)).normalize() * self.cohesionStrength

            if (rule2.length() != 0):
                baseVelocity += rule2.normalize() * self.seperationStrength

            if (rule3.length() != 0):
                baseVelocity += pg.Vector2((rule3 / len(boidsInRange))).normalize() * self.alignmentStrength


        if (len(predatorsInRange) != 0):
            predatorAvoidance = pg.Vector2(0,0)
            for predator in predatorsInRange:
                predatorAvoidance += predator.position

            if (predatorAvoidance.length() != 0):
                    baseVelocity -= pg.Vector2((predatorAvoidance / len(predatorsInRange) - self.position)).normalize() * self.predatorAvoidStrength


        # self.velocity = baseVelocity
        self.activeEffects = [
            baseVelocity, 
            self.randomness(5), 
            self.avoidWalls(self.wallAvoid * self.walls), 
            self.wind(self.windDirection, self.windStrength),
            self.trackMouse()
        ]

        for effect in self.activeEffects:
            self.velocity += effect

        super().movement()
        self.bounceOfWalls()
     
    def trackMouse(self) -> pg.Vector2:
        if (not bool(self.mouseTracking)):
            return pg.Vector2(0,0)
        try:
            return (pg.Vector2(pg.mouse.get_pos()) - self.position).normalize() * self.mouseTracking
        except:
            return pg.Vector2(0,0)

    def demonstrate(self) -> None:
        if (self.demonstrating):
            gfxdraw.filled_polygon(self.surface, drawPie(pg.Vector2(self.position.x, self.position.y), self.searchRadius * self.predatorAwarenessFactor, self.lWingVector, self.rWingVector), self.demonstratePredatorColor)
            gfxdraw.filled_polygon(self.surface, drawPie(pg.Vector2(self.position.x, self.position.y), self.searchRadius, self.lWingVector, self.rWingVector), self.demonstrateBoidColor)


class Predator(Entity):
    def __init__(self, surface, qtreePredator, boids, radius, vLimit = 0) -> None:
        super().__init__(surface, pg.Vector2(0,0), radius, vLimit)
        
        self.position = pg.Vector2(randrange(self.surface.get_width()), randrange(self.surface.get_height()))
        self.rotation = pg.Vector2(uniform(-1,1),uniform(-1,1)).normalize()
        self.boids = boids
        self.target = choice(self.boids) 
        self.cooldownTargetChange = pg.time.get_ticks()

        self.qtreePredator = qtreePredator
        self.qtreePredator.insert(self)

        self.timeToNewTarget = uniform(3, 8)
        self.targetSwitchRange = 5
        self.color = "#000000"


    def live(self, windDirection = pg.Vector2(0, 0), windStrength = 0) -> None:
        self.windDirection = windDirection
        self.windStrength = windStrength
        super().live()

    def movement(self) -> None:
        self.baseTracking = pg.Vector2(0,0)
        if ((pg.Vector2(self.target.position)-pg.Vector2(self.position)).length() != 0):
            self.baseTracking = (pg.Vector2(self.target.position)-pg.Vector2(self.position)).normalize() * self.vLimit
        else:
            self.baseTracking = pg.Vector2(0,0)
        
        self.activeEffects = [
            self.baseTracking, 
            self.avoidWalls(5 * self.walls), 
            self.wind(self.windDirection, self.windStrength)
        ]

        for effect in self.activeEffects:
            self.velocity += effect

        if (pg.time.get_ticks() - self.cooldownTargetChange > self.timeToNewTarget * 1000 or pg.Vector2(self.position).distance_to(pg.Vector2(self.target.position)) < self.targetSwitchRange):
            self.target = choice(self.boids)
            self.cooldownTargetChange = pg.time.get_ticks()

        super().movement()    
        self.bounceOfWalls()

class WindPointer(Entity):
    def __init__(self, surface, radius = 15, margin = 30, antiAliasing=True) -> None:
        self.margin = margin
        self.surface = surface
        position = pg.Vector2(self.margin, self.surface.get_height()-self.margin)
        super().__init__(surface, position, radius, 0, pg.Vector2(0, 1), antiAliasing)

        self.color = "#6b6b8c"

    def live(self, windDirection = pg.Vector2(0,1)) -> None:
        self.rotation = windDirection.normalize()
        self.position = pg.Vector2(self.margin, self.surface.get_height()-self.margin)
        super().live()