from random import randrange
import sys,pygame as pg
from pygame import gfxdraw
from entities import *

def main():
    print("main")
    pg.init()

    size = [500,500]
    screen = pg.display.set_mode(size)
    backgroundColour = "#3E4D66"

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




