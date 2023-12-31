import pygame
import neat
import time
import os
import random

# NEAT randomly add node and connection to the network to make it better
# favoring smaller architectures if they are able to solve the problem
# start from simple network and make it more complex as needed


# start by giving position of the bird
###### distance between bird and top pipe and bottom pipe
# input: bird y position, top pipe position, bottom pipe position
# output: jump or not jump in this case
# activation function: tanh <--- hyperbolic tangent function (if its greater than 0.5 jump)
# population size: 100 birds (Gen 0 - 100)
# fitness function: **important** how far the bird gets
# Max generations: 30 if it didnt work after 30 generations then we will stop
pygame.font.init()
# constants
WIN_WIDTH = 500
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
STAT_FONT = pygame.font.SysFont("comicsans", 50)


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


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    # draw two images next to each other so
    # when one image move off the screen the other image will show up
    def move(self):
        # move the base to the left
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        # if the first image is off the screen move it to the right
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        # if the second image is off the screen move it to the right
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        # draw two images next to each other
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()


# make pipes backwards so it looks like its moving
class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        # how tall the pipe is
        self.height = 0
        self.top = 0
        self.bottom = 0
        # where the top and bottom of the pipe is drawn
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        # if the bird has already passed the pipe
        # use for the ai
        self.passed = False
        # define where is the top and bottom of the pipe
        self.set_height()

    def set_height(self):
        # where the top of the pipe is
        self.height = random.randrange(50, 450)
        # where the bottom of the pipe is
        self.top = self.height - self.PIPE_TOP.get_height()
        # where the top of the bottom pipe is
        self.bottom = self.height + self.GAP

    # now we are going to use mask collision
    def collide(self, bird, win):
        # get the mask of the bird
        bird_mask = bird.get_mask()
        # get the mask of the top and bottom pipe
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        # how far away the masks are from each other
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # point of collision if they dont collide
        # it will return none **important**
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
        # if there is a collision return true
        if b_point or t_point:
            return True
        return False

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        # draw the top pipe
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw the bottom pipe
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


def main(genomes, config):
    nets = []
    ge = []
    birds = []
    # genome is a tuple
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    pipes = [Pipe(700)]
    score = 0
    # run = false to end the game
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        # bird.move()
        pipe_ind = 0
        if len(birds) > 0:
            # if there is a bird then we will check the position of the pipe
            if (
                len(pipes) > 1
                and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width()
            ):
                # check the next pipe
                pipe_ind = 1
        else:
            run = False
            break
        for x, bird in enumerate(birds):
            # give the bird a 1 fitness point every second it stays alive
            bird.move()
            # every sec bir stay alive it will get 0.1 fitness
            ge[x].fitness += 0.1
            # give the network the bird position, top pipe position, bottom pipe position
            # normalize the inputs
            output = nets[x].activate(
                (
                    bird.y,
                    abs(bird.y - pipes[pipe_ind].height),
                    abs(bird.y - pipes[pipe_ind].bottom),
                )
            )
            # if the output is greater than 0.5 then jump
            if output[0] > 0.5:
                bird.jump()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                # if collision with pipe and bird end the game
                if pipe.collide(bird, win):
                    # if bird hit the pipe then we will reduce the fitness
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                # when bird passes then it sets to true an generate new one
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()
        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
        for r in rem:
            pipes.remove(r)
        for bird in birds:
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                pass
        base.move()
        draw_window(win, birds, pipes, base, score)


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )
    # create population based on the config file
    p = neat.Population(config)
    # giving output to the terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # call the main function 50 times and pass it all the genome as well as the config file
    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
