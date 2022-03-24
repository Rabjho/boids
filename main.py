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
        self.color = (29,222,85)
        self.color = "#5a8ff5"
        self.velocity = pg.Vector2(0,0)

    def live(self):
        self.position = self.position + self.velocity


        self.tip = [self.position.x + self.rotation.x * self.radius, self.position.y + self.rotation.y * self.radius]
        self.rWingTip = [self.position.x + self.rotation.rotate(self.angle).x * self.radius / 2, self.position.y + self.rotation.rotate(self.angle).y * self.radius / 2]
        self.lWingTip = [self.position.x + self.rotation.rotate(-self.angle).x * self.radius / 2, self.position.y + self.rotation.rotate(-self.angle).y * self.radius / 2]

        gfxdraw.filled_polygon(self.surface, [self.tip, self.rWingTip, self.position, self.lWingTip], pg.Color(self.color))
        gfxdraw.aapolygon(self.surface, [self.tip, self.rWingTip, self.position, self.lWingTip], pg.Color(self.color))

  
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


    
    boid1 = Boid(screen, pg.Vector2(250,250), 10)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

        screen.fill(backgroundColour)
        boid1.live()
        clock.tick(60)
        pg.display.flip()

        boid1.rotation.rotate_ip(1)


if (__name__ == "__main__"):
    main()




