import sys,pygame as pg
from entities import *
import random
from pygame import gfxdraw


def main():
    print("main")
    pg.init()

    size = [1000,500]
    screen = pg.display.set_mode(size)
    backgroundColour = "#3E4D66"
    demonstrate = False
    mode = 0

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
                    if (mode == 0):                        
                        for boid in boids:
                            boid.noClip = False
                        mode += 1
                    elif (mode == 1):
                        for boid in boids:
                            boid.noClip = bool(random.getrandbits(1))
                        mode += 1
                    elif (mode == 2):
                        for boid in boids:
                            boid.noClip = True
                        mode = 0
                        



        clock.tick(60)

        screen.fill(backgroundColour)

        for boid in boids:
            boid.live(boids)
        if (demonstrate):
            boids[0].demonstrate()
        pg.display.flip()


if (__name__ == "__main__"):
    main()



