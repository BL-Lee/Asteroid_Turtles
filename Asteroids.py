import turtle
import time
import math
import random

#
#  Shapes & Info --------------------------------------------------------------------
#

SPACESHIP_SPRITE_INFO = {'coordinates': [ ( (7,-20), (0,5), (-7,-20) ),
                                         ], 'name': 'SPACESHIP_SHAPE'}

SPACESHIP_ACCELERATE_SPRITE_INFO = {'coordinates': [ ( (7,-20), (0,5), (-7,-20) ),
                                                     ( (7,-20), (0,-30), (-7,-20) ) ],
                                    'name': 'SPACESHIP_ACCELERATION_SHAPE'}

SPACESHIP_FLICKER_INFO = {'coordinates': [ () ],
                          'name': 'SPACESHIP_FLICKER_SHAPE'}

BULLET_SPRITE_INFO = {'coordinates': [ ((-1, -1), (-1, 1), (1, 1), (1, -1)) ],
                      'name': 'BULLET_SHAPE'}

ASTEROID_INFO = { 'speeds' : [None, 30, 50, 70],
                  'radii': [None, 15, 30, 45],
                  'turtle_sizes': [None, 1.5, 3.0, 4.5], 
                  'points': [None, 50, 25, 10]}

#
#  Class / Struct definitions -------------------------------------------------
#

#
#  Classes are useful ways to store similar data together
#     Anything in the class can be accessed with a dot operator
#     For example the vec2 (vector in 2 dimensions) class simply stores an X and a Y component
#     so if we have a vec2 named direction, we could access just the x component with direction.x
#     And we can create a new vec2 with the initialization function
#         eg: direction = vec2(1.5, 3.0)
#         This will call the __init__ function inside vec2,
#         and direction will now store a vector with an x component of 1.5 and a y component of 3.0
#     vec2 is also a special case where we can use the __add__ function.
#     This will make it so if we have two vec2s and we use the + operator it will call our __add__
#         eg: first =  vec2(1.0, 2.0)
#             second = vec2(3.0, 4.0)
#             first + second would return a new vec2 [4.0, 6.0] (because it adds the components)
#     Similar idea with the __mul__ for multiply
#
#  There are other ways we could store vector2s,
#    For example we could use an array [x,y], and assume the first index is x, and second is y
#    Or a dictionary: {'x': 0.0, 'y': 0.0} and access it with ['x']
#  Are there any pros and cons of each of these?

class vec2:
    x: float
    y: float
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, vec):
        x = self.x + vec.x
        y = self.y + vec.y
        return vec2(x,y)
    def __mul__(self, scalar):
        x = self.x * scalar
        y = self.y * scalar
        return vec2(x,y)

#
#   This is an "Entity" class which acts as our base class
#   This means that anything that inherits this will have all the fields in an entity
#   We'll see how this is useful when we see the other classes below
#

class Entity:
    position: vec2 # Technically not required, but I like putting these here to show that each entity will have a position, velocity and radius
    velocity: vec2
    radius: float
    def __init__(self, position, velocity, radius):
        self.position = position
        self.velocity = velocity
        self.turtle = turtle.Turtle()
        self.turtle.penup()
        self.turtle.speed(0)
        self.radius = radius

#
#   Here we have a class for the Player.
#   The player inherits the Entity class (because it has it in the brackets)
#   Which means that in addition to the fields we put in here, it will also have the fields
#     inside of Entity. This saves a bunch of copied code and typing!
#   

class Player(Entity):
    health: int
    rotation: float
    def __init__(self,health, position, velocity):
        super().__init__(position, velocity, 20.0 ) # do the superclass's (Entity) initializer, ie: set position, velocity, turtle...
        self.health = health
        self.rotation = 0.0
        self.ROTATION_SPEED = 50
        self.ACCELERATION_SPEED = 20
        self.invincibility_frames = 0
        
class Asteroid(Entity):
    health: int
    shape: int
    active: bool
    
    def __init__(self,health, position, velocity, info):
        super().__init__(position, velocity, (health * 10) * 1.5)
        self.health = health
        self.turtle.shape('circle')
        self.turtle.shapesize(health * 1.5, health * 1.5)
        self.turtle.color('white')
        self.turtle.penup()
        self.turtle.fillcolor('black')
        self.active = True

    # This is where classes really shine
    # If we have a variable asteroid we can deactivate that specific asteroid by
    # calling deactivate on it
    #  eg:
    #      a = Asteroid(...)
    #      a.deactivate() (the self gets filled in automatically!)
    #
    # These are called class methods, which means these functions only really affect
    #  this SPECIFIC asteroid. If we have two asteroids A and B, and we call A.deactivate(). B will
    #  still be activated and moving around
    #
    # Can you think of other class functions we could move into here?
    # One could be a split function for when we shoot it
    #
    # What about class functions for the player?
    
    def deactivate(self): 
        self.turtle.ht()
        self.active = False

class Bullet(Entity):
    active: bool
    def __init__(self, position):
        super().__init__(position, vec2(0.0, 0.0), 2)
        self.turtle.shape(BULLET_SPRITE_INFO['name'])
        self.active = False
    def deactivate(self):
        self.turtle.ht()
        self.active = False
        
#
#  Globals --------------------------------------------------------
#

# I'm putting these variables in a GlobalTimeInfo class so it is cleaner when I use them
# globally. This way I'll have only one global TimeInfo statement later on than a bunch.
# 

class GlobalTimeInfo:
    def __init__(self):
        self.delta_time = 0.0 # time since the last window update
        self.stop_watch = time.time()
        self.MS_PER_FRAME = 1 / 60 # How often the screen is refreshed in milliseconds

class GlobalScoreInfo:
    def __init__(self):
        self.current_score = 0
        self.high_score = 0

main_player = None

# An array to store all the asteroids
asteroid_buffer = []
total_active_asteroids = 0
ASTEROID_BUFFER_SIZE = 50

# An array to store all the bullets
bullet_buffer = []
current_bullet_index = 0
BULLET_BUFFER_SIZE = 6 # How many bullets we allow on the screen at once.
BULLET_SPEED = 300

game_running = None
game_window = None
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

score_drawer = None
health_drawer = None

#
#  Utility Functions ----------------------------------------------------
#

# Returns a vector with length 1 from a rotation. Assumes rotatation in degrees
def unit_vector_from_rotation(rotation):
    return vec2( math.cos(math.radians(rotation)),
                 math.sin(math.radians(rotation)) )

def distance_between(first, second):
    delta_x = first.x - second.x
    delta_y = first.y - second.y
    distance = ((delta_x ** 2) + (delta_y ** 2)) ** 0.5
    return distance

# Returns if two entities are colliding, using circular hitboxes
def is_colliding(entity, other):
    return distance_between(entity.position, other.position) < entity.radius + other.radius

# Adds a shape to turtles so it can be used later with turtle.shape
def add_shape_to_turtle(coordinates, name):
    #check lengths
    shape = turtle.Shape('compound', None)
    for i in range(len(coordinates)):
        shape.addcomponent(coordinates[i], 'black', 'white')
    game_window.register_shape(name, shape)
    return shape

# Returns a random value between -1 and 1
def random_bilateral():
    return (random.random() - 0.5) * 2.0

# Returns a random vec2 with x and y between [-scale, scale]
def random_vec2_component_length(scale):
    return vec2(random_bilateral() * scale, random_bilateral() * scale)

#
#  Text Drawer Functions ---------------------------------------------
#

def set_turtle_text(text, turtle):
    turtle.clear()
    turtle.write(text, align='left', font=('fixedsys', 15, 'normal'))

#
#  Player functions ---------------------------------------------------
#

def rotate_right():
    main_player.rotation -= main_player.ROTATION_SPEED * TimeInfo.delta_time
    # The reason we are multiplying by delta_time (the time since the last update)
    #  is because it makes the player turn the same amount, no matter how fast your computer is running
    #  If the game lags, then we want to make sure that we still rotate the same amount, even
    #  if the screen hadn't updated in time. This is a relatively simple way of making the game
    #  framerate independent
    
def rotate_left():
    main_player.rotation += main_player.ROTATION_SPEED * TimeInfo.delta_time
    
def accelerate_player():
    acceleration_vector = unit_vector_from_rotation(main_player.rotation)
    main_player.velocity += acceleration_vector * main_player.ACCELERATION_SPEED * TimeInfo.delta_time
    main_player.turtle.shape(SPACESHIP_ACCELERATE_SPRITE_INFO['name'])
    
def shoot():
    global bullet_buffer
    global current_bullet_index
    global main_player
    global BULLET_SPEED

    # bullet_buffer acts as a circular array
    # which just means when we add a new bullet, we go forward one slot in the array
    # and replace that one.
    # If we hit the end, we go around to the beginning again
    # This way if we overwrite an active bullet, its the one that we shot first

    # In the beginning it is all non-active bullets
    # [ *Non-Active*, Non-Active, Non-Active, Non-Active ]
    # Currently current_bullet_index points at the first index (marked with *)
    # Then we shoot and move current_bullet_index up
    # [ Active, *Non-Active*, Non-Active, Non-Active ]
    # If we shoot two more times then we have this setup
    # [ Active, Active, Active, *Non-Active* ]
    # Next time we shoot it will wrap around to the beginning
    # [ *Active*, Active, Active, Active ]
    # At any point, any of these bullets could have hit an asteroid and deactivate
    # [ *Active*, Non-Active, Active, Non-Active ]
    
    bullet_buffer[current_bullet_index].turtle.st() #show_turtle 
    bullet_buffer[current_bullet_index].position = main_player.position
    bullet_buffer[current_bullet_index].velocity = unit_vector_from_rotation(main_player.rotation) * BULLET_SPEED
    bullet_buffer[current_bullet_index].active = True

    # Move current_bullet_index up by one, but the modulo will make it wrap to the beginning
    # if it its the end
    current_bullet_index = (current_bullet_index + 1) % BULLET_BUFFER_SIZE

# This is used to make the player flicker when getting hit
def animate_player():
    if main_player.invincibility_frames > 0.0:
        fractional = main_player.invincibility_frames - int(main_player.invincibility_frames)
        scaled = int(fractional * 5)
        
        is_invisible = scaled % 2

        if is_invisible:
            main_player.turtle.shape(SPACESHIP_FLICKER_INFO['name'])
        else:
            if keys_pressed[UP_KEY]:
                main_player.turtle.shape(SPACESHIP_ACCELERATE_SPRITE_INFO['name'])
            else: 
                main_player.turtle.shape(SPACESHIP_SPRITE_INFO['name'])
        main_player.invincibility_frames -= TimeInfo.delta_time
    
#
#   Key events --------------------------------------------------------------
#

RIGHT_KEY = 0 #indices into the arrays below
LEFT_KEY = 1
UP_KEY = 2
SPACE_KEY = 3
# Stores a boolean of whether the key is pressed or not
keys_pressed = [False, False, False, False]
keys = [RIGHT_KEY, LEFT_KEY, UP_KEY, SPACE_KEY]
# Functions to call when a certain key is pressed
key_events = [rotate_right, rotate_left, accelerate_player, lambda: None]
def Right():
    keys_pressed[RIGHT_KEY] = True
def RightRelease():
    keys_pressed[RIGHT_KEY] = False

def Left():
    keys_pressed[LEFT_KEY] = True
def LeftRelease():
    keys_pressed[LEFT_KEY] = False

def Up():
    keys_pressed[UP_KEY] = True
def UpRelease():
    keys_pressed[UP_KEY] = False

def Space():
    shoot()
    keys_pressed[SPACE_KEY] = True

# This is called every frame.
# We loop over all the keys and check if any of them are pressed at the moment
# If it is, we call the function that is saved in key_events.
def process_inputs():    
    for key in keys:
        if keys_pressed[key]:
            key_events[key]()

#
#  Initialization functions ---------------------------------------------------------------
#

def init_constants():

    # Initialize the player
    global main_player
    main_player = Player(health=3, position=vec2(0.0, 0.0), velocity=vec2(0.0, 0.0))

    # Initialize the score information
    global ScoreInfo
    ScoreInfo = GlobalScoreInfo()
    global TimeInfo
    TimeInfo = GlobalTimeInfo()

    # Initialize the Turtle Window
    global game_window
    game_window = turtle.Screen()
    game_window.listen()

    # Register the key events
    game_window.onkeypress(Right, 'Right')
    game_window.onkeyrelease(RightRelease, 'Right')
    game_window.onkeypress(Left,'Left')
    game_window.onkeyrelease(LeftRelease,'Left')
    game_window.onkeypress(Up,'Up')
    game_window.onkeyrelease(UpRelease,'Up')
    game_window.onkey(Space,'space')

    # Add the shapes to turtles
    add_shape_to_turtle(SPACESHIP_SPRITE_INFO['coordinates'], SPACESHIP_SPRITE_INFO['name'])
    add_shape_to_turtle(SPACESHIP_ACCELERATE_SPRITE_INFO['coordinates'], SPACESHIP_ACCELERATE_SPRITE_INFO['name'])
    add_shape_to_turtle(BULLET_SPRITE_INFO['coordinates'], BULLET_SPRITE_INFO['name'])
    add_shape_to_turtle(SPACESHIP_FLICKER_INFO['coordinates'], SPACESHIP_FLICKER_INFO['name'])

    # Set the screen width, height, colour
    turtle.setup(WINDOW_WIDTH, WINDOW_HEIGHT)
    game_window.bgcolor('black')

    # We will be updated the screen manually, so we turn off the screen's updates
    game_window.tracer(0, 0) 

    # Initialize the bullet array
    global bullet_buffer
    for bullet in range(BULLET_BUFFER_SIZE):
        bullet_buffer.append( Bullet(vec2(0.0, 0.0)) )

    # Initialize the asteroids
    global asteroid_buffer
    global total_active_asteroids
    global ASTEROID_BUFFER_SIZE
    for i in range(ASTEROID_BUFFER_SIZE):
        asteroid_buffer.append(
            Asteroid(3,
                     random_vec2_component_length(300),
                     random_vec2_component_length(30),
                     None))
    for i in range(ASTEROID_BUFFER_SIZE - 5):
        asteroid_buffer[i].deactivate()    
    total_active_asteroids = 5

    # Initialize score and health drawers
    # Do you think this code could be cleaner up somehow?
    global score_drawer
    score_drawer=turtle.Turtle()
    score_drawer.ht()
    score_drawer.color('white')    
    score_drawer.penup()
    score_drawer.goto((-WINDOW_WIDTH / 2) + 20, WINDOW_HEIGHT / 2 - 30)
    set_turtle_text('SCORE: 0', score_drawer)
    
    global health_drawer
    health_drawer=turtle.Turtle()
    health_drawer.ht()
    health_drawer.color('white')    
    health_drawer.penup()
    health_drawer.goto((-WINDOW_WIDTH / 2) + 20, WINDOW_HEIGHT / 2 - 70)
    set_turtle_text('HEALTH: ' + str(main_player.health), health_drawer)

def reset_round(asteroid_count):
    
    # Clear all the bullets
    for bullet in bullet_buffer:
        bullet.active = False

    # Create new asteroids
    for i in range(asteroid_count):
        position = random_vec2_component_length(300)
        
        # Make sure the created asteroid does not spawn ontop of the player        
        while distance_between(main_player.position, position) < 300:
            position = random_vec2_component_length(300)            
        spawn_asteroid(3, position, random_vec2_component_length(ASTEROID_INFO['speeds'][3]))
        
    global total_active_asteroids
    total_active_asteroids = asteroid_count
                       

#
#  Asteroid and Bullet functions ----------------------------------------------------------
#
            
def spawn_asteroid(stage, position, velocity):
    # Find an empty slot in the buffer for our new asteroid
    for i in range(len(asteroid_buffer)):
        if not asteroid_buffer[i].active:
            asteroid_buffer[i].active = True
            asteroid_buffer[i].health = stage
            asteroid_buffer[i].position = position
            asteroid_buffer[i].velocity = velocity
            asteroid_buffer[i].turtle.st()
            size = ASTEROID_INFO['turtle_sizes'][stage]
            asteroid_buffer[i].turtle.shapesize(size, size)
            asteroid_buffer[i].radius = ASTEROID_INFO['radii'][stage]
            return
    assert False # buffer is full! Essentially crash if we dont find a slot
    # We could also append to the list if we didn't find one!

def handle_bullet_asteroid_collisions():
    global total_active_asteroids
    
    # Check if each bullet hits any of the asteroids
    
    for bullet in bullet_buffer:
        if bullet.active:
            for asteroid in asteroid_buffer:
                if asteroid.active and is_colliding(bullet, asteroid):
                    
                    # If it is then we deactivate both of them 
                    total_active_asteroids -= 1

                    asteroid.deactivate()
                    bullet.deactivate()
                    
                    health = asteroid.health
                    position = asteroid.position
                    
                    ScoreInfo.current_score += ASTEROID_INFO['points'][health]

                    # If the asteroid was not the smallest, then we split it in two!
                    if asteroid.health >= 2:
                        spawn_asteroid(health - 1, position,
                                       random_vec2_component_length(ASTEROID_INFO['speeds'][health]))
                        spawn_asteroid(health - 1, position,
                                       random_vec2_component_length(ASTEROID_INFO['speeds'][health]))

                        total_active_asteroids += 2

                    set_turtle_text("SCORE: " + str(ScoreInfo.current_score), score_drawer)
    if total_active_asteroids == 0:
        reset_round(5)

#
#  Movement and Physics Functions ---------------------------------------------------------
#

# Make the entity wrap around the sides of the screen
def border_wrap_entity(entity):
    if abs(entity.position.x) > WINDOW_WIDTH / 2 or abs(entity.position.y) > WINDOW_HEIGHT / 2:        
        if entity.position.x > WINDOW_WIDTH / 2:
            entity.position.x = -WINDOW_WIDTH / 2
        elif entity.position.x < -WINDOW_WIDTH / 2:
            entity.position.x = WINDOW_WIDTH / 2 
            
        if entity.position.y > WINDOW_HEIGHT / 2:
            entity.position.y = -WINDOW_HEIGHT / 2
        elif entity.position.y < -WINDOW_HEIGHT / 2:
            entity.position.y = WINDOW_HEIGHT / 2
                
def move_turtles(entities):
    for entity in entities:
        
        # Only move the entity if it is active
        # hasattr will return false if it is not in the class
        # Player does not have 'active', so it will not make this check!
        if hasattr(entity, 'active') and entity.active is False:
            continue

        # Move the entity forward by its velocity
        turtle = entity.turtle
        newpos = vec2( entity.position.x + entity.velocity.x * TimeInfo.delta_time,
                     entity.position.y + entity.velocity.y * TimeInfo.delta_time )
        
        turtle.goto( newpos.x, newpos.y )
        entity.position = newpos

        # Set the rotation if it has it
        if hasattr(entity, 'rotation'):
            turtle.setheading(entity.rotation)

        border_wrap_entity(entity)

def check_player_collisions():
    if main_player.invincibility_frames > 0.0:
        return
    for asteroid in asteroid_buffer:
        if asteroid.active and is_colliding(main_player, asteroid):
            main_player.health -= 1
            set_turtle_text("HEALTH: " + str(main_player.health), health_drawer)
            main_player.invincibility_frames = 5.00 # seconds of invincibility

        

#
#  Main Function --------------------------------------------------------
#  This is where we start the code!
#
        
def __main__():
    init_constants()
    
    time_elapsed = 0.0
    global bullet_buffer
    game_running = True
    
    while game_running:
        # Only run the loop if its been MS_PER_FRAME time.
        # This way we're not updating it as fast as we can!
        # Keeps your computer from working too hard!
        if time.time() - TimeInfo.stop_watch < TimeInfo.MS_PER_FRAME:
            continue

        # Update the timing info
        # Basically calculate how much time has passed since the last time we updated the screen
        current_time = time.time()
        TimeInfo.delta_time = current_time - TimeInfo.stop_watch
        while current_time - TimeInfo.stop_watch >= TimeInfo.MS_PER_FRAME:
            TimeInfo.delta_time += TimeInfo.MS_PER_FRAME
            TimeInfo.stop_watch += TimeInfo.MS_PER_FRAME
        TimeInfo.stop_watch = current_time

        
        main_player.turtle.shape(SPACESHIP_SPRITE_INFO['name'])

        # Get the keys that were pressed this frame        
        process_inputs()
        
        # Check collisions
        handle_bullet_asteroid_collisions()
        check_player_collisions()

        # Move the turtles!
        move_turtles([main_player])
        move_turtles(asteroid_buffer)
        move_turtles(bullet_buffer)

        # Animate the player
        animate_player()

        # Draw the screen
        game_window.update()

        if main_player.health <= 0:
            game_running = False

    # Pause on dying
    time.sleep(2)
        

__main__()
