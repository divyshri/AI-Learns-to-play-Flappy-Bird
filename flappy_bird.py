"""
The classic game of flappy bird. Make with python
and pygame. Features pixel perfect collision using masks :o

"""

#importing all the required libraries
import pygame
import random
import os
import time
import neat
import pickle

pygame.font.init()  # init font
#Set the Screen Width
WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730

STAT_FONT = pygame.font.SysFont("comicsans", 50)        #Font To display Score
END_FONT = pygame.font.SysFont("comicsans", 70)         
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

#Importing all the Required Images
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("images","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("images","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("images","base.png")).convert_alpha())

gen = 0

#Class Bird to handle all the operation of flappy bird
class Bird:
    
    MAX_ROTATION = 25               #Maximum angle to tilt bird upward or downward
    IMGS = bird_images              #Make a copy of bird Images
    ROT_VEL = 20                    #How much we rorate the bird at each frame or at each time we move the bird
    ANIMATION_TIME = 5              #How long an each bird animation will be shown

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x                  #Starting position of bird
        self.y = y
        self.tilt = 0               #How much degree an image will be tilted
        self.tick_count = 0         #How Many times we have jumped from last time
        self.vel = 0                #Speed of bird
        self.height = self.y        #Origin of the bird from where bird is start moving
        self.img_count = 0          #Keep track of the current showing Image
        self.img = self.IMGS[0]     #Initialize first bird

    def jump(self):
        self.vel = -10.5            #Starting with going Upward i.e -ve direction
        self.tick_count = 0
        self.height = self.y

    def move(self):
        
        self.tick_count += 1
        
        
        #How many pixel we are moving Up and Down based on the current bird velocity of the bird
		#Intially (-10.5*1 + 1.5*1**2 = -9 )  which results the bird going upward from -10.5 to -9
        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 1.5*(self.tick_count)**2  

        #Terminal Velocity from which we are not accepting to accelarate any more
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:        #If you are moving upward just move little more
            displacement -= 2
            
            
        #Whatever the Displacement is calculated add to the current position of the bird
        self.y = self.y + displacement

        #Tilt the bird up if current position is above the starting position keep pointing upward
        if displacement < 0 or self.y < self.height + 50:  
            if self.tilt < self.MAX_ROTATION:       #Defined maximum rotation
                self.tilt = self.MAX_ROTATION
        else:                                       #Tilt down
            if self.tilt > -90:                     #Rotate the bird completely downward
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:           #Less than 5 show first image
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:       #Less than 10 show first image
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:       #Less than 15 show third image
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:       #Less than 20 show second image
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:   #Equal to 21 show first image
            self.img = self.IMGS[0]
            self.img_count = 0                              #Reset the Image Count

        # So when bird is nose diving it isn't flapping
        # Downward going bird dosent flap 
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            #Just to make sure that when again bird goes up it start with flat wings
            self.img_count = self.ANIMATION_TIME*2          


        #Tilt the bird as it is going Downward and Upward
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        #To handle collision of our object pack the bird image in a sqaure shape
        return pygame.mask.from_surface(self.img)


class Pipe():
    
    GAP = 200           #Defines the gap between two pipes
    VEL = 5             #Velocity of pipe moving backward as we know that bird remains at same position

    def __init__(self, x):
        #Y is not included because the height of the pipe is completely random at every time
        self.x = x              
        self.height = 0

        # where the top and bottom of the pipe is to be drawn
        self.top = 0
        self.bottom = 0
        #Rotate the image of the pipe towards downward facing because the default image is facing upward
        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False     #Check if the bird is already passed the pipe

        self.set_height()

    def set_height(self):
        #Define the range where we want to our pipe to be 
        self.height = random.randrange(50, 450)
        #To get the location where exactly the top pipe is drawn is height is subtracted from random placing height
        self.top = self.height - self.PIPE_TOP.get_height()
        #To draw the bottom pipe we just have to add the gap to the random location to get the required location
        self.bottom = self.height + self.GAP

    def move(self):
        #Move pipe based on vel
        self.x -= self.VEL

    def draw(self, win):
        #Draw both the top and bottom of the pipe
        #Draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        #Draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        #Returns if a point is colliding with the pipe
        
        bird_mask = bird.get_mask()         #Call the mask method in Bird Class

        #Create a mask for top pipe and bottom pipe
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        #Offset is calculate to determine how far actually two objects are
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        #Finding the point of Collision or point of overlapand if dosent collide it return false
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point = bird_mask.overlap(top_mask,top_offset)

        #If any of the of points return true i.e. the bird collided with the pipe
        if bottom_point or top_point:
            return True

        return False

class Base:
    #Represnts the moving floor of the game
    VEL = 5                         #It must be same as pipe velocity
    WIDTH = base_img.get_width()    #Image Width
    IMG = base_img                  #Image of the base

    def __init__(self, y):
        self.y = y                  #Cordinate y to place the image
        self.x1 = 0                 #Set First image to the starting point of the screen
        self.x2 = self.WIDTH        #Set Second Image to the ending point of the screen

    def move(self):
        #Move floor so it looks like its scrolling
        self.x1 -= self.VEL         #Move First Image as per the velocity
        self.x2 -= self.VEL         #Move Second Image as per the velocity
        
        if self.x1 + self.WIDTH < 0:            #Check if the first Image if out of Frame
            self.x1 = self.x2 + self.WIDTH      #Set The First Image just Behind the second Image

        if self.x2 + self.WIDTH < 0:            #Check if the Second Image if out of Frame
            self.x2 = self.x1 + self.WIDTH      #Set The Second Image just Behind the First Image

    def draw(self, win):
        #Draw the floor. This is two images that move together.
        
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # draw bird
        bird.draw(win) 

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))       #Draw Score Such that it keeps adjust with window size

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    global WIN, gen
    win = WIN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
                pipe_ind = 1                                                                 # pipe on the screen for neural network input

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        # break if score gets large enough
        '''if score > 20:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break'''


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
     
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
