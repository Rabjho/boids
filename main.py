import sys,pygame as pg
from matplotlib.pyplot import draw
from entities import *
import random
from pygame import gfxdraw
from auxfunctions import State


def main():
    print("main")
    pg.init()

    size = [1000,500]
    screen = pg.display.set_mode(size)
    backgroundColour = "#3E4D66"
    demonstrate = False
    mode = State(3)

    pg.display.set_caption('Boids')
    Icon = pg.image.load('Assets/Logo.png')
    pg.display.set_icon(Icon)
    clock = pg.time.Clock()

    boids = []
    for i in range(100):
        boids.append(Boid(screen, 10, 50, 200))


    while True:
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                sys.exit()
            if (event.type == pg.KEYDOWN):

                if (event.key == pg.K_r):
                    main()
                
                if (event.key == pg.K_d):
                    demonstrate = not demonstrate

                if (event.key == pg.K_m):
                    if (mode.current == 0):                        
                        for boid in boids:
                            boid.walls = False

                    elif (mode.current == 1):
                        for boid in boids:
                            boid.walls = bool(random.getrandbits(1))

                    elif (mode.current == 2):
                        for boid in boids:
                            boid.walls = True
                    mode.next()

                        
        clock.tick(60)

        screen.fill(backgroundColour)

        # drawPie(screen, pg.Vector2(500,250), 50, 120, 180)

        for boid in boids:
            boid.live(boids)
        if (demonstrate):
            boids[0].demonstrate()
        pg.display.flip()


if (__name__ == "__main__"):
    main()




