# Left Out: Last Stand - Zombie Survival Game

# Import standard modules.
import sys
import random
import math
 
# Import non-standard modules.
import pygame
from pygame.locals import *

# Game constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 32
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
CRASHED = 4  # New state to handle crashes

# Entity types
PLAYER = 0
ZOMBIE = 1
SURVIVOR = 2
BUILDING = 3
RESOURCE = 4

class GameState:
    def __init__(self):
        self.state = MENU
        self.player = None
        self.zombies = []
        self.survivors = []
        self.buildings = []
        self.resources = []
        self.day = 1
        self.time = 0  # 0-1439 minutes (24 hours)
        self.food = 100
        self.materials = 100
        self.ammunition = 50
        self.medicine = 20
        self.error_message = ""  # Store error messages
        
    def is_night(self):
        # Night time is between 8pm (1200) and 6am (360)
        return self.time > 1200 or self.time < 360
        
    def update_time(self, dt):
        # Advance time (1 real second = 1 game minute)
        self.time += dt
        if self.time >= 1440:  # New day
            self.time = 0
            self.day += 1
            # Trigger daily events here

class Entity:
    def __init__(self, x, y, entity_type, health=100):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.entity_type = entity_type
        self.health = health
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        
    def update(self, dt, game_state):
        self.x += self.vx * dt
        self.y += self.vy * dt
        
    def draw(self, screen):
        color = WHITE
        if self.entity_type == PLAYER:
            color = BLUE
        elif self.entity_type == ZOMBIE:
            color = RED
        elif self.entity_type == SURVIVOR:
            color = GREEN
            
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER, 100)
        self.speed = 150
        
    def update(self, dt, game_state):
        # Handle player movement with WASD
        keys = pygame.key.get_pressed()
        self.vx = 0
        self.vy = 0
        
        if keys[K_w]:
            self.vy = -self.speed
        if keys[K_s]:
            self.vy = self.speed
        if keys[K_a]:
            self.vx = -self.speed
        if keys[K_d]:
            self.vx = self.speed
            
        # Normalize diagonal movement
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071
            
        super().update(dt, game_state)
        
        # Keep player on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

class Zombie(Entity):
    def __init__(self, x, y, zombie_type=0):
        super().__init__(x, y, ZOMBIE, 50)
        self.zombie_type = zombie_type
        self.speed = 50 + (25 * zombie_type)  # Faster zombies for higher types
        
    def update(self, dt, game_state):
        # Simple AI - chase player
        if game_state.player:
            dx = game_state.player.x - self.x
            dy = game_state.player.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                self.vx = (dx / dist) * self.speed
                self.vy = (dy / dist) * self.speed
            else:
                self.vx = 0
                self.vy = 0
                
        super().update(dt, game_state)

# Create game state
game_state = GameState()

def initialize_game():
    """Initialize or reset the game to starting state"""
    global game_state
    game_state = GameState()
    game_state.state = PLAYING
    game_state.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    try:
        spawn_zombies(5, game_state)
    except Exception as e:
        print(f"Error spawning zombies: {e}")

def spawn_zombies(count, game_state):
    for _ in range(count):
        # Spawn zombies at screen edges
        side = random.randint(0, 3)
        if side == 0:  # Top
            x = random.randint(0, SCREEN_WIDTH)
            y = -TILE_SIZE
        elif side == 1:  # Right
            x = SCREEN_WIDTH + TILE_SIZE
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Bottom
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + TILE_SIZE
        else:  # Left
            x = -TILE_SIZE
            y = random.randint(0, SCREEN_HEIGHT)
            
        zombie_type = random.choices([0, 1, 2], weights=[0.7, 0.2, 0.1])[0]
        game_state.zombies.append(Zombie(x, y, zombie_type))

def update(dt):
    """
    Update game. Called once per frame.
    dt is the amount of time passed since last frame in milliseconds.
    """
    global game_state
    
    try:
        # Go through events that are passed to the script by the window.
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if game_state.state == PLAYING:
                        game_state.state = PAUSED
                    elif game_state.state == PAUSED:
                        game_state.state = PLAYING
                elif event.key == K_RETURN:
                    if game_state.state == MENU or game_state.state == GAME_OVER or game_state.state == CRASHED:
                        try:
                            initialize_game()
                        except Exception as e:
                            game_state.error_message = f"Error initializing game: {str(e)}"
                            game_state.state = CRASHED
                            print(game_state.error_message)
        
        # Convert dt from milliseconds to seconds
        dt_seconds = dt / 1000.0
        
        if game_state.state == PLAYING:
            # Update game state time
            game_state.update_time(dt_seconds * 60)  # 1 real second = 60 game minutes
            
            # Update player
            if game_state.player:
                game_state.player.update(dt_seconds, game_state)
                
            # Update zombies
            for zombie in game_state.zombies:
                zombie.update(dt_seconds, game_state)
                
            # Check collisions
            for zombie in game_state.zombies[:]:
                if (abs(zombie.x - game_state.player.x) < TILE_SIZE and 
                    abs(zombie.y - game_state.player.y) < TILE_SIZE):
                    game_state.player.health -= 5 * dt_seconds
                    if game_state.player.health <= 0:
                        game_state.state = GAME_OVER
                    
            # Spawn new zombies every few seconds
            if random.random() < 0.01:  # 1% chance per frame
                spawn_count = 1
                if game_state.is_night():
                    spawn_count = 3  # More zombies at night
                try:
                    spawn_zombies(spawn_count, game_state)
                except Exception as e:
                    game_state.error_message = f"Error spawning zombies: {str(e)}"
                    game_state.state = CRASHED
                    print(game_state.error_message)
    
    except Exception as e:
        # Capture any other exceptions that might occur
        game_state.error_message = f"Unhandled exception: {str(e)}"
        game_state.state = CRASHED
        print(game_state.error_message)
        # Print full traceback to console
        import traceback
        traceback.print_exc()
 
def draw(screen):
    """
    Draw things to the window. Called once per frame.
    """
    global game_state
    
    try:
        # Fill the screen with black
        screen.fill(BLACK)
        
        if game_state.state == MENU:
            # Draw menu
            font = pygame.font.SysFont(None, 64)
            title = font.render("LEFT OUT: LAST STAND", True, WHITE)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//4))
            
            font = pygame.font.SysFont(None, 36)
            instruction = font.render("Press ENTER to start game", True, WHITE)
            screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT//2))
            
        elif game_state.state == PLAYING or game_state.state == PAUSED:
            # Draw game world
            
            # Draw player
            if game_state.player:
                game_state.player.draw(screen)
                
            # Draw zombies
            for zombie in game_state.zombies:
                zombie.draw(screen)
                
            # Draw HUD
            font = pygame.font.SysFont(None, 24)
            
            # Day/night indicator
            time_str = f"Day {game_state.day} - "
            hour = int(game_state.time // 60)  # Convert to integer
            minute = int(game_state.time % 60)  # Convert to integer
            time_str += f"{hour:02d}:{minute:02d}"
            time_text = font.render(time_str, True, WHITE)
            screen.blit(time_text, (10, 10))
            
            # Health
            health_text = font.render(f"Health: {int(game_state.player.health)}", True, WHITE)
            screen.blit(health_text, (10, 40))
            
            # Resources
            resource_text = font.render(f"Food: {game_state.food} | Materials: {game_state.materials} | Ammo: {game_state.ammunition}", True, WHITE)
            screen.blit(resource_text, (10, 70))
            
            if game_state.state == PAUSED:
                # Draw pause screen overlay
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                s.fill((0, 0, 0, 128))
                screen.blit(s, (0, 0))
                
                font = pygame.font.SysFont(None, 64)
                pause_text = font.render("PAUSED", True, WHITE)
                screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - pause_text.get_height()//2))
                
        elif game_state.state == GAME_OVER:
            font = pygame.font.SysFont(None, 64)
            gameover_text = font.render("GAME OVER", True, RED)
            screen.blit(gameover_text, (SCREEN_WIDTH//2 - gameover_text.get_width()//2, SCREEN_HEIGHT//2 - gameover_text.get_height()//2))
            
            font = pygame.font.SysFont(None, 36)
            instruction = font.render("Press ENTER to restart", True, WHITE)
            screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        elif game_state.state == CRASHED:
            # Display crash information
            screen.fill((50, 0, 0))  # Dark red background
            
            font = pygame.font.SysFont(None, 48)
            error_title = font.render("GAME CRASHED", True, WHITE)
            screen.blit(error_title, (SCREEN_WIDTH//2 - error_title.get_width()//2, SCREEN_HEIGHT//4))
            
            # Display error message
            font = pygame.font.SysFont(None, 24)
            lines = []
            message = game_state.error_message
            # Split long error messages into multiple lines
            while len(message) > 60:
                lines.append(message[:60])
                message = message[60:]
            lines.append(message)
            
            y_pos = SCREEN_HEIGHT//2 - (len(lines) * 30) // 2
            for line in lines:
                error_text = font.render(line, True, WHITE)
                screen.blit(error_text, (SCREEN_WIDTH//2 - error_text.get_width()//2, y_pos))
                y_pos += 30
            
            # Instructions
            font = pygame.font.SysFont(None, 36)
            instruction = font.render("Press ENTER to restart game", True, WHITE)
            screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT - 100))
            
            instruction2 = font.render("Check console for full error details", True, WHITE)
            screen.blit(instruction2, (SCREEN_WIDTH//2 - instruction2.get_width()//2, SCREEN_HEIGHT - 60))
      
        # Flip the display so that the things we drew actually show up.
        pygame.display.flip()
        
    except Exception as e:
        # Last resort error handling for drawing errors
        print(f"Error in draw function: {str(e)}")
        import traceback
        traceback.print_exc()
 
def runPyGame():
    # Initialise PyGame.
    pygame.init()
    
    # Set up the clock. This will tick every frame and thus maintain a relatively constant framerate. Hopefully.
    fps = FPS
    fpsClock = pygame.time.Clock()
    
    # Set up the window.
    pygame.display.set_caption("Left Out: Last Stand")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Main game loop.
    while True: # Loop forever!
        try:
            dt = fpsClock.tick(fps)
            update(dt)
            draw(screen)
        except Exception as e:
            # Global error handling as a last resort
            print(f"Critical error in main game loop: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Try to show the error on screen
            try:
                game_state.error_message = f"Critical error: {str(e)}"
                game_state.state = CRASHED
                screen.fill((50, 0, 0))
                font = pygame.font.SysFont(None, 36)
                error_text = font.render("CRITICAL ERROR - See Console", True, WHITE)
                screen.blit(error_text, (SCREEN_WIDTH//2 - error_text.get_width()//2, SCREEN_HEIGHT//2))
                pygame.display.flip()
                # Wait a bit to let user see the message
                pygame.time.wait(100)
            except:
                # If even that fails, at least we tried
                pass

runPyGame()