import pygame
import neat
import time
import os
import random

# constants
WIN_WIDTH = 600
WIN_HEIGHT = 800

# load images
# use scale2x to make the image bigger
# .load() to simply loads the image
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # how much the bird will tilt
    ROT_VEL = 20  # how much we will rotate on each frame
    ANIMATION_TIME = 5  # how long we will show each bird animation

    def __init__(self, x, y):
        # x and y are the starting positions of the bird
        self.x = x
        self.y = y
        self.tilt = 0  # how much the image is tilted
        # figure physic of the bird
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]  # the image of the bird

    def jump(self):
        # the reason the velocity is negative is because the top left corner is (0,0)
        self.vel = -10.5
        self.tick_count = 0  # when we last jump
        # where bird originally jump from
        self.height = self.y

    def move(self):
        self.tick_count += 1
        # physic equation how much we move up or down
        d = self.vel * self.tick_count + 1.5 * self.tick_count**2
        if d >= 16:
            d = 16
        if d < 0:
            # if we moving up we move a little more (fine tuning)
            d -= 2
        self.y = self.y + d
        if d < 0 or self.y < self.height + 50:
            # if we moving up we tilt the bird up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        # how many times we show a single image
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
            # show the first image
            # checking what image to show based on count
            # its for bird animation
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            # reset the image count
            self.img_count = 0

        if self.tilt <= -80:
            # if we are nose diving we dont flap
            self.img = self.IMGS[1]
            # we dont want to flap the wings when we nose diving
            self.img_count = self.ANIMATION_TIME * 2
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            # rotates the image around the center
            center=self.img.get_rect(topleft=(self.x, self.y)).center
        )
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        # for pixel perfect collision
        return pygame.mask.from_surface(self.img)


def draw_window(win, bird):
    win.blit(BG_IMG, (0, 0))
    bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(200, 200)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    # run = false to end the game
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        bird.move()
        draw_window(win, bird)
    pygame.quit()
    quit()
