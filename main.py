# Removes pygame print in terminal on import
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Imports required libraries including other files in this project
import sys,pygame as pg
from entities import *
import random
from auxfunctions import State
from quadtree import Boundary, Quadtree
import json

# main function running the program, called in the bottom if-statement
# Has default arguments to run the first time and afterwards those arguments are supplied when the game is reset
def main(size=(1280, 720), fullscreen=False, resetTemplate="default"):


    pg.init()

    # Loading templates from templates.json using 'with' to ensure proper exiting of file
    with open(os.path.dirname(__file__)+"/templates.json", "r") as file:
        templates = json.load(file)

    # Template handling with a basic state machine
    activeTemplate = templates[resetTemplate]
    templateController = State(len(templates))

    # The colour palette of the background and boids
    backgroundColour = "#252530"
    palette = ["#31b5d1", "#ff2625", "#a9a9a9", "#6EB257", "#F3F719", "#ed651c", "#1978e5", "#b422bf", "#41c676"]

    # Initial values for the windPointer, should scale with resolution instead of being hardcoded
    windPointerSize = 15
    windPointerWallMargin = 30
    # How quickly the wind can be turned
    windTurnSpeed = 360


    # Defines how many objects that may be in each quadtree cell
    qtreeBoidsCapacity = 3
    qtreePredatorCapacity = 3

    # Checks if the game should be started in fullscreen and starts accordingly
    if (fullscreen):
        screen = pg.display.set_mode(pg.display.get_desktop_sizes()[0], pg.FULLSCREEN | pg.RESIZABLE)
    else:
        screen = pg.display.set_mode(size, pg.RESIZABLE)
    # Sets window title and icon
    pg.display.set_caption('Boids vs predators')
    Icon = pg.image.load('Assets/Logo.png')
    pg.display.set_icon(Icon)

    # Initializes clock used to track deltatime i.e. time it took to run/render last frame
    clock = pg.time.Clock()

    # Initializes variables that are required
    demonstrate = False
    mode = State(3)
    activeDemo = [0, float('inf')]    
    boids = []
    predators = []
    windToggle = False
    windDirection = pg.Vector2(1,0)
    heldKeys = {"K_LEFT" : False, "K_RIGHT" : False}


    # Initializes quadtrees (source in quadtree.py)
    qtreeBoids = Quadtree(Boundary(screen.get_width()/2, screen.get_height()/2, screen.get_width()/2, screen.get_height()/2), qtreeBoidsCapacity)
    qtreePredator = Quadtree(Boundary(screen.get_width()/2, screen.get_height()/2, screen.get_width()/2, screen.get_height()/2), qtreePredatorCapacity)

    # Creates list of boids/predators according to how many are set as default w/ values according to the same template
    boids = [Boid(screen, qtreeBoids, qtreePredator, activeTemplate["boidSpeedLimit"], activeTemplate["boidSize"], activeTemplate["boidSearchRadius"], activeTemplate["cohesionStrength"], activeTemplate["seperationStrength"], activeTemplate["alignmentStrength"], activeTemplate["predatorAvoidStrength"], activeTemplate["predatorAwarenessFactor"]) for i in range(activeTemplate["boids"])]
    predators = [Predator(screen, qtreePredator, boids, activeTemplate["predatorSize"], activeTemplate["predatorSpeedLimit"]) for i in range(activeTemplate["predators"])]

    # Initializes the windpointer
    windArrow = WindPointer(screen, windPointerSize, windPointerWallMargin)

    # Starts game loop
    while True:
        # Iterates the clock at 60 fps
        clock.tick(60)
        # Fills background with colour
        screen.fill(backgroundColour)


    # START INPUT HANDLER  (not in seperate function because of access to many global variables)
        # Checks pygame event handler
        for event in pg.event.get():
            # Handles exits
            if (event.type == pg.QUIT):
                sys.exit()

            # Handles keypresses
            elif (event.type == pg.KEYDOWN):
                # Reset
                if (event.key == pg.K_r):
                    main(screen.get_size(), fullscreen, list(templates)[templateController.current])
                
                # Fullscreen toggle
                if ((event.key == pg.K_RETURN and event.mod == pg.KMOD_LALT) or event.key == pg.K_f):
                    fullscreen = not fullscreen
                    if (fullscreen):
                        size = pg.display.get_window_size()
                        screen = pg.display.set_mode(pg.display.get_desktop_sizes()[0], pg.FULLSCREEN | pg.RESIZABLE)
                    else:
                        screen = pg.display.set_mode(size, pg.RESIZABLE)

                # Demonstration toggle. When turning on chooses closest to mouse or the first in the list of boids
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

                # Changes the mode of the boids i.e. avoids walls and can't go through, noclip or half of each
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


                # Wind toggle
                if (event.key == pg.K_w):
                    windToggle = not windToggle

                # Wind turning
                if (event.key == pg.K_LEFT):
                    heldKeys["K_LEFT"] = True
                if (event.key == pg.K_RIGHT):
                    heldKeys["K_RIGHT"] = True

                # Family handling
                if (event.key > pg.K_0 and event.key <= pg.K_9):
                    for boid in boids:
                        # This is possible because event.key is an interger and the numberrow is sequential 
                        # if you then subtract 48 from that integer you can get the number on the key.
                        boid.color = pg.Color(random.choice(palette[:event.key-48]))

                # Adds trails to all boids (has performance issues that need to be looked after)
                if (event.key == pg.K_t):
                    for boid in boids:
                        if (not boid.demonstrating):
                            boid.trailing = not boid.trailing
                
                # Template controller
                if (event.key == pg.K_q or event.key == pg.K_e):
                    if (event.key == pg.K_q):
                        templateController.prior()
                    
                    if (event.key == pg.K_e):
                        templateController.next()

                    # Makes a list of strings of the keys from the dictionary of dictionaries and uses key according to what is the next or prior
                    activeTemplate = templates[list(templates)[templateController.current]]

                    # Adds and removes boids according to what's needed
                    if (len(boids) < activeTemplate["boids"]):
                        for i in range(activeTemplate["boids"] - len(boids)):
                            boids.append(Boid(screen, qtreeBoids, qtreePredator, activeTemplate["boidSpeedLimit"], activeTemplate["boidSize"], activeTemplate["boidSearchRadius"], activeTemplate["cohesionStrength"], activeTemplate["seperationStrength"], activeTemplate["alignmentStrength"], activeTemplate["predatorAvoidStrength"], activeTemplate["predatorAwarenessFactor"]))

                    elif (len(boids) > activeTemplate["boids"]):
                        for i in range(len(boids) - activeTemplate["boids"]):
                            boids.pop(-1)

                    # Adds and removes predators according to what's needed
                    if (len(predators) < activeTemplate["predators"]):
                        for i in range(activeTemplate["predators"] - len(predators)):
                            predators.append(Predator(screen, qtreePredator, boids, activeTemplate["predatorSize"], activeTemplate["predatorSpeedLimit"]))

                    elif (len(predators) > activeTemplate["predators"]):
                        for i in range(len(predators) - activeTemplate["predators"]):
                            predators.pop(-1)

                    # Changes variables for all boids (there is probably a better way of doing this)
                    for boid in boids:
                        boid.vLimit = activeTemplate["boidSpeedLimit"]
                        boid.radius = activeTemplate["boidSize"]
                        boid.searchRadius = activeTemplate["boidSearchRadius"]
                        boid.cohesionStrength = activeTemplate["cohesionStrength"]
                        boid.seperationStrength = activeTemplate["seperationStrength"]
                        boid.alignmentStrength = activeTemplate["alignmentStrength"]
                        boid.predatorAvoidStrength = activeTemplate["predatorAvoidStrength"]
                        boid.predatorAwarenessFactor = activeTemplate["predatorAwarenessFactor"]  
  
                    # Changes variables for all predators
                    for predator in predators:
                        predator.radius = activeTemplate["predatorSize"]
                        predator.vLimit = activeTemplate["predatorSpeedLimit"]


            # Handles releasing of keys for handling held down keys.
            elif (event.type == pg.KEYUP):
                if (event.key == pg.K_LEFT):
                    heldKeys["K_LEFT"] = False
                if (event.key == pg.K_RIGHT):
                    heldKeys["K_RIGHT"] = False

        # Handler for keys that are held down
        if (heldKeys["K_LEFT"]):
            windDirection.rotate_ip(-windTurnSpeed * clock.get_time() / 1000)
        if (heldKeys["K_RIGHT"]):
            windDirection.rotate_ip(windTurnSpeed * clock.get_time() / 1000)
# END INPUT HANDLER

        # Resets quadtree by overriding old objects
        qtreeBoids = Quadtree(Boundary(screen.get_width()/2, screen.get_height()/2, screen.get_width()/2, screen.get_height()/2), qtreeBoidsCapacity)
        qtreePredator = Quadtree(Boundary(screen.get_width()/2, screen.get_height()/2, screen.get_width()/2, screen.get_height()/2), qtreePredatorCapacity)

        # Iterates through all predators
        for predator in predators:
            # Moves predator
            predator.live(windDirection, activeTemplate["windStrength"] * windToggle)
            # Inserts predator in quadtree
            qtreePredator.insert(predator)
            
        # Iterates through all boids
        for boid in boids:
            # Moves boid
            boid.live(windDirection, activeTemplate["windStrength"] * windToggle, activeTemplate["wallAvoid"] ,activeTemplate["mouseTrackingStrength"] * pg.mouse.get_pressed()[0])
            # INserts boid in quadtree
            qtreeBoids.insert(boid)

        # Toggles if wind arrow is visible
        if (windToggle):
            windArrow.live(windDirection)

        # Draws to window using pygame
        pg.display.flip()

# Assures that file is not run as library but as the main file.
if (__name__ == "__main__"):
    print("Started simulation")
    main()