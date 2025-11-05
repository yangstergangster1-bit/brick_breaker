# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 19:36:31 2025

@author: Josue
"""

#imports the pygame library

import pygame
import sys

#initiialize pygame
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont("Comic Sans MS", 30)
text_surface = my_font.render("Game Over", False, (0, 0, 0))

#set up the screen



# color values
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")

clock = pygame.time.Clock()



# paddle class/variables
class paddle:
    def __init__(self, x, y, width, height, speed, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
    
    def move(self, keys, screen_width):
        if  keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            
        #keeps it within range of the screen
        
        if self.x < 0:
            self.x = 0
        elif self.x > screen_width - self.width:
            self.x = screen_width - self.width
            
    def draw(self,screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
# ball class/ variable

class ball:
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        
    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
    def bounce_walls(self, screen_width, screen_height):
        if self.x - self.radius <= 0 or self.radius + self.x >= screen_width:
            self.speed_x = self.speed_x * (-1)
        if self.y - self.radius <= 0:
            self.speed_y = self.speed_y * (-1)
                
    def bounce_paddle(self, paddle):
        if (paddle.y <= self.y + self.radius <= paddle.y + paddle.height) and (paddle.x <= self.x <= paddle.x + paddle.width):
            self.speed_y = -self.speed_y
                    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        
    def collide_bricks(self, bricks):
        for brick in bricks:
            if brick.visible:
                if (brick.x <= self.x <= brick.x + brick.width) and \
                (brick.y <= self.y - self.radius <= brick.y + brick.height):
                    self.speed_y = (-1) * self.speed_y
                    brick.visible = False
        

# brick Class

class Brick:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.visible = True
        
    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color ,(self.x ,self.y, self.width, self.height))



#brick Set up
bricks = []
rows = 5
columns = 8
brick_w = WIDTH // columns - 10
brick_h = 25
start_y = 60
    
for row in range(rows):
    for col in range(columns):
        x = col * (brick_w + 10) + 5
        y = start_y + row * (brick_h + 10)
        color = (255, 100 + row * 20, 100)  # different colors
        bricks.append(Brick(x, y, brick_w, brick_h, color))

# game setup i guess:
    

paddle = paddle(WIDTH // 2 - 50, HEIGHT - 40, 100   , 7, 10, BLUE)
ball = ball(WIDTH//2, HEIGHT//2, 10, RED, 4,-4)

clock = pygame.time.Clock()
running= True

# loop the game 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    keys = pygame.key.get_pressed()
    paddle.move(keys, WIDTH)
    
    ball.move()
    ball.bounce_walls(WIDTH, HEIGHT)
    ball.bounce_paddle(paddle)
    ball.collide_bricks(bricks)
        
    screen.fill(WHITE)
       
    for brick in bricks:
        brick.draw(screen)
        
        
    paddle.draw(screen)
    ball.draw(screen)
    
    if ball.y > paddle.y:
        screen.fill(RED)
        screen.blit(text_surface, (0,0))
        
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
sys.exit()  # properly insures that the game ends
            
        
            
