import pygame
from pygame.locals import *
import sys
from os.path import join
import random

# Initializing pygame
pygame.init()

# Setting up clock
game_clock = pygame.time.Clock()
game_fps = 60

# Creating the game window
game_width = 750
game_height = 600
icon = pygame.image.load(join('assets', 'images', 'icon.png'))
pygame.display.set_icon(icon)
pygame.display.set_caption('Floppy Bird')
display_screen = pygame.display.set_mode((game_width, game_height))

# Loading images
background_image = pygame.image.load(join('assets', 'images', 'background.png'))
base_image = pygame.image.load(join('assets', 'images', 'base.png'))
_, _, base_width, base_height = base_image.get_rect()
button_image = pygame.image.load(join('assets','images','restart.png'))

# Scrolling parameters
scroll = 0
scroll_speed = 4

# Game state variables
fly = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks()

# score and text
pipe_pass = False
score = 0
score_font = pygame.font.SysFont('Helvetica',60)
score_color = (149, 116, 255)
manual = True

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = game_height/2
    global score
    score = 0
    pygame.time.delay(100)

# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # Loading bird images
        self.image_list = [pygame.transform.scale(pygame.image.load(join('assets', 'images', f'bird_{i}.png')), (27, 27)) for i in range(1, 4)]
        self.index = 0
        self.count = 0
        self.vel = 0
        self.button_click = True
        self.image = self.image_list[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        global game_over
        # Gravity
        if fly and not game_over:
            self.vel += 0.2
            if self.vel > 8:
                self.vel = 0
            if self.rect.bottom < game_height - base_height * 0.4 and self.rect.top > 0:
                self.rect.y += self.vel
            else:
                game_over = True

        if game_over:
            if self.rect.bottom < game_height - base_height * 0.4:
                self.rect.bottom += 5
            else:
                self.rect.bottom = game_height - base_height * 0.4

        # Jump
        mouse = pygame.mouse.get_pressed()
        if mouse[0] and self.button_click and not game_over:
            self.button_click = False
            self.vel -= 4
        if mouse[0] == 0:
            self.button_click = True
        # Bird image animation
        self.count += 1
        flap_cool = 5
        if self.count > flap_cool:
            self.index = (self.index + 1) % len(self.image_list)
            self.count = 0
        self.image = pygame.transform.rotate(self.image_list[self.index], -self.vel * 2) if not game_over else pygame.transform.rotate(self.image_list[1], -90)

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(join('assets', 'images', 'pipe.png'))
        self.rect = self.image.get_rect()
        # Position 1 is for top and -1 is for bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, flip_x=False, flip_y=True)
            self.rect.bottomleft = [x, y - (pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + (pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class button():
    def __init__(self,x,y,img):
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = [x,y]
    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        display_screen.blit(self.image,(self.rect.x,self.rect.y))
        return action

def draw_text(text,font,text_col,x=game_width/2,y=5):
    img = font.render(text,True,text_col)
    display_screen.blit(img,(x,y))

# Sprite groups
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

# Creating the bird and adding it to the group
flappy = Bird(100, int(game_height / 2))
bird_group.add(flappy)
btn = button(int(game_width/2)-150,int(game_height/2)-100,button_image)

# Main game loop
run = True
while run:
    game_clock.tick(game_fps)
    display_screen.blit(background_image, (0, 0))
    if manual :
        draw_text('Click Mouse Left to ARISE!!!!', score_font,score_color,50,100)
        if fly == True:
            manual = False
    bird_group.draw(display_screen)
    bird_group.update()

    pipe_group.draw(display_screen)
    display_screen.blit(base_image, (0, game_height - base_height * 0.4))
    if len(pipe_group) > 0:
        if  bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
        and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
        and pipe_pass == False:
            pipe_pass = True
        if pipe_pass == True and bird_group.sprites()[0].rect.right > pipe_group.sprites()[0].rect.right:
            score += 1
            pipe_pass = False

    # Check for collision with pipes
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):
        game_over = True

    # Game logic when not game over and flying
    if not game_over and fly:
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            bottom_pipe = Pipe(game_width, int(game_height / 2) + pipe_height, -1)
            top_pipe = Pipe(game_width, int(game_height / 2) + pipe_height, 1)
            pipe_group.add(bottom_pipe, top_pipe)
            last_pipe = current_time

        # Scroll
        pipe_group.update()
        for i in range(2):
            display_screen.blit(base_image, (i * base_width + scroll, game_height - base_height * 0.4))
        scroll -= scroll_speed
        if abs(scroll) > base_width:
            scroll = 0
    #check for game over and reset
    if game_over == True:
        if btn.draw() == True:
            game_over = False
            reset_game()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            fly = True
            break
    draw_text(str(score),score_font,score_color)

    pygame.display.update()

# Clean up and exit the game
pygame.quit()
sys.exit()
