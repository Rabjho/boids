from logging import exception
from random import randrange
import sys,pygame as pg
from math import *
from pygame import gfxdraw


def inCircle(point, circlePos, r):
    if ((circlePos.x - point.x) * (circlePos.x - point.x) + (circlePos.y - point.y) * (circlePos.y - point.y) >= r*r):
        return False
    else:
        return True

class Entity:
    # size is the size from the center to the "tip" of the entity
    def __init__(self, surface, position, radius, rotation=pg.Vector2(0,1)):
        self.id = id
        self.surface = surface
        self.position = position
        self.radius = radius
        self.rotation = rotation
        self.angle = 120
        self.color = (29,222,85)
        self.color = "#5a8ff5"
        self.velocity = pg.Vector2(0,0)
        self.clock = pg.time.Clock()

    def draw(self):
        self.tip = [self.position.x + self.rotation.x * self.radius, self.position.y + self.rotation.y * self.radius]
        self.rWingVector = self.rotation.rotate(self.angle)
        self.lWingVector = self.rotation.rotate(-self.angle)

        self.rWingTip = [self.position.x + self.rWingVector.x * self.radius / 2, self.position.y + self.rWingVector.y * self.radius / 2]
        self.lWingTip = [self.position.x + self.lWingVector.x * self.radius / 2, self.position.y + self.lWingVector.y * self.radius / 2]
        self.points = [self.tip, self.rWingTip, self.position, self.lWingTip]


        gfxdraw.filled_polygon(self.surface, self.points, pg.Color(self.color))
        gfxdraw.aapolygon(self.surface, self.points, pg.Color(self.color))

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
        self.searchRadius = searchRadius
        self.vLimit = vLimit

    def movement(self):
        self.activeEffects = [self.cohesion(10), self.seperation(), self.alignment(), self.randomness()]
        
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
        self.boidsInRange = [boid for boid in self.boids if inCircle(boid.position,self.position, self.searchRadius) and boid.position != self.position]

        super().live()

    def cohesion(self, strength):
        self.centerBoids = pg.Vector2(0,0)
        if (len(self.boidsInRange) != 0):
            for boid in self.boidsInRange:
                self.centerBoids += boid.position

            return pg.Vector2((self.centerBoids / len(self.boidsInRange) - self.position) / (100/strength))        

        else:
            return pg.Vector2(0,0)

    def seperation(self, strength=0):
        return pg.Vector2(0,0)

    def alignment(self, strength=0):
        return pg.Vector2(0,0)

    def randomness(self, strength=0):
        return pg.Vector2(0,0)

    def demonstrate(self):
        gfxdraw.filled_circle(self.surface, round(self.position.x), round(self.position.y), self.searchRadius, pg.Color(150,150,150,10))
    


def main():
    print("main")
    pg.init()

    size = [500,500]
    screen = pg.display.set_mode(size)
    backgroundColour = "#282c34"

    pg.display.set_caption('Boids')
    Icon = pg.image.load('Assets/Logo.png')
    pg.display.set_icon(Icon)
    clock = pg.time.Clock()

    boids = []
    
    for i in range(100):
        boids.append(Boid(screen, 10, 50))


    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
        clock.tick()

        screen.fill(backgroundColour)

        for boid in boids:
            boid.live(boids)
        boids[0].demonstrate()

        pg.display.flip()



if (__name__ == "__main__"):
    main()




