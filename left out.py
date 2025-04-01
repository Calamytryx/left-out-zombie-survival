import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Left Out: Zombie Survival")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_RED = (139, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)

# FPS (frames per second)
FPS = 30
clock = pygame.time.Clock()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.health = 100

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

# Zombie class
class Zombie(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(0, HEIGHT)
        self.speed = random.randint(2, 5)

    def update(self):
        # Simple AI for zombies: Move towards the player
        player_x, player_y = player.rect.center
        if self.rect.x < player_x:
            self.rect.x += self.speed
        if self.rect.x > player_x:
            self.rect.x -= self.speed
        if self.rect.y < player_y:
            self.rect.y += self.speed
        if self.rect.y > player_y:
            self.rect.y -= self.speed

# Game Functions
def draw_health_bar(health):
    pygame.draw.rect(screen, DARK_RED, (10, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, health * 2, 20))

def show_text(text, x, y, color):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def game_over():
    show_text("Game Over", WIDTH // 2 - 100, HEIGHT // 2 - 50, RED)
    show_text("Press SPACE to Retry", WIDTH // 2 - 130, HEIGHT // 2, WHITE)

def home_screen():
    show_text("Left Out: Zombie Survival", WIDTH // 2 - 160, HEIGHT // 2 - 50, WHITE)
    show_text("Press SPACE to Start", WIDTH // 2 - 130, HEIGHT // 2, WHITE)
    show_text("Press ESC to Quit", WIDTH // 2 - 115, HEIGHT // 2 + 50, WHITE)

# Main game loop
def main_game():
    global player, zombies, all_sprites
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    zombies = pygame.sprite.Group()

    # Spawn zombies in waves
    wave_count = 1
    zombie_spawn_rate = 5

    for _ in range(zombie_spawn_rate * wave_count):  # Spawn zombies
        zombie = Zombie()
        all_sprites.add(zombie)
        zombies.add(zombie)

    # Game variables
    score = 0
    running = True
    while running:
        screen.fill(BLACK)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update player and zombies
        keys = pygame.key.get_pressed()
        player.update(keys)
        zombies.update()

        # Check for collisions with zombies
        if pygame.sprite.spritecollide(player, zombies, False):
            player.take_damage(1)
            if player.health <= 0:
                game_over()

        # Draw the environment
        all_sprites.draw(screen)
        draw_health_bar(player.health)

        # Show score
        show_text(f"Score: {score}", 10, 50, WHITE)

        # Spawn next wave after some time
        if len(zombies) == 0:
            wave_count += 1
            for _ in range(zombie_spawn_rate * wave_count):  # Spawn more zombies in the next wave
                zombie = Zombie()
                all_sprites.add(zombie)
                zombies.add(zombie)

        # Update display
        pygame.display.flip()

        # Frame rate
        clock.tick(FPS)

# Home screen loop
def game_loop():
    running = True
    on_home_screen = True
    while running:
        screen.fill(BLACK)

        if on_home_screen:
            home_screen()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        on_home_screen = False  # Start the game
                    if event.key == pygame.K_ESCAPE:
                        running = False  # Quit the game

        else:
            main_game()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        main_game()  # Restart the game
                    if event.key == pygame.K_ESCAPE:
                        running = False  # Quit the game

        pygame.display.flip()
        clock.tick(FPS)

# Start the game loop
game_loop()

# Quit the game
pygame.quit()
