import pygame
import random
import time
import sys


pygame.init()
pygame.font.init() 

STAT_FONT = pygame.font.SysFont("comicsans", 25)
SCORE_FONT = font = pygame.font.SysFont("comicsansms", 50)
DEVELOPER_FONT = font = pygame.font.SysFont("comicsans", 35)
NAME_FONT = pygame.font.SysFont("comicsans", 50)

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

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

def Draw(win, birds, pipes, base, score_Player2, score_Player1, PLAYER1, PLAYER2, time_left):
    global time_up
    win.blit(BG_IMG, (0, 0))
    bird_player2 = birds[1]
    bird_player1 = birds[0]
    bird_player1.draw(win)
    win.blit(BG_IMG, (800, 0))
    for pipe in pipes:
        pipe.draw(win)
    
    base.draw(win)
    bird_player2.draw(win)
    Border = pygame.Rect(500, 0, 300, 800)
    pygame.draw.rect(win, (0,0,0), Border)
    win.blit(SCORE_IMG, (500,0))

    player_name = NAME_FONT.render(f"{PLAYER1}", True, (255,255,255))
    win.blit(player_name, (20,5))
    Score_Head_display_player = STAT_FONT.render(f" {PLAYER1} SCORE: ", 1, (163,73,164))
    win.blit(Score_Head_display_player, (543,46))
    Score_display_Player = SCORE_FONT.render(f"{score_Player1} ", 1, (163,73,164))
    win.blit(Score_display_Player, (600, 90))

    player_name = NAME_FONT.render(f"{PLAYER2}", True, (255,255,255))
    win.blit(player_name, (820,5))
    Score_Head_display_AI = STAT_FONT.render(f" {PLAYER2} SCORE: ", 1, (255,201,14))
    win.blit(Score_Head_display_AI, (540, 278))
    Score_display_AI = SCORE_FONT.render(f"{score_Player2} ", 1, (255,201,14))
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

def main(PLAYER1, PLAYER2, time_to_run):
    global time_up
    # pygame.mixer.music.load("sounds/bg music.mp3")
    # pygame.mixer.music.set_volume(0.25)
    # pygame.mixer.music.play(-1)
    birds = [Bird(230, 350), Bird(1030, 350)]
    bird_player1 = birds[0]
    bird_player2 = birds[1]
    bird_player1.IMG = BIRD_IMGS_PLAYER


    run = True
    clock = pygame.time.Clock()
    pipes = [Pipe(600)]
    base = Base(730)
    score_Player2 = 0
    score_Player1 = 0
    start_time = time.time()
    player1_hitting_ground = True 
    player2_hitting_ground = True 
    player1_hitting_pipe = True 
    player2_hitting_pipe = True 
    player1_next = False
    player1_next2 = False
    player2_next = False
    player2_next2 = False 
    time_up = True

    while run:
        elapsed_time = time.time() - start_time
        time_left = str(round(int(time_to_run) - elapsed_time))
        if elapsed_time > int(time_to_run):
            run = False
        clock.tick(30)
        Draw(win, birds, pipes, base, score_Player2, score_Player1, PLAYER1, PLAYER2, time_left)

        for bird in birds:
            bird.move()

        rem = []
        add_pipe = False

            
        for pipe in pipes:
            if pipe.collide(bird_player2, pipe.x_player):
                score_Player2 -= 1
                player2_next = True
                if player2_hitting_pipe:
                    HITTING_PIPE.play()
                    player2_hitting_pipe = False
            else:
                if player2_next:
                    player2_next = False
                    player2_next2 = True
                elif player2_next2:
                    player2_hitting_pipe = True

            if pipe.collide(bird_player1, pipe.x):
                score_Player1 -= 1
                player1_next = True
                if player1_hitting_pipe:
                    HITTING_PIPE.play()
                    player1_hitting_pipe = False
            else:
                if player1_next:
                    player1_next = False
                    player1_next2 = True
                elif player1_next2:
                    player1_hitting_pipe = True
                
            if (not pipe.passed and pipe.x < bird_player2.x) and (not pipe.passed and pipe.x < bird_player1.x):
                pipe.passed = True
                add_pipe = True
                    
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            pipe.move()
            
        if add_pipe:
            score_Player1 += 10
            score_Player2 += 10
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        base.move()

        if bird_player2.y + bird_player2.img.get_height() >= 730 or bird_player2.y < 0:
            score_Player2 -= 10
            if player2_hitting_ground:
                HITTING_GROUND.play()
                player2_hitting_ground = False
        else:
            player2_hitting_ground = True

        if bird_player1.y + bird_player1.img.get_height() >= 730 or bird_player1.y < 0:
            score_Player1 -= 10
            if player1_hitting_ground:
                HITTING_GROUND.play()
                player1_hitting_ground = False
        else:
            player1_hitting_ground = True




        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    bird_player1.jump()
                    FLYING_SOUND.play()
                if event.key == pygame.K_UP:
                    bird_player2.jump()
                    FLYING_SOUND.play()
    return (score_Player1, score_Player2)
if __name__ == "__main__":
    main("Deb", "Saptarshi", 7)