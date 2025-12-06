# -*- coding: utf-8 -*-
"""

Created by Josue,Ryan and Samy 2025
"""



import pygame, sys, math, random

pygame.init()
pygame.font.init()

# Setup the screen
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")
clock = pygame.time.Clock()

# Set color values
WHITE      = (255, 255, 255)
LIGHT_BLUE = (120, 200, 255)
DARK_BLUE  = (30, 60, 120)
RED        = (255, 80, 80)
YELLOW     = (255, 230, 100)
PURPLE     = (170, 100, 255)
GREEN      = (100, 255, 100)
ORANGE     = (255, 165, 0)
BLACK      = (0, 0, 0)

# Set fonts
title_font = pygame.font.SysFont("Comic Sans MS", 72, bold=True)
menu_font  = pygame.font.SysFont("Comic Sans MS", 36, bold=True)
small_font = pygame.font.SysFont("Comic Sans MS", 22)

# --------------------------------------------------Classes


class Paddle:
    def __init__(self, x, y, width, height, speed, color):
        self.x = x
        self.y = y
        self.width  = width
        self.height = height
        self.speed  = speed
        self.color  = color

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        # keep on screen
        self.x = max(0, min(WIDTH - self.width, self.x))

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))


class Ball:
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        self.x = x
        self.y = y
        self.radius = radius
        self.color  = color
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def bounce_walls(self):
        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.speed_x *= -1
        if self.y - self.radius <= 0:
            self.speed_y *= -1

    def bounce_paddle(self, paddle):
        prev_x = self.x - self.speed_x
        prev_y = self.y - self.speed_y

        # overlap check using ball radius in order for the edges to count
        overlapping_now = (
            self.x + self.radius >= paddle.x and
            self.x - self.radius <= paddle.x + paddle.width and
            self.y + self.radius >= paddle.y and
            self.y - self.radius <= paddle.y + paddle.height
        )

        if overlapping_now:
            came_from_above = prev_y + self.radius <= paddle.y
            if came_from_above:
                # places the ball just above paddle to avoid sticking
                self.y = paddle.y - self.radius
                self.speed_y = -abs(self.speed_y)

                # angle based on where it hits the paddle
                # ball Physics
                paddle_center = paddle.x + paddle.width / 2
                distance_from_center = self.x - paddle_center
                normalized = distance_from_center / (paddle.width / 2)  # -1 .. 1
                self.speed_x += normalized * 1.5  # tweak if too strong
                self.speed_x += normalized * 1.5

        # clamps the speed so it doesnt get out of control
        self.clamp_speed()


    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def collide_bricks(self, bricks, powerups):
        # previous position
        prev_x = self.x - self.speed_x
        prev_y = self.y - self.speed_y

        for brick in bricks:
            if not brick.visible:
                continue

            # AABB overlap between ball and brick
            if (self.x + self.radius > brick.x and
                self.x - self.radius < brick.x + brick.width and
                self.y + self.radius > brick.y and
                self.y - self.radius < brick.y + brick.height):

                hit_from_top    = prev_y + self.radius <= brick.y
                hit_from_bottom = prev_y - self.radius >= brick.y + brick.height
                hit_from_left   = prev_x + self.radius <= brick.x
                hit_from_right  = prev_x - self.radius >= brick.x + brick.width

                if hit_from_top or hit_from_bottom:
                    self.speed_y *= -1
                elif hit_from_left or hit_from_right:
                    self.speed_x *= -1
                else:
                    self.speed_y *= -1

                brick.visible = False

                # 15% chance to spawn a power-up 
                if random.random() < 0.15:
                    ptype = random.choice(["expand", "shrink", "life", "multiball"])
                    powerups.append(
                        PowerUp(brick.x + brick.width / 2,
                                brick.y + brick.height / 2,
                                ptype)
                    )
                break  # only handle one brick per frame
                
    def clamp_speed(self, max_speed=9):
        
        # limit the magnitude of the velocity vector
        mag = math.hypot(self.speed_x, self.speed_y)
        if mag > max_speed:
            scale = max_speed / mag
            self.speed_x *= scale
            self.speed_y *= scale



class Brick:
    def __init__(self, x, y, width, height, color):
        self.x      = x
        self.y      = y
        self.width  = width
        self.height = height
        self.color  = color
        self.visible = True

    def draw(self):
        if self.visible:
            pygame.draw.rect(screen, self.color,
                             (self.x, self.y, self.width, self.height))


class PowerUp:
    def __init__(self, x, y, ptype):
        self.x = x
        self.y = y
        self.ptype = ptype
        self.width  = 20
        self.height = 20
        self.speed  = 3
        self.color = {
            "expand":    GREEN,
            "shrink":    ORANGE,
            "life":      PURPLE,
            "multiball": RED
        }[ptype]

    def move(self):
        self.y += self.speed

    def draw(self):
        pygame.draw.rect(
            screen, self.color,
            (self.x - self.width // 2,
             self.y - self.height // 2,
             self.width, self.height)
        )
        
        # designs the power up by giving it a corresponding letter
        label = {
            "expand":    "E",
            "shrink":    "P",
            "life":      "L",
            "multiball": "M"
        }[self.ptype]
        text = small_font.render(label, True, BLACK)
        screen.blit(text, (self.x - text.get_width() // 2,
                           self.y - text.get_height() // 2))

    def apply_effect(self, paddle, balls, lives):
        if self.ptype == "expand":
            paddle.width = min(paddle.width + 30, 260)

        elif self.ptype == "shrink":
            #shrinks the paddle
            paddle.width = max(paddle.width - 30, 60)

        elif self.ptype == "life":
            lives += 1

        elif self.ptype == "multiball":
            new_balls = []
            for b in balls:
                # duplicate each ball, flip X for variety
                nb = Ball(b.x, b.y, b.radius, b.color, -b.speed_x, b.speed_y)
                new_balls.append(nb)
            balls.extend(new_balls)

        return lives


# --------------------------------------------------Helper functions

def create_bricks(rows, cols):
    bricks = []
    brick_w = WIDTH // cols - 10
    brick_h = 25
    start_y = 60

    for row in range(rows):
        for col in range(cols):
            x = col * (brick_w + 10) + 5
            y = start_y + row * (brick_h + 10)
            color = random.choice([RED, YELLOW, LIGHT_BLUE, PURPLE])
            bricks.append(Brick(x, y, brick_w, brick_h, color))
    return bricks


def draw_gradient_background():
    for i in range(HEIGHT):
        t = i / HEIGHT
        r = int(DARK_BLUE[0] * (1 - t) + LIGHT_BLUE[0] * t)
        g = int(DARK_BLUE[1] * (1 - t) + LIGHT_BLUE[1] * t)
        b = int(DARK_BLUE[2] * (1 - t) + LIGHT_BLUE[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, i), (WIDTH, i))


# --------------------------------------------------Menus

def main_menu():
    """Main menu: basic entry screen."""
    t = 0
    while True:
        draw_gradient_background()

        # animated title
        title_y = 150 + math.sin(t * 3) * 10
        title = title_font.render("BRICK BREAKER", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, title_y))

        flicker = (math.sin(t * 5) + 1) / 2
        play_color = (255, int(200 * flicker) + 55, int(255 * flicker))

        play_text = menu_font.render("Press [SPACE] to Start", True, play_color)
        diff_text = menu_font.render("Press [D] for Difficulty", True, WHITE)
        quit_text = menu_font.render("Press [Q] to Quit", True, WHITE)
        credits   = small_font.render(
            "Created by Josue, Ryan and Samy",
            True, WHITE
        )

        screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, HEIGHT // 2 + 40))
        screen.blit(diff_text, (WIDTH // 2 - diff_text.get_width() // 2, HEIGHT // 2 + 90))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 140))
        screen.blit(credits,   (WIDTH // 2 - credits.get_width() // 2, HEIGHT - 40))

        pygame.display.flip()
        t += 0.02
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "easy"         # default difficulty
                elif event.key == pygame.K_d:
                    return difficulty_menu()
                elif event.key == pygame.K_q:
                    pygame.quit(); sys.exit()


def difficulty_menu():
    """Difficulty selection submenu: returns 'easy', 'medium', or 'hard'."""
    while True:
        draw_gradient_background()

        title = title_font.render("Select Difficulty", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

        easy_text = menu_font.render("1 - Easy (slow ball, fewer bricks)", True, WHITE)
        med_text  = menu_font.render("2 - Medium (faster ball, more bricks)", True, WHITE)
        hard_text = menu_font.render("3 - Hard (fast ball, small paddle, many bricks)", True, WHITE)
        back_text = small_font.render("Press [ESC] to go back", True, WHITE)

        screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, 230))
        screen.blit(med_text,  (WIDTH // 2 - med_text.get_width() // 2, 280))
        screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, 330))
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "easy"
                if event.key == pygame.K_2:
                    return "medium"
                if event.key == pygame.K_3:
                    return "hard"
                if event.key == pygame.K_ESCAPE:
                    return "easy"


def end_screen(result, difficulty):
    """
    Win/Lose screen.
    result: "win" or "lose"
    returns: "retry", "menu", or "quit"
    """
    while True:
        draw_gradient_background()

        if result == "win":
            main_text = "YOU WIN!"
            color = YELLOW
        else:
            main_text = "GAME OVER"
            color = RED

        title = title_font.render(main_text, True, color)
        info  = small_font.render(f"Difficulty: {difficulty.capitalize()}", True, WHITE)
        retry = menu_font.render("Press [SPACE] to Play Again", True, WHITE)
        menu  = menu_font.render("Press [M] for Main Menu", True, WHITE)
        quit_t= menu_font.render("Press [Q] to Quit", True, WHITE)

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        screen.blit(info,  (WIDTH // 2 - info.get_width() // 2, 230))
        screen.blit(retry, (WIDTH // 2 - retry.get_width() // 2, 300))
        screen.blit(menu,  (WIDTH // 2 - menu.get_width() // 2, 350))
        screen.blit(quit_t,(WIDTH // 2 - quit_t.get_width() // 2, 400))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "retry"
                if event.key == pygame.K_m:
                    return "menu"
                if event.key == pygame.K_q:
                    return "quit"


# -------------------------------------------------Game loop with difficulty

def play_game(difficulty):
    if difficulty == "easy":
        rows, cols   = 5, 8
        ball_speed   = 4
        paddle_width = 140
    elif difficulty == "medium":
        rows, cols   = 8, 10   # more bricks
        ball_speed   = 5
        paddle_width = 120
    else:  # hard
        rows, cols   = 10, 12  # a lot of bricks
        ball_speed   = 6
        paddle_width = 90

    paddle = Paddle(WIDTH // 2 - paddle_width // 2,
                    HEIGHT - 40,
                    paddle_width, 15, 10, WHITE)

    # multiple balls support
    balls = [Ball(WIDTH // 2, HEIGHT // 2, 10, RED, ball_speed, -ball_speed)]

    bricks = create_bricks(rows, cols)
    powerups = []
    lives = 3
    paused = False   # pause 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused           # toggle pause

                if paused and event.key == pygame.K_m:
                    return "menu"

                if event.key == pygame.K_b and not paused:
                    new_balls = []
                    for b in balls:

                        nb = Ball(b.x, b.y, b.radius, b.color,
                                  -b.speed_x, b.speed_y)
                        new_balls.append(nb)
                    balls.extend(new_balls)


        keys = pygame.key.get_pressed()

        if not paused:
            paddle.move(keys)

            # update all balls
            for ball in balls:
                ball.move()
                ball.bounce_walls()
                ball.bounce_paddle(paddle)
                ball.collide_bricks(bricks, powerups)

            # Move powerups
            for p in powerups:
                p.move()

            # Check powerup collisions with paddle / off-screen
            for p in powerups[:]:
                if (paddle.y <= p.y + p.height // 2 <= paddle.y + paddle.height and
                    paddle.x <= p.x <= paddle.x + paddle.width):
                    lives = p.apply_effect(paddle, balls, lives)
                    powerups.remove(p)
                elif p.y - p.height // 2 > HEIGHT:
                    powerups.remove(p)

            # Lose condition: balls that fall below
            for ball in balls[:]:
                if ball.y - ball.radius > HEIGHT:
                    balls.remove(ball)

            if not balls:
                lives -= 1
                if lives <= 0:
                    return "lose"
                else:
                    # reset to a single ball at center
                    balls.append(Ball(WIDTH // 2, HEIGHT // 2, 10, RED, ball_speed, -ball_speed))

            # Win condition: all bricks gone
            if all(not b.visible for b in bricks):
                return "win"

        draw_gradient_background()
        for b in bricks:
            b.draw()
        for p in powerups:
            p.draw()
        paddle.draw()
        for ball in balls:
            ball.draw()

        # HUD
        lives_text = small_font.render(f"Lives: {lives}", True, WHITE)
        diff_text  = small_font.render(f"Difficulty: {difficulty.capitalize()}", True, WHITE)
        balls_text = small_font.render(f"Balls: {len(balls)}", True, WHITE)
        pause_hint = small_font.render("P: pause/resume", True, WHITE)

        screen.blit(lives_text, (10, 10))
        screen.blit(balls_text, (10, 35))
        screen.blit(pause_hint, (10, 60))
        screen.blit(diff_text,  (WIDTH - diff_text.get_width() - 10, 10))

        # If paused this draws overlay text
        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # semi-transparent dark layer
            screen.blit(overlay, (0, 0))

            pause_text = title_font.render("PAUSED", True, YELLOW)
            hint_text  = menu_font.render("Press P to resume", True, WHITE)
            menu_text  = menu_font.render("Press M for Main Menu", True, WHITE)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2,
                                     HEIGHT // 2 - 80))
            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2,
                                    HEIGHT // 2 + 10))
            screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2,
                                    HEIGHT // 2 + 60))

        pygame.display.flip()
        clock.tick(60)



# --------------------------------------------------Main loop

while True:
    difficulty = main_menu()
    while True:
        result = play_game(difficulty)          # win or lose
        action = end_screen(result, difficulty) # retry menu and quit

        if action == "retry":
            continue          # play again with same difficulty
        elif action == "menu":
            break             # go back to main menu
        elif action == "quit":
            pygame.quit()
            sys.exit()
