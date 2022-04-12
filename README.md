# boids
Boids implementation w/ ability to make templates. Done using quadtrees in pygame. I recommend no more than 250 boids on a beefy laptop 

## Keybinds  
|Key|Action|
|---|------|
|r|Resets|
|d|Toggles demonstration|
|m|Switches between modes|
|f|Toggles fullscreen|
|ALT+ENTER|Toggles fullscreen|
|0-9|Changes amount of families|

## Modes 
### Wall (default) 
Boids avoid walls and bounce of them, if they still hit the walls

### Noclip
Boids can go through walls and are teleported to the opposite side

### Hybrid
A random amount of boids act as if they are in wall mode while others are in noclip mode. It is chosen at random on a per boid basis, so the distribution should be roughly 50/50


## Links
[Pygame docs](https://www.pygame.org/docs/)
