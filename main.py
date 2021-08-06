# Flappy Bird game by Infernocat
# Project began on 7/20/21, finished the day after.

import pygame, random, sys

# Initialize

pygame.init()
pygame.mixer.init()

# Config Variables

HEIGHT = 600
WIDTH = 500
FPS = 60
BACKDROP = (66, 200, 245)

# Important Variables

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
VEC = pygame.math.Vector2

GAME_RUNNING = True
SPACE_PRESSED = False

SCORE = 0

SPRITES = pygame.sprite.Group()
PIPES = pygame.sprite.Group()
BUTTONS = pygame.sprite.Group()

P1 = None
Board = None
Floor = None

# Sprite Images

BIRD = pygame.image.load("images/bird.png").convert_alpha()
PIPE = pygame.image.load("images/pipe.png").convert_alpha()
FLOOR = pygame.image.load("images/ground.png").convert_alpha()
START = pygame.image.load("images/start.png").convert_alpha()

# Sounds

SOUND = {
    "collect": pygame.mixer.Sound("assets/collect.mp3"),
    "hit": pygame.mixer.Sound("assets/death.mp3"),
    "jump": pygame.mixer.Sound("assets/jump.mp3")
}

for i in SOUND.items(): i[1].set_volume(.1)

# Window Settings

pygame.display.set_icon(pygame.image.load("images/logo.png"))
pygame.display.set_caption("Flappy Bird")

# Classes

class Player(pygame.sprite.Sprite):
    def __init__(self):
        global P1
        super().__init__()
        self.image = BIRD
        self.rect = self.image.get_rect(center=(200, HEIGHT / 2 ))
        self.pos = VEC((200, HEIGHT / 2))
        self.jump = 35
        self.speed = .8
        self.vel = .25
        self.gravity = 0
        self.anchored = False
        SPRITES.add(self)
        P1 = self

    def rotate(self):
        self.image = pygame.transform.rotate(BIRD, max(self.gravity * -7, -90))

    def flap(self):
        global SPACE_PRESSED
        if SPACE_PRESSED or self.anchored: return
        self.pos.y -= self.jump
        if self.pos.y <= 0: self.pos.y = 0
        self.rect.y = self.pos.y
        self.gravity = -5
        SOUND["jump"].play()

    def get_hits(self):
        hits = pygame.sprite.spritecollide(self, [sprite for sprite in SPRITES], False)
        hits.remove(self)
        return hits

    def fall(self):
        collisions = self.get_hits()
        if collisions:
            if not self.anchored: stop_everything()
            if collisions[0] == Floor:
                self.pos.y = collisions[0].rect.y
                return
        self.pos.y += self.speed * self.gravity
        self.gravity += self.vel
        self.rect.y = self.pos.y

    def destroy(self):
        SPRITES.remove(self)
        del self

    def update(self):
        self.rotate()
        self.fall()

class Pipe(pygame.sprite.Sprite):
    def __init__(self, style=None, height=None, spacing=None, edit_score: bool=False):
        super().__init__()
        img, ypos = self.get_settings(style, height)
        self.image = img
        self.rect = self.image.get_rect(center=(WIDTH + 25 + spacing, ypos))
        self.speed = 2.8
        self.anchored = False
        self.added = False
        self.edit = edit_score
        PIPES.add(self)
        SPRITES.add(self)
        
    def get_settings(self, style, height):
        if style == "TOP":
            return pygame.transform.rotate(PIPE, 180), height / 2
        elif style == "BOTTOM":
            return PIPE, HEIGHT - height / 2

    def add(self):
        global SCORE
        self.added = True
        SCORE += 1
        SOUND["collect"].play()
        Board.change(text=SCORE)

    def destroy(self):
        SPRITES.remove(self)
        PIPES.remove(self)
        del self

    def update(self):
        global P1
        if self.anchored: return
        self.rect.x -= self.speed
        if self.rect.x <= P1.rect.x and not self.added and self.edit:
            self.add()
        elif self.rect.x < -self.image.get_width():
            self.destroy()

class Ground(pygame.sprite.Sprite):
    def __init__(self):
        global Floor
        super().__init__()
        self.image = FLOOR
        self.rect = self.image.get_rect(center=(WIDTH / 2, HEIGHT))
        SPRITES.add(self)
        Floor = self

    def destroy(self):
        SPRITES.remove(self)
        del self

class Text:
    def __init__(self, text=None):
        global Board
        super().__init__()
        self.font = pygame.font.Font("assets/flappy-font.ttf", 50)
        self.text = text
        Board = self

    def change(self, text=None):
        self.text = str(text)

    def destroy(self):
        del self

    def update(self):
        render = self.font.render(self.text, 1, (255, 255, 255))
        WINDOW.blit(render, ((WIDTH / 2) - render.get_width() / 2, 100 - render.get_height()))

class Button(pygame.sprite.Sprite):
    def __init__(self, image=None, pos=None, click=None):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.clicked = click
        SPRITES.add(self)
        BUTTONS.add(self)

    def destroy(self):
        BUTTONS.remove(self)
        SPRITES.remove(self)
        del self

    def on_click(self):
        self.clicked()
        self.destroy()

# Functions

def get_height(): # messy af
    choice = random.randint(1, 3)
    if choice == 1:
        num = random.randint(0, 120)
        num2 = random.randint(0, 120)
    elif choice == 2:
        num = random.randint(120, 300)
        num2 = random.randint(0, 30)
    else:
        num = random.randint(0, 30)
        num2 = random.randint(120, 300)
    return num, num2

def play():
    global SCORE
    for sprite in SPRITES:
        sprite.destroy()
    SCORE = 0
    Floor = Ground()
    P1 = Player()
    Board = Text(text=str(SCORE))

def stop_everything():
    for sprite in SPRITES:
        sprite.anchored = True
    SOUND["hit"].play()
    Button(image=START, pos=(WIDTH / 2, HEIGHT / 2), click=play)

# Main Loop

play()

while GAME_RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GAME_RUNNING = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                P1.flap()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                SPACE_PRESSED = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for b in BUTTONS:
                if b.rect.collidepoint(event.pos):
                    b.on_click()

    WINDOW.fill(BACKDROP)

    if len(PIPES) == 0:
        for i in range(2):
            top, bottom = get_height()
            spacing = i * random.randint(150, 700)
            Pipe(style="TOP", height=top, spacing=spacing, edit_score=True)
            Pipe(style="BOTTOM", height=bottom, spacing=spacing)

    for sprite in SPRITES:
        if sprite.update: sprite.update()
        WINDOW.blit(sprite.image, sprite.rect)

    Board.update()
    CLOCK.tick(FPS)
    pygame.display.update()

pygame.quit()
sys.exit()
