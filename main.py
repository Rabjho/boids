from re import A
import sys,pygame as pg
from entities import *
import random
from auxfunctions import State
from quadtree import Boundary, QuadTree

def main(size=(1280, 720), fullscreen=False):
    backgroundColour = "#252530"
    windStrength = 5
    windTurnSpeed = 360

    templates = {
        "default" : 
        {
            "boids" : 100,
            "boidSize" : 10,
            "predators" : 10,
            "predatorSize" : 12,
            "boidSpeedLimit" : 200,
            "boidSearchRadius" : 50,
            "cohesionStrength" : 3,
            "seperationStrength" : 15,
            "alignmentStrength" : 7.5,
            "mouseTrackingStrength" : 5,
            "predatorAvoidStrength" : 20,
            "predatorAwarenessFactor" : 2,
            "predatorSpeedLimit" : 150,
        },
        "speed" : 
        {
            "boids" : 10,
            "boidSize" : 10,
            "predators" : 5,
            "predatorSize" : 12,
            "boidSpeedLimit" : 2000,
            "boidSearchRadius" : 50,
            "cohesionStrength" : 15,
            "seperationStrength" : 30,
            "alignmentStrength" : 25,
            "mouseTrackingStrength" : 5,
            "predatorAvoidStrength" : 200,
            "predatorAwarenessFactor" : 2,
            "predatorSpeedLimit" : 150,
        }
    }
    
    activeTemplate = templates["default"]
    templateController = State(len(templates))

    palette = ["#31b5d1", "#ff2625", "#a9a9a9", "#6EB257", "#F3F719", "#ed651c", "#1978e5", "#b422bf", "#41c676"]

    windPointerSize = 15
    windPointerWallMargin = 30

    qtreeBoidsCapacity = 3
    qtreePredatorCapacity = 3


    pg.init()
    if (fullscreen):
        screen = pg.display.set_mode(pg.display.get_desktop_sizes()[0], pg.FULLSCREEN | pg.RESIZABLE)
    else:
        screen = pg.display.set_mode(size, pg.RESIZABLE)
    pg.display.set_caption('Boids vs predators')
    Icon = pg.image.load('Assets/Logo.png')
    pg.display.set_icon(Icon)
    clock = pg.time.Clock()


    demonstrate = False
    mode = State(3)
    activeDemo = [0, float('inf')]    
    boids = []
    predators = []
    windToggle = False
    windDirection = pg.Vector2(1,0)
    heldKeys = {"K_LEFT" : False, "K_RIGHT" : False}



    qtreeBoids = QuadTree(Boundary(screen.get_width()/2, screen.get_height()/2, screen.get_width()/2, screen.get_height()/2), qtreeBoidsCapacity)
    qtreePredator = QuadTree(Boundary(screen.get_width()/2, screen.get_height()/2, screen.get_width()/2, screen.get_height()/2), qtreePredatorCapacity)

    for i in range(activeTemplate["boids"]):
        boids.append(Boid(screen, qtreeBoids, qtreePredator, activeTemplate["boidSpeedLimit"], activeTemplate["boidSize"], activeTemplate["boidSearchRadius"], activeTemplate["cohesionStrength"], activeTemplate["seperationStrength"], activeTemplate["alignmentStrength"], activeTemplate["predatorAvoidStrength"], activeTemplate["predatorAwarenessFactor"]))

    for i in range(activeTemplate["predators"]):
        predators.append(Predator(screen, qtreePredator, boids, activeTemplate["predatorSize"], activeTemplate["predatorSpeedLimit"]))

    windArrow = WindPointer(screen, windPointerSize, windPointerWallMargin)


    while True:
        clock.tick(60)
        screen.fill(backgroundColour)


# TODO Clean this code tremendously

# START INPUT HANDLER
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                sys.exit()
            elif (event.type == pg.KEYDOWN):
                if (event.key == pg.K_r):
                    main(screen.get_size(), fullscreen)
                
                if ((event.key == pg.K_RETURN and event.mod == pg.KMOD_LALT) or event.key == pg.K_f):
                    fullscreen = not fullscreen
                    if (fullscreen):
                        size = pg.display.get_window_size()
                        screen = pg.display.set_mode(pg.display.get_desktop_sizes()[0], pg.FULLSCREEN | pg.RESIZABLE)
                    else:
                        screen = pg.display.set_mode(size, pg.RESIZABLE)


                if (event.key == pg.K_d):
                    if (not demonstrate):
                        activeDemo[1] = pg.Vector2(boids[activeDemo[0]].position).distance_squared_to(pg.Vector2(pg.mouse.get_pos()))
                        for boid in boids:
                            if (pg.Vector2(boid.position).distance_squared_to(pg.Vector2(pg.mouse.get_pos())) < activeDemo[1]):
                                activeDemo = [boids.index(boid), pg.Vector2(boid.position).distance_squared_to(pg.Vector2(pg.mouse.get_pos()))]
                        boids[activeDemo[0]].demonstrating = True
                    else:
                        boids[activeDemo[0]].demonstrating = False
                    demonstrate = not demonstrate

                if (event.key == pg.K_m):
                    if (mode.current == 0):                        
                        for boid in boids:
                            boid.walls = False
                        for predator in predators:
                            predator.walls = False

                    elif (mode.current == 1):
                        for boid in boids:
                            boid.walls = bool(random.getrandbits(1))
                        for predator in predators:
                            predator.walls = bool(random.getrandbits(1))

                    elif (mode.current == 2):
                        for boid in boids:
                            boid.walls = True
                        for predator in predators:
                            predator.walls = True
                    mode.next()

                if (event.key == pg.K_w):
                    windToggle = not windToggle

                if (event.key == pg.K_LEFT):
                    heldKeys["K_LEFT"] = True
                if (event.key == pg.K_RIGHT):
                    heldKeys["K_RIGHT"] = True

                if (event.key > pg.K_0 and event.key <= pg.K_9):
                    for boid in boids:
                        boid.color = pg.Color(random.choice(palette[:event.key-48]))

                if (event.key == pg.K_t):
                    for boid in boids:
                        if (not boid.demonstrating):
                            boid.trailing = not boid.trailing
                
                if (event.key == pg.K_q or event.key == pg.K_e):
                    if (event.key == pg.K_q):
                        templateController.prior()
                    
                    if (event.key == pg.K_e):
                        templateController.next()

                    activeTemplate = templates[list(templates)[templateController.current]]

                    if (len(boids) < activeTemplate["boids"]):
                        for i in range(activeTemplate["boids"] - len(boids)):
                            boids.append(Boid(screen, qtreeBoids, qtreePredator, activeTemplate["boidSpeedLimit"], activeTemplate["boidSize"], activeTemplate["boidSearchRadius"], activeTemplate["cohesionStrength"], activeTemplate["seperationStrength"], activeTemplate["alignmentStrength"], activeTemplate["predatorAvoidStrength"], activeTemplate["predatorAwarenessFactor"]))

                    elif (len(boids) > activeTemplate["boids"]):
                        for i in range(len(boids) - activeTemplate["boids"]):
                            boids.pop(-1)

                    if (len(predators) < activeTemplate["predators"]):
                        for i in range(activeTemplate["predators"] - len(predators)):
                            predators.append(Predator(screen, qtreePredator, boids, activeTemplate["predatorSize"], activeTemplate["predatorSpeedLimit"]))

                    elif (len(predators) > activeTemplate["predators"]):
                        for i in range(len(predators) - activeTemplate["predators"]):
                            predators.pop(-1)

                    for boid in boids:
                        boid.vLimit = activeTemplate["boidSpeedLimit"]
                        boid.radius = activeTemplate["boidSize"]
                        boid.searchRadius = activeTemplate["boidSearchRadius"]
                        boid.cohesionStrength = activeTemplate["cohesionStrength"]
                        boid.seperationStrength = activeTemplate["seperationStrength"]
                        boid.alignmentStrength = activeTemplate["alignmentStrength"]
                        boid.predatorAvoidStrength = activeTemplate["predatorAvoidStrength"]
                        boid.predatorAwarenessFactor = activeTemplate["predatorAwarenessFactor"]    

                    for predator in predators:
                        predator.radius = activeTemplate["predatorSize"]
                        predator.vLimit = activeTemplate["predatorSpeedLimit"]


         
            elif (event.type == pg.KEYUP):
                if (event.key == pg.K_LEFT):
                    heldKeys["K_LEFT"] = False
                if (event.key == pg.K_RIGHT):
                    heldKeys["K_RIGHT"] = False


        if (heldKeys["K_LEFT"]):
            windDirection.rotate_ip(-windTurnSpeed * clock.get_time() / 1000)
        if (heldKeys["K_RIGHT"]):
            windDirection.rotate_ip(windTurnSpeed * clock.get_time() / 1000)
# END INPUT HANDLER

        qtreeBoids = QuadTree(Boundary(screen.get_width()/2, screen.get_height()/2, screen.get_width()/2, screen.get_height()/2), qtreeBoidsCapacity)
        qtreePredator = QuadTree(Boundary(screen.get_width()/2, screen.get_height()/2, screen.get_width()/2, screen.get_height()/2), qtreePredatorCapacity)

        for predator in predators:
            predator.live(windDirection, windStrength * windToggle)
            qtreePredator.insert(predator)
            
        for boid in boids:
            boid.live(windDirection, windStrength * windToggle, activeTemplate["mouseTrackingStrength"] * pg.mouse.get_pressed()[0])
            qtreeBoids.insert(boid)

        if (windToggle):
            windArrow.live(windDirection)

        pg.display.flip()


if (__name__ == "__main__"):
    print("Started simulation")
    main()