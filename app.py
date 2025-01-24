import pygame
import sys
from time import sleep
from threading import Thread
import random
from pygame.mixer import stop
from watchdict import WatchDict
from time import time

db = WatchDict('user.json')

# Initialize Pygame

pygame.init()

# Initialize the mixer for sound
pygame.mixer.init()

# Load sound effects
jump_sound = pygame.mixer.Sound("assets/jump.mp3")
stop_sound = pygame.mixer.Sound("assets/stop.mp3")
menu_sound = pygame.mixer.Sound("assets/main.mp3")
dead_sound = pygame.mixer.Sound("assets/bat.mp3")
hit_sound = pygame.mixer.Sound("assets/hit.mp3")
cry_sound = pygame.mixer.Sound("assets/cry.mp3")
gamb_sound = pygame.mixer.Sound("assets/gambel.mp3")
# Set up display
width, height = 720, 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Moving Character with Rain")

# Define colors
WHITE = (255, 255, 255)
font = pygame.font.Font('assets/font.otf', 36)  # None uses the default font, 74 is the font size
state = 'menu'
# Sprite sizes
CHARACTER_SIZE = (120, 120)  # Width and height for character
RAIN_SIZE = (45, 75)         # Width and height for rain
DEAD_SIZE = (75, 45)
SPEECH = (230,140)
# Load and scale images
character_image = pygame.image.load("assets/character.png")
character_image = pygame.transform.scale(character_image, CHARACTER_SIZE)

wallpaper = pygame.image.load("assets/wallpaper.png")
wallpaper = pygame.transform.scale(wallpaper, (width, height))

wl2 = pygame.image.load("assets/image.png")
wl2 = pygame.transform.scale(wl2, (width, height))

rain_image = pygame.image.load("assets/rain.png")
rain_image = pygame.transform.scale(rain_image, RAIN_SIZE)

rain_back = pygame.image.load("assets/rain.png")
rain_back = pygame.transform.scale(rain_back, RAIN_SIZE)

speech = pygame.image.load("assets/speech.png")
speech = pygame.transform.scale(speech, SPEECH)

dead = pygame.image.load("assets/dead.png")
dead = pygame.transform.scale(dead, DEAD_SIZE)

# Function to display centered text
def display_centered_text(text, x, y, color=(40,42,54)):
    text_surface = font.render(text, True, color)  # Render the text onto a surface
    text_rect = text_surface.get_rect(center=(x, y))  # Center the text
    screen.blit(text_surface, text_rect)

# Character properties
character_x = width // 2
character_y = height // 2
speed = 15
jumping = False
jump_height = (CHARACTER_SIZE[1] * 3) // 2

# Rain properties
rain_x = width // 2
rain_y = 0
points = 0

lose = False


def gravity():
    global character_y
    if not grounded(character_y):
        character_y += speed / 2

def grounded(y, hit=None):
    if not hit:
        hit = CHARACTER_SIZE[1]
    return y >= height - hit

def jump():
    global character_y, jumping
    jumping = True
    for i in range(jump_height // speed):
        character_y -= speed
        sleep(1 / 60)
    jumping = False



    

def rain_fall():
    global rain_y, rain_x, points, state, rain_image, lose, speed
    rain_y += speed // 2
    if inside_character(rain_x, rain_y):
        rain_y = 0
        rain_x = random.randint(30, width-30)
        points += 1
        hit_sound.play()  # Play hit sound when rain hits character
        speed +=1
    elif grounded(rain_y, RAIN_SIZE[1]):  # Use the height of the rain sprite
        # state = 'menu'
        rain_y = height-DEAD_SIZE[1]
        
        lose = True
        rain_image = dead
        dead_sound.play()
        cry_sound.play()
        if points > db.get('top_score', 0):
            db['top_score'] = points

    elif rain_y <= speed//2:
        jump_sound.play()

giggle = 0        

def inside_character(x, y):
    return (character_x < x < character_x + CHARACTER_SIZE[0]) and (character_y < y < character_y + CHARACTER_SIZE[1])

menu_sound.play(1)
stop_sound.play(1)
stop_sound.set_volume(0)
last = [random.randint(20, 30), 0]

def get_rand():
    global last
    if time()-last[1] >= 0.1:
        last = [random.randint(20, 30), time()]
    return last[0]

# Main loop
while True:
    keys = pygame.key.get_pressed()
    if state == 'menu':
        stop_sound.set_volume(0)
        if menu_sound.get_volume() == 0:
            menu_sound.stop()
            menu_sound.play()
            menu_sound.set_volume(1)
        screen.blit(wallpaper, (0, 0))
        
        

        
        display_centered_text(f'Top score: {db.get("top_score", 0)}',width//2, height-get_rand())
        points = 0
        speed = 25

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # Check for key presses
                if event.key == pygame.K_RETURN:
                    state = 'game'
                    gamb_sound.play()
        
    elif state == 'stop':
        if stop_sound.get_volume() == 0:
            stop_sound.stop()
            stop_sound.play()
            stop_sound.set_volume(1.5)
        
        screen.blit(wallpaper, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # Check for key presses
                if event.key == pygame.K_RETURN:
                    state = 'game'
    else:
        menu_sound.set_volume(0)
        stop_sound.set_volume(0)
        gravity()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and lose:
                rain_image = rain_back
                rain_y = 0
                lose = False
                rain_x = width//2
                state = 'menu'
        # Get keys pressed
        if not lose:
            if keys[pygame.K_LEFT]:
                character_x -= speed
            if keys[pygame.K_RIGHT]:
                character_x += speed
            if keys[pygame.K_UP] and grounded(character_y):
                Thread(target=jump).start()
            if keys[pygame.K_ESCAPE]:
                state='stop'
            rain_fall()
        

        # Fill the screen with white
        screen.fill(WHITE)
        screen.blit(wl2, (0,0))
        # Draw the character and rain
        screen.blit(character_image, (character_x, character_y))
        screen.blit(rain_image, (rain_x, rain_y))
        
        # Display points
        display_centered_text(f'{points}', character_x, character_y)
        if lose:
            screen.blit(speech, (rain_x, rain_y-120))
        # Update the display
        
        
        
        # Cap the frame rate
    pygame.display.flip()
    pygame.time.Clock().tick(60)