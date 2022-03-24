import sys,pygame as pg


def main():
    print("main")
    pg.init()

    size = [500,500]

    screen = pg.display.set_mode(size)
    


    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

        screen.fill((255,255,255))
        pg.draw.polygon(screen,(255,0,0),[(20,20),(50,50),(20,150)])
        pg.display.flip()
    




if (__name__ == "__main__"):
    main()