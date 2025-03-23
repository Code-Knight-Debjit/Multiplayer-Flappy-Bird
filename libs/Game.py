import pygame
import random
import time
import pickle
import sys
from libs import pvp_V2_1 as Player_VS_Player
from libs import pvc_V2_6 as Player_VS_Computer

pygame.init()
pygame.font.init()
Continue_playing = True

WINNER_FONT = font = pygame.font.SysFont("comicsans", 25)
STAT_FONT = pygame.font.SysFont("comicsans", 25)
SCORE_FONT = font = pygame.font.SysFont("comicsansms", 50)
DEVELOPER_FONT = font = pygame.font.SysFont("comicsans", 35)
COUNT_DOWN_FONT = pygame.font.SysFont("impact", 180)
POINT_FONT = pygame.font.SysFont("arialblack", 35)
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800


BIRD_IMGS_COMPUTER = [pygame.transform.scale2x(pygame.image.load("imgs/bird1.png")), pygame.transform.scale2x(pygame.image.load("imgs/bird2.png")), pygame.transform.scale2x(pygame.image.load("imgs/bird3.png"))]
BIRD_IMGS_PLAYER = [pygame.transform.scale2x(pygame.image.load("imgs/bird1_player.png")), pygame.transform.scale2x(pygame.image.load("imgs/bird2_player.png")), pygame.transform.scale2x(pygame.image.load("imgs/bird3_player.png"))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load("imgs/pipe.png"))
BG_IMG = pygame.transform.scale2x(pygame.image.load("imgs/bg.png"))
BASE_IMG = pygame.transform.scale2x(pygame.image.load("imgs/base_dual.png"))
START_IMG = pygame.image.load("imgs/Start.png")
PVP_IMG = pygame.image.load("imgs/PVP.png")
PVC_IMG = pygame.image.load("imgs/PVC.png")
END_PAGE = pygame.image.load("imgs/End Page.png")
READY_IMG = pygame.image.load("imgs/Get Ready.png")
READY_PC_IMG = pygame.image.load("imgs/Get Ready PC.png")

GAME_OVER = pygame.mixer.Sound("sounds/game over.mp3")
COUNTDOWN_5_TO_1 = pygame.mixer.Sound("sounds/5 to 1 countdown.mp3")




pvp_button = pygame.Rect(535, 244, 230, 100)
pvc_button = pygame.Rect(535, 412, 230, 100)
play = pygame.Rect(585, 425, 130, 60)

easy = pygame.Rect(600, 268, 130, 55)
medium = pygame.Rect(600, 343, 130, 55)
hard = pygame.Rect(600, 421, 130, 55)

start = True
pvp_page = False
pvc_page = False
ready_page = False
ready_PC_page = False

difficulty = None

player1_status = font.render("NOT READY" , True, (255,0,0))
player2_status = font.render("NOT READY" , True, (255,0,0))

player_status = font.render("NOT READY" , True, (255,0,0))

again = pygame.Rect(600, 470, 115, 60)
quit_button = pygame.Rect(740, 470, 105, 60)

pygame.mixer.music.load("sounds/bg music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)


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

def Drawn(win, birds, pipes, base, pvp_button, pvc_button, start, pvp_page, pvc_page, player1_name, player2_name, time_secs, player1_name_save, player2_name_save, count_down_img):
    global ready_page, ready_PC_page
    win.blit(BG_IMG, (0, 0))
    birds_AI = birds[1]

    win.blit(BG_IMG, (500, 0))
    win.blit(BG_IMG, (1000, 0))
    birds_player = birds[2]
    


    birds_player.draw(win)
    birds_AI.draw(win)
    
    for pipe in pipes:
        pipe.draw(win)
    
    base.draw(win)
    pygame.draw.rect(win, (0,0,0), pvp_button)
    pygame.draw.rect(win, (0,0,0), pvc_button)
    pygame.draw.rect(win, (0,0,0), play)
    if start:
        win.blit(START_IMG, (500,0))
    if pvp_page:
        win.blit(PVP_IMG, (500,0))
    if pvc_page:
        win.blit(PVC_IMG, (500,0))
    text_surface = font.render(player1_name, True, (255,255,255), (0, 255, 0))
    win.blit(text_surface, (530, 60))
    text_surface = font.render(player2_name, True, (255,255,255), (0, 255, 0))
    win.blit(text_surface, (530,130))
    text_surface = font.render(time_secs, True, (0,0,0))
    win.blit(text_surface, (640, 710))
    
    if ready_page:
        win.blit(READY_IMG, (0, 0))
        win.blit(font.render(player1_name_save, True, (0, 255, 0)),(100, 240))
        win.blit(font.render(player2_name_save, True, (0, 255, 0)),(900, 235))
        win.blit(player1_status, (200,390))
        win.blit(player2_status, (1020,390))
        win.blit(count_down_img, (610, 200))
    if ready_PC_page:
        win.blit(READY_PC_IMG, (0, 0))
        win.blit(player_status, (580,185))
        win.blit(count_down_img, (610, 250))


    pygame.display.update()

with open("libs/flappy2 v1.3.pickle", "rb") as flappy_ai:
    net = pickle.load(flappy_ai)
def main():
    global pvp_page, pvc_page, start, ready_page,ready_PC_page, player1_status, player2_status, player_status
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird - Developed By Debjit Paul")
    nets = [net]
    birds = [Bird(230, 350), Bird(1130, 350), Bird(330, 350)]
    bird_player = birds[0]
    bird_AI = birds[1]
    bird_2nd_AI = birds[2]
    bird_player.IMG = BIRD_IMGS_PLAYER


    run = True
    clock = pygame.time.Clock()
    pipes = [Pipe(600)]
    base = Base(730)
    score_AI = 0
    score_Player = 0
    player1_name = ""
    player1_name_save = ""
    player2_name = ""
    player2_name_save = ""
    time_secs = ""
    first_named = False
    second_named = False
    time_done = False
    Played = False
    start = True
    pvp_page = False
    pvc_page = False
    player1_ready = False
    player2_ready = False
    player_ready = False
    ready_page = False
    ready_PC_page = False
    countdown_not_done = True
    count_down_img = font.render(" ", True, (0,0,0))
    count_down = 5
    player1_status = font.render("NOT READY" , True, (255,0,0))
    player2_status = font.render("NOT READY" , True, (255,0,0))

    player_status = font.render("NOT READY" , True, (255,0,0))

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pvp_button.collidepoint(pos) and not pvp_page and not pvc_page:
                    start = False
                    pvp_page = True
                if pvc_button.collidepoint(pos) and not pvp_page and not pvc_page:
                    start = False
                    pvc_page = True
                    
                if first_named and second_named and time_done and play.collidepoint(pos):
                    pvp_page = False
                    ready_page = True


                if pvc_page and time_done and easy.collidepoint(pos):
                    ready_PC_page = True
                    pvc_page = False
                    difficulty = "easy"
                if pvc_page and  time_done and medium.collidepoint(pos):
                    ready_PC_page = True
                    pvc_page = False
                    difficulty = "medium"
                if pvc_page and  time_done and hard.collidepoint(pos):
                    ready_PC_page = True
                    pvc_page = False
                    difficulty = "hard"

            elif event.type == pygame.KEYDOWN and not first_named and pvp_page:
                if event.key == pygame.K_RETURN:  # Enter key pressed
                    player1_name_save = player1_name
                    first_named = True
                    
                elif event.key == pygame.K_BACKSPACE:
                    player1_name = player1_name[:-1]  # Remove the last character
                else:
                    player1_name += event.unicode  # Add the character to the string
            elif event.type == pygame.KEYDOWN and not second_named and pvp_page:
                if event.key == pygame.K_RETURN:  # Enter key pressed
                    player2_name_save = player2_name
                    second_named = True
                    
                elif event.key == pygame.K_BACKSPACE:
                    player2_name = player2_name[:-1]  # Remove the last character
                else:
                    player2_name += event.unicode  # Add the character to the string
            elif event.type == pygame.KEYDOWN and not time_done and (pvp_page or pvc_page):
                if event.key == pygame.K_RETURN:  # Enter key pressed
                    time_save = time_secs
                    time_done = True
                    
                elif event.key == pygame.K_BACKSPACE:
                    time_secs = time_secs[:-1]  # Remove the last character
                else:
                    time_secs += event.unicode  # Add the character to the string

            if event.type == pygame.KEYDOWN and ready_page:
                if event.key == pygame.K_w:
                    player1_status = font.render("READY" , True, (0,255,0))
                    player1_ready = True
                if event.key == pygame.K_UP:
                    player2_status = font.render("READY" , True, (0,255,0))
                    player2_ready = True

            if event.type == pygame.KEYDOWN and ready_PC_page:
                if event.key == pygame.K_SPACE:
                    player_status = font.render("READY" , True, (0,255,0))
                    player_ready = True

        Drawn(win, birds, pipes, base, pvp_button, pvc_button, start, pvp_page, pvc_page, player1_name, player2_name, time_secs, player1_name_save, player2_name_save, count_down_img)
        if player1_ready and player2_ready:
            count_down_img = COUNT_DOWN_FONT.render(str(count_down), True, (27,112,91))
            time.sleep(1)
            if countdown_not_done:
                COUNTDOWN_5_TO_1.play()
                countdown_not_done = False
            count_down -= 1
            if count_down < 0:
                Played = True
                player1_score, player2_score = Player_VS_Player.main(player1_name_save, player2_name_save, time_save)
                GAME_OVER.play()


        if player_ready:
            count_down_img = COUNT_DOWN_FONT.render(str(count_down), True, (27,112,91))
            time.sleep(1)
            if countdown_not_done:
                COUNTDOWN_5_TO_1.play()
                countdown_not_done = False
            count_down -= 1
            if count_down < 0:
                Played = True
                if difficulty =="easy":
                    player1_score, player2_score = Player_VS_Computer.main(1, time_save)
                    GAME_OVER.play()
                if difficulty =="medium":
                    player1_score, player2_score = Player_VS_Computer.main(5, time_save)
                    GAME_OVER.play()
                if difficulty =="hard":
                    player1_score, player2_score = Player_VS_Computer.main(10, time_save)
                    GAME_OVER.play()
        if Played:
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

        output = nets[0].activate((bird_2nd_AI.y, abs(bird_2nd_AI.y - pipes[pipe_index].height), abs(bird_2nd_AI.y - pipes[pipe_index].bottom)))
        if output[0] > 0.5:
            bird_2nd_AI.jump()



        rem = []
        add_pipe = False

            
        for pipe in pipes:
                
            if (not pipe.passed and pipe.x < bird_AI.x) and (not pipe.passed and pipe.x < bird_player.x):
                pipe.passed = True
                add_pipe = True
                    
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            pipe.move()
            
        if add_pipe:
            score_AI += 10
            score_Player += 10
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        base.move()


    return (player1_score, player2_score, pvc_page, "Player", "Computer") if pvc_page else (player1_score, player2_score, pvc_page, player1_name_save, player2_name_save)


def overall_showcase():
    global Continue_playing
    
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    run = True
    quit_button_collide = False
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if again.collidepoint(pos):
                    Continue_playing = True
                    run = False
                if quit_button.collidepoint(pos):
                    Continue_playing = False
                    run = False
                    quit_button_collide = True
                
        win.blit(END_PAGE, (0,0))
        small_player_bird = pygame.transform.scale(BIRD_IMGS_PLAYER[1], (90, 70)).convert_alpha()
        small_AI_bird = pygame.transform.scale(BIRD_IMGS_COMPUTER[1], (80, 70)).convert_alpha()
        small_player_bird.set_alpha(100)
        small_AI_bird.set_alpha(100)
        win.blit(small_player_bird, (600, 270))
        win.blit(small_AI_bird, (760, 270))

        if Played_with_AI:
            players_score = player_score
            AI_score = player_or_AI_score
            winner = BIRD_IMGS_COMPUTER[1] if players_score < AI_score else BIRD_IMGS_PLAYER[1] if players_score > AI_score else font.render("TIE", True, (0,0,0))
            players_score_img = POINT_FONT.render(str(player_score), True, (0, 0, 0))
            AI_score_img = POINT_FONT.render(str(AI_score), True, (0, 0, 0))

            win.blit(winner, (465, 280))
            win.blit(players_score_img, (615, 280))
            win.blit(AI_score_img, (765, 280))
        else:
            player1_score = player_score
            player2_score = player_or_AI_score
            winner = BIRD_IMGS_COMPUTER[1] if player1_score < player2_score else BIRD_IMGS_PLAYER[1] if player1_score > player2_score else font.render("TIE", True, (0,0,0))
            player1_score_img = POINT_FONT.render(str(player1_score), True, (0, 0, 0))
            player2_score_img = POINT_FONT.render(str(player2_score), True, (0, 0, 0))

            win.blit(winner, (465, 280))
            win.blit(player1_score_img, (615, 280))
            win.blit(player2_score_img, (765, 280))
        
        pygame.display.update()
    if quit_button_collide:
        pygame.quit()
        sys.exit()

while Continue_playing:
    player_score, player_or_AI_score, Played_with_AI, player_name, player_or_AI_name = main()
    overall_showcase()