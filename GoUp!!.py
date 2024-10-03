import pygame
import random
import os
from spritesheet import Spritesheet
from enemy import Enemy
from pygame import mixer



mixer.init()
pygame.init()

screen_width = 400
screen_heigth = 600

screen = pygame.display.set_mode((screen_width, screen_heigth))

pygame.display.set_caption('Go Up!')  

# set frame rate
clock = pygame.time.Clock()
FPS = 60

#load music and sounds
'''
pygame.mixer.music.load('GoUpAssets/music.mp3')
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1,0.0)
'''
jump_fx = pygame.mixer.Sound('GoUpAssets/jump.mp3')
jump_fx.set_volume(0.01)
death_fx = pygame.mixer.Sound('GoUpAssets/death.mp3')
death_fx.set_volume(0.7)

#game variable
SCROLL_THRESH=200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll=0
bg_scroll=0
game_over=False
score=0
fade_counter=0

if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0

  
# define colors 
white = (255,255,255)
BLACK=(0,0,0)
PANEL = (153, 217, 234)

#define font:
font_small=pygame.font.SysFont('Lucida Sans',20)
font_big=pygame.font.SysFont('Lucida Sans',24)


# load images 
mario_image = pygame.image.load('GoUpAssets/sprite.png').convert_alpha()
bg_image = pygame.image.load('GoUpAssets/bg.jpg').convert_alpha()
platform_image = pygame.image.load('GoUpAssets/log.jpg').convert_alpha()
#bird 
bird_sheet_img = pygame.image.load('GoUpAssets/bird.png').convert_alpha()
bird_sheet = Spritesheet(bird_sheet_img)


#function for outputting text

def draw_text(text,font,text_col,x,y):
    img=font.render(text,True,text_col)
    screen.blit(img, (x,y))

#function for drawing info panel

def draw_panel():
    pygame.draw.rect(screen , PANEL, (0,0, screen_width, 30))
    pygame.draw.line(screen, white, (0,30), (screen_width, 30 ), 2)
    draw_text('SCORE ' + str(score), font_small, white, 0, 0)



#function for drawing the background:

def draw_bg(bg_scroll):
    screen.blit(bg_image, (0,0 + bg_scroll))
    screen.blit(bg_image, (0,-600 + bg_scroll))

# player class 
class player():
    def __init__(self, x,y):
        self.image = pygame.transform.scale(mario_image, (30,40))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x,y)
        self.vel_y = 0
        self.flip = False
              

    def move(self):
        # reset variables
        scroll=0
        dx = 0
        dy = 0
        

        # keypress
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx = -10
            self.flip = True
        if key[pygame.K_d]:
            dx = 10
            self.flip = False


        #gravity
        self.vel_y += GRAVITY 
        dy += self.vel_y


        # to ensure player doesnt go outside the window
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.left + dx > screen_width:
            dx = screen_width - self.rect.right

        # check collision w platforms
        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # to check sprite above platform
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20
                        jump_fx.play()
        # to ensure collision w the ground
        '''if self.rect.bottom + dy > screen_heigth:
            dy = 0
            self.vel_y = -20'''

        #to check if the player bounced to top of screen
        if self.rect.top <= SCROLL_THRESH:
            #if player is jumping
            if self.vel_y<0:
             scroll=-dy
 
 
        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy + scroll

        #update mask
        self.mask = pygame.mask.from_surface(self.image)

        return scroll


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False)   , (self.rect.x-1, self.rect.y))
        

# platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.moving = moving
        self.move_counter = random.randint(0,50)
        self.direction = random.choice([-1,1])
        self.speed = random.randint(1,2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self,scroll):
        #moving platfor side to side if it is a moving platform
        if self.moving == True:
            self.move_counter +=1
            self.rect.x += self.direction * self.speed

        #change platform direction if it has move fully or hit a wall
        if self.move_counter >=100 or self.rect.left < 0 or self.rect.right > screen_width:
            self.direction*= -1
            self.move_counter = 0
        #update platforms vertical pos.
        self.rect.y+=scroll

        #check if platform has gone off the screen:

        if self.rect.top > screen_heigth:
            self.kill()


# player instance
mario = player(screen_width // 2, screen_heigth - 150)

# create sprite groups
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

#create temporary platforms
'''for p in range (MAX_PLATFORMS):
    p_w = random.randint(40, 60)
    p_x = random.randint(0, screen_width - p_w)
    p_y = p * random.randint(80,120)
    platform = Platform(p_x, p_y, p_w)
    platform_group.add(platform)'''
#creating a starting platform manually:
platform=Platform(screen_width//2 - 50,screen_heigth-50,100 , False)
platform_group.add(platform)







#mario = player(screen_width // 2, screen_heigth - 150)




# game loop
run = True
while run:

    clock.tick(FPS)


    if game_over==False:
        scroll=mario.move()

        #print(scroll)

        # draw bg
        bg_scroll+=scroll
        if bg_scroll>=600:
            bg_scroll=0
        draw_bg(bg_scroll)

        #draw temporary scroll threshold
        #pygame.draw.line(screen,WHITE,(0,SCROLL_THRESH),(screen_width,SCROLL_THRESH))


        #generate platforms:
        if len(platform_group)< MAX_PLATFORMS:
            p_w=random.randint(40,60)
            p_x=random.randint(0,screen_width - p_w)
            p_y=platform.rect.y - random.randint(80,120)
            p_type = random.randint(1,2)
            if p_type == 1 and score > 500:
                p_moving = True
            else:
                p_moving = False    
            platform=Platform(p_x,p_y,p_w,p_moving)
            platform_group.add(platform)

            


        #update platforms
        platform_group.update(scroll)

        #generate enemies
        if len(enemy_group) == 0 and score > 1500:
            enemy = Enemy(screen_width, 100, bird_sheet, 1.5)
            enemy_group.add(enemy)

        #update enemies
        enemy_group.update(scroll, screen_width)

        
        #update score
        if scroll > 0:
            score += scroll


        


        #draw line at previous highscore
        pygame.draw.line(screen, white,(0, score - high_score + SCROLL_THRESH),(screen_width, score - high_score + SCROLL_THRESH),3)
        draw_text('HIGH SCORE', font_small, BLACK, screen_width - 130, score - high_score + SCROLL_THRESH)  

        # draw sprite
        platform_group.draw(screen)
        enemy_group.draw(screen)
        mario.draw()

        #draw panel
        draw_panel()

        #check game over:
        if mario.rect.top > screen_heigth:
            game_over=True
            death_fx.play()

        #check for collison with enemies
        if pygame.sprite.spritecollide(mario, enemy_group, False):
            if pygame.sprite.spritecollide(mario,enemy_group, False, pygame.sprite.collide_mask):
                game_over = True
                death_fx.play()
    else:
        if fade_counter<screen_width:
            fade_counter+=5
            for y in range(0,6,2):
                pygame.draw.rect(screen,BLACK,(0,y*100,fade_counter,100))
                pygame.draw.rect(screen,BLACK,(screen_width - fade_counter,(y+1)*100,screen_width,100))
        else:
            draw_text('GAME OVER!!',font_big,white,130,200)
            draw_text('SCORE:' + str(score),font_big,white,130,250)
            draw_text('PRESS SPACE TO PLAY AGAIN!',font_big,white,40,300)
        #update high score
        if score > high_score:
            high_score = score
            with open('score.txt','w') as file:
                file.write(str(high_score))
        key=pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            #reset variables:
            game_over=False
            score=0
            scroll=0
            fade_counter=0
            #reposition player
            mario.rect.center =(screen_width // 2, screen_heigth - 150)

            #reset enemies
            enemy_group.empty()


            #reset platforms
            platform_group.empty()

            #creating a starting platform manually:
            platform=Platform(screen_width//2 - 50,screen_heigth-50,100, False)
            platform_group.add(platform)
            

  

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            #update high score
            if score > high_score:
                high_score = score
                with open('score.txt','w') as file:
                    file.write(str(high_score))
            run = False
    


    # update display window
    pygame.display.update()





pygame.quit()