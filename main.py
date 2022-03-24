import sys,pygame as pg
from math import *
from pygame import gfxdraw

class Boid:
    # size is the size from the center to the "tip" of the boid
    def __init__(self, surface, position, radius, rotation=pg.Vector2(0,1)):
        self.surface = surface
        self.position = position
        self.radius = radius
        self.rotation = rotation
        self.angle = 120
        self.color = [255,0,0]

    def live(self):

        self.tip = [self.position.x + self.rotation.x * self.radius, self.position.y + self.rotation.y * self.radius]
        self.rWingTip = [self.position.x + self.rotation.rotate(self.angle).x * self.radius / 2, self.position.y + self.rotation.rotate(self.angle).y * self.radius / 2]
        self.lWingTip = [self.position.x + self.rotation.rotate(-self.angle).x * self.radius / 2, self.position.y + self.rotation.rotate(-self.angle).y * self.radius / 2]

        gfxdraw.filled_polygon(self.surface, [self.tip, self.rWingTip, self.position, self.lWingTip], self.color)
        gfxdraw.aapolygon(self.surface, [self.tip, self.rWingTip, self.position, self.lWingTip], self.color)

  
def main():
    print("main")
    pg.init()

    clock = pg.time.Clock()

    size = [500,500]

    screen = pg.display.set_mode(size)
    
    boid1 = Boid(screen, pg.Vector2(250,250), 50)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

        screen.fill((255,255,255))
        boid1.live()
        clock.tick(60)
        pg.display.flip()

        boid1.rotation.rotate_ip(1)


if (__name__ == "__main__"):
    main()




