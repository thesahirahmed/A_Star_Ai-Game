import pygame
import random
import heapq

from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Initialize Pygame
pygame.init()

# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Create the screen object
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Define the Player object extending pygame.sprite.Sprite


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("jet.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# Define the Enemy object extending pygame.sprite.Sprite


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("missile.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5, 20)
        self.path = self.astar_pathfinding(player_rect)

    def update(self):
        if self.path:
            next_cell = self.path.pop(0)
            self.rect.topleft = next_cell[0] * 50, next_cell[1] * 50

            if not self.path:
                self.kill()

    def astar_pathfinding(self, player_rect):
        start_cell = (self.rect.x // 50, self.rect.y // 50)
        goal_cell = (player_rect.x // 50, player_rect.y // 50)

        open_set = [(0, start_cell)]
        heapq.heapify(open_set)
        came_from = {}
        g_score = {start_cell: 0}

        while open_set:
            current_g, current_cell = heapq.heappop(open_set)

            if current_cell == goal_cell:
                path = [current_cell]
                while current_cell in came_from:
                    current_cell = came_from[current_cell]
                    path.insert(0, current_cell)
                return path

            for neighbor in self.get_neighbors(current_cell):
                tentative_g = g_score[current_cell] + 1

                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current_cell
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal_cell)
                    heapq.heappush(open_set, (f_score, neighbor))

        return []

    def get_neighbors(self, cell):
        x, y = cell
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [(x, y) for x, y in neighbors if 0 <= x < SCREEN_WIDTH // 50 and 0 <= y < SCREEN_HEIGHT // 50]

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


# Setup for sounds, defaults are good
pygame.mixer.init()

# Create custom events for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)

# Create our 'player'
player = Player()

# Create groups to hold player sprite and enemy sprites
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

enemies = pygame.sprite.Group()

# Our main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False
        elif event.type == ADDENEMY:
            new_enemy = Enemy(player.rect)
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)

    enemies.update()

    screen.fill((135, 206, 250))

    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    if pygame.sprite.spritecollideany(player, enemies):
        player.kill()
        running = False

    pygame.display.flip()
    clock.tick(15)

pygame.mixer.quit()
pygame.quit()
