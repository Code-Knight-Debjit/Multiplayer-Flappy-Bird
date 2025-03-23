import pygame
import random
import time
import pickle
import sys


pygame.init()
pygame.font.init() 

STAT_FONT = pygame.font.SysFont("comicsans", 25)
SCORE_FONT = font = pygame.font.SysFont("comicsansms", 50)
DEVELOPER_FONT = font = pygame.font.SysFont("comicsans", 35)
NAME_FONT = pygame.font.SysFont("comicsans", 50)
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800


BIRD_IMGS_COMPUTER = [pygame.transform.scale2x(pygame.image.load("imgs/bird1.png")), pygame.transform.scale2x(pygame.image.load("imgs/bird2.png")), pygame.transform.scale2x(pygame.image.load("imgs/bird3.png"))]
BIRD_IMGS_PLAYER = [pygame.transform.scale2x(pygame.image.load("imgs/bird1_player.png")), pygame.transform.scale2x(pygame.image.load("imgs/bird2_player.png")), pygame.transform.scale2x(pygame.image.load("imgs/bird3_player.png"))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load("imgs/pipe.png"))
BG_IMG = pygame.transform.scale2x(pygame.image.load("imgs/bg.png"))
BASE_IMG = pygame.transform.scale2x(pygame.image.load("imgs/base_dual.png"))
SCORE_IMG = pygame.image.load("imgs/Score and Credit.png")

FLYING_SOUND = pygame.mixer.Sound("sounds/flying sound.mp3")
HITTING_PIPE = pygame.mixer.Sound("sounds/hitting pipe.mp3")
HITTING_GROUND = pygame.mixer.Sound("sounds/hitting ground.mp3")
TIME_UP_WARNING = pygame.mixer.Sound("sounds/time_up_warning.mp3")

FLYING_SOUND.set_volume(0.5)
HITTING_GROUND.set_volume(0.5)
HITTING_PIPE.set_volume(0.5)
TIME_UP_WARNING.set_volume(0.15)

time_up = True

class Bird():
    IMG = BIRD_IMGS_COMPUTER
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5
    ACCELARATION = 3
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMG[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        s = self.vel*self.tick_count + 0.5*self.ACCELARATION*(self.tick_count**2)

        if s >= 16:
            s = 16
        if s < 0:
            s -= 2
        
        self.y = self.y + s

        if s < 0 or self.y < self.height:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL


    def draw(self, win):
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMG[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMG[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMG[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMG[1]
        elif self.img_count == self.ANIMATION_TIME*4+1:
            self.img = self.IMG[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMG[1]
            self.img_count = self.ANIMATION_TIME*2


        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe():
    """
    represents a pipe object
    """
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.x_player = x + 800
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL
        self.x_player = (self.x_player - self.VEL) if self.x_player > 500 else self.x_player 
 
    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_TOP, (self.x_player, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        win.blit(self.PIPE_BOTTOM, (self.x_player, self.bottom))


    def collide(self, bird, pipe_x):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (pipe_x - bird.x, self.top - round(bird.y))
        bottom_offset = (pipe_x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False


class Base():
    """
    Represnts the moving floor of the game
    """
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def Draw(win, birds, pipes, base, score_AI, score_Player, time_left):
    global time_up
    win.blit(BG_IMG, (0, 0))
    birds_AI = birds[1]
    birds_player = birds[0]
    birds_player.draw(win)
    win.blit(BG_IMG, (800, 0))
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)
    birds_AI.draw(win)
    win.blit(SCORE_IMG, (500,0))

    player_name = NAME_FONT.render("Player", True, (255,255,255))
    win.blit(player_name, (20,5))
    Score_Head_display_player = STAT_FONT.render(f" PLAYER SCORE: ", 1, (163,73,164))
    win.blit(Score_Head_display_player, (543,46))
    Score_display_Player = SCORE_FONT.render(f"{score_Player} ", 1, (163,73,164))
    win.blit(Score_display_Player, (600, 90))

    player_name = NAME_FONT.render("Computer", True, (255,255,255))
    win.blit(player_name, (820,5))
    Score_Head_display_AI = STAT_FONT.render(f"COMPUTER SCORE: ", 1, (255,201,14))
    win.blit(Score_Head_display_AI, (540, 278))
    Score_display_AI = SCORE_FONT.render(f"{score_AI} ", 1, (255,201,14))
    win.blit(Score_display_AI, (600, 320))

    Developer_Head = STAT_FONT.render(f" Developed By---: ", 1, (255,255,255))
    win.blit(Developer_Head, (550,550))
    Developer_name = DEVELOPER_FONT.render(f"DEBJIT PAUL ", 1, (255,255,255))
    win.blit(Developer_name, (533, 620))
    if int(time_left) > 5:
        time_left_img = STAT_FONT.render(f"Time Left: {time_left}", True, (0,255,0), (0,0,0))
        win.blit(time_left_img, (570, 700))
    else:
        time_left_img = STAT_FONT.render(f"Time Left: {time_left}", True, (255,0,0), (255,255,255))
        win.blit(time_left_img, (570, 700))
        if time_up:
            TIME_UP_WARNING.play()
            time_up = False


    pygame.display.update()

with open("libs/flappy2 v1.3.pickle", "rb") as flappy_ai:
    net = pickle.load(flappy_ai)
def main(score, time_to_run):
    global time_up
    # pygame.mixer.music.load("sounds/bg music.mp3")
    # pygame.mixer.music.set_volume(0.25)
    # pygame.mixer.music.play(-1)
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    nets = [net]
    birds = [Bird(230, 350), Bird(1130, 350)]
    bird_player = birds[0]
    bird_AI = birds[1]
    bird_player.IMG = BIRD_IMGS_PLAYER


    run = True
    clock = pygame.time.Clock()
    pipes = [Pipe(600)]
    base = Base(730)
    score_AI = 0
    score_Player = 0
    start_time = time.time()
    hitting_ground = True
    hitting_pipe = True
    next = False
    next2 = False
    time_up = True


    while run:
        time_elpsed = time.time() - start_time
        time_left = str(round(int(time_to_run) - time_elpsed))
        if time_elpsed > int(time_to_run):
            run = False
        
        clock.tick(30)

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and bird_AI.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1
        else:
            run = False
            break

        for bird in birds:
            bird.move()

        output = nets[0].activate((bird_AI.y, abs(bird_AI.y - pipes[pipe_index].height), abs(bird_AI.y - pipes[pipe_index].bottom)))

        if output[0] > 0.5:
            bird_AI.jump()

        rem = []
        add_pipe = False

            
        for pipe in pipes:
            if pipe.collide(bird_AI, pipe.x_player):
                score_AI -= 1
            if pipe.collide(bird_player, pipe.x):
                score_Player -= 1
                next = True
                if hitting_pipe:
                    HITTING_PIPE.play()
                    hitting_pipe = False
            else:
                if next:
                    next = False
                    next2 = True
                elif next2:
                    hitting_pipe = True
                    
                
            if (not pipe.passed and pipe.x < bird_AI.x) and (not pipe.passed and pipe.x < bird_player.x):
                pipe.passed = True
                add_pipe = True
                    
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            pipe.move()
            
        if add_pipe:
            score_AI += score
            score_Player += 10
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        base.move()

        if bird_AI.y + bird_AI.img.get_height() >= 730 or bird_AI.y < 0:
            score_AI -= 10
        if bird_player.y + bird_player.img.get_height() >= 730 or bird_player.y < 0:
            score_Player -= 10
            if hitting_ground:
                HITTING_GROUND.play()
                hitting_ground = False
        else:
            hitting_ground = True

        Draw(win, birds, pipes, base, score_AI, score_Player, time_left)



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_player.jump()
                    FLYING_SOUND.set_volume(0.5)
                    FLYING_SOUND.play()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(pos)
    
    return (score_Player, score_AI)

if __name__ == "__main__":
    main(10,10)