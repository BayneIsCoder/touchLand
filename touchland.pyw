import pygame
import numpy as np
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
GREEN = (50, 255, 50)
RED = (255, 50, 50)
GRAY = (128, 128, 128)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = 22
        self.on_ground = False
        self.gravity = 0.8
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
    def update(self, platforms):
        # Handle input
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False
            
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 15:  # Terminal velocity
            self.vel_y = 15
            
        # Move horizontally
        self.x += self.vel_x
        self.rect.x = self.x
        
        # Check horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_x > 0:  # Moving right
                    self.rect.right = platform.left
                    self.x = self.rect.x
                elif self.vel_x < 0:  # Moving left
                    self.rect.left = platform.right
                    self.x = self.rect.x
                    
        # Move vertically
        self.y += self.vel_y
        self.rect.y = self.y
        
        # Check vertical collisions
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.top
                    self.y = self.rect.y
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping
                    self.rect.top = platform.bottom
                    self.y = self.rect.y
                    self.vel_y = 0
                    
        # Keep player on screen
        if self.x < 0:
            self.x = 0
            self.rect.x = self.x
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.rect.x = self.x
            
        # Check if player fell off screen
        if self.y > SCREEN_HEIGHT:
            return "death"
        
        return "alive"
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)
        # Draw simple face
        pygame.draw.circle(screen, WHITE, (self.rect.centerx - 5, self.rect.centery - 5), 3)
        pygame.draw.circle(screen, WHITE, (self.rect.centerx + 5, self.rect.centery - 5), 3)

class Robot:
    def __init__(self, x, y, patrol_range=100):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 35
        self.speed = 2
        self.direction = 1
        self.patrol_start = x
        self.patrol_range = patrol_range
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
    def update(self, platforms):
        # Patrol movement
        self.x += self.speed * self.direction
        
        # Turn around at patrol boundaries
        if self.x <= self.patrol_start or self.x >= self.patrol_start + self.patrol_range:
            self.direction *= -1
            
        self.rect.x = self.x
        
        # Simple gravity
        self.y += 3
        self.rect.y = self.y
        
        # Check platform collisions
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.rect.bottom > platform.top:
                    self.rect.bottom = platform.top
                    self.y = self.rect.y
                    break
    
    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)
        # Draw robot features
        pygame.draw.circle(screen, YELLOW, (self.rect.centerx - 4, self.rect.centery - 5), 2)
        pygame.draw.circle(screen, YELLOW, (self.rect.centerx + 4, self.rect.centery - 5), 2)
        pygame.draw.rect(screen, WHITE, (self.rect.centerx - 3, self.rect.centery + 3, 6, 2))

class Portal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.animation = 0
        
    def update(self):
        self.animation += 0.2
        
    def draw(self, screen):
        # Animated portal effect
        colors = [PURPLE, CYAN, PURPLE]
        for i in range(3):
            offset = math.sin(self.animation + i) * 5
            pygame.draw.ellipse(screen, colors[i], 
                              (self.x + offset, self.y + offset, 
                               self.width - offset*2, self.height - offset*2))

class LevelGenerator:
    @staticmethod
    def generate_level(level_num):
        platforms = []
        robots = []
        
        # Ground platforms
        for i in range(0, SCREEN_WIDTH, 200):
            platforms.append(pygame.Rect(i, SCREEN_HEIGHT - 40, 200, 40))
        
        # Create perfect step-by-step platforms
        # Each level has a predetermined, perfect layout
        
        # Level-specific layouts
        if level_num == 1:
            # Simple staircase - very easy
            platforms.extend([
                pygame.Rect(150, SCREEN_HEIGHT - 140, 150, 20),   # First step
                pygame.Rect(350, SCREEN_HEIGHT - 240, 150, 20),   # Second step
                pygame.Rect(550, SCREEN_HEIGHT - 340, 150, 20),   # Third step
                pygame.Rect(400, SCREEN_HEIGHT - 440, 200, 20),   # Portal platform
            ])
        elif level_num == 2:
            # Slightly more complex
            platforms.extend([
                pygame.Rect(100, SCREEN_HEIGHT - 120, 120, 20),
                pygame.Rect(300, SCREEN_HEIGHT - 200, 120, 20),
                pygame.Rect(500, SCREEN_HEIGHT - 280, 120, 20),
                pygame.Rect(700, SCREEN_HEIGHT - 360, 120, 20),
                pygame.Rect(450, SCREEN_HEIGHT - 450, 180, 20),
            ])
            # Add one robot
            robots.append(Robot(480, SCREEN_HEIGHT - 485, 100))
        elif level_num == 3:
            # Zigzag pattern
            platforms.extend([
                pygame.Rect(80, SCREEN_HEIGHT - 140, 140, 20),
                pygame.Rect(280, SCREEN_HEIGHT - 220, 140, 20),
                pygame.Rect(480, SCREEN_HEIGHT - 160, 140, 20),
                pygame.Rect(680, SCREEN_HEIGHT - 240, 140, 20),
                pygame.Rect(480, SCREEN_HEIGHT - 320, 140, 20),
                pygame.Rect(280, SCREEN_HEIGHT - 400, 140, 20),
                pygame.Rect(420, SCREEN_HEIGHT - 480, 160, 20),
            ])
            robots.extend([
                Robot(310, SCREEN_HEIGHT - 255, 80),
                Robot(710, SCREEN_HEIGHT - 275, 80),
            ])
        else:
            # For levels 4+, create procedural but perfect layouts
            base_height = SCREEN_HEIGHT - 120
            step_height = 80  # Perfect jump distance
            platform_width = 150
            
            # Create a perfect staircase with some variation
            num_steps = 5 + (level_num // 3)  # More steps for higher levels
            
            for i in range(num_steps):
                # Alternate sides for interesting patterns
                if i % 2 == 0:
                    x = 100 + (i % 3) * 200
                else:
                    x = SCREEN_WIDTH - 250 - (i % 3) * 200
                    
                y = base_height - (i + 1) * step_height
                
                # Make sure platforms don't go too high
                if y < 100:
                    y = 100 + (i * 20)
                    
                platforms.append(pygame.Rect(x, y, platform_width, 20))
                
                # Add robots on higher levels - more starting at level 5
                if level_num >= 5:
                    if i > 0 and (i + level_num) % 2 == 0:  # More frequent robots
                        robot_x = x + 20
                        robots.append(Robot(robot_x, y - 35, platform_width - 40))
                        
                    # Add extra robots on even higher levels
                    if level_num >= 10 and i > 1 and (i + level_num) % 3 == 1:
                        robot_x = x + platform_width - 60
                        robots.append(Robot(robot_x, y - 35, platform_width - 60))
                        
                    # Even more robots on very high levels
                    if level_num >= 20 and i > 2 and (i % 4) == 0:
                        robot_x = x + platform_width // 2
                        robots.append(Robot(robot_x, y - 35, platform_width - 80))
        
        # Portal at the highest platform
        if platforms:
            portal_platform = min(platforms, key=lambda p: p.y)
            portal = Portal(portal_platform.x + portal_platform.width // 2 - 20, 
                           portal_platform.y - 60)
        else:
            portal = Portal(SCREEN_WIDTH // 2 - 20, 50)
        
        return platforms, robots, portal

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TouchLand - Robot Invasion")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.level = 1
        self.lives = 3
        self.score = 0
        self.game_state = "menu"  # menu, playing, game_over, victory
        
        self.reset_level()
        
    def reset_level(self):
        self.player = Player(50, SCREEN_HEIGHT - 100)
        self.platforms, self.robots, self.portal = LevelGenerator.generate_level(self.level)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_SPACE:
                        self.game_state = "playing"
                elif self.game_state == "game_over":
                    if event.key == pygame.K_r:
                        self.level = 1
                        self.lives = 3
                        self.score = 0
                        self.reset_level()
                        self.game_state = "playing"
                elif self.game_state == "victory":
                    if event.key == pygame.K_SPACE:
                        self.level += 1
                        self.score += 100
                        self.reset_level()
                        self.game_state = "playing"
        return True
        
    def update(self):
        if self.game_state == "playing":
            # Update player
            status = self.player.update(self.platforms)
            
            if status == "death":
                self.lives -= 1
                if self.lives <= 0:
                    self.game_state = "game_over"
                else:
                    self.reset_level()
                    
            # Update robots
            for robot in self.robots:
                robot.update(self.platforms)
                
                # Check collision with player
                if self.player.rect.colliderect(robot.rect):
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_state = "game_over"
                    else:
                        self.reset_level()
                        
            # Update portal
            self.portal.update()
            
            # Check portal collision
            if self.player.rect.colliderect(self.portal.rect):
                if self.level >= 100:
                    self.game_state = "final_victory"
                else:
                    self.game_state = "victory"
    
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title = self.font.render("TOUCHLAND", True, CYAN)
        subtitle = self.small_font.render("The robots have taken over TouchLand!", True, WHITE)
        instruction1 = self.small_font.render("Help our hero reach the portals to save the land!", True, WHITE)
        instruction2 = self.small_font.render("Use ARROW KEYS or WASD to move, SPACE to jump", True, WHITE)
        start = self.font.render("Press SPACE to start", True, GREEN)
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 250))
        self.screen.blit(instruction1, (SCREEN_WIDTH//2 - instruction1.get_width()//2, 300))
        self.screen.blit(instruction2, (SCREEN_WIDTH//2 - instruction2.get_width()//2, 330))
        self.screen.blit(start, (SCREEN_WIDTH//2 - start.get_width()//2, 450))
        
    def draw_hud(self):
        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
        lives_text = self.small_font.render(f"Lives: {self.lives}", True, WHITE)
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        
        self.screen.blit(level_text, (10, 10))
        self.screen.blit(lives_text, (10, 35))
        self.screen.blit(score_text, (10, 60))
        
    def draw_game_over(self):
        self.screen.fill(BLACK)
        
        game_over = self.font.render("GAME OVER", True, RED)
        score = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
        level_reached = self.small_font.render(f"Levels Completed: {self.level - 1}", True, WHITE)
        restart = self.small_font.render("Press R to restart", True, GREEN)
        
        self.screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 250))
        self.screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, 320))
        self.screen.blit(level_reached, (SCREEN_WIDTH//2 - level_reached.get_width()//2, 350))
        self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 420))
        
    def draw_victory(self):
        self.screen.fill(BLACK)
        
        victory = self.font.render("LEVEL COMPLETE!", True, GREEN)
        next_level = self.small_font.render(f"Next: Level {self.level + 1}", True, WHITE)
        continue_text = self.small_font.render("Press SPACE to continue", True, CYAN)
        
        self.screen.blit(victory, (SCREEN_WIDTH//2 - victory.get_width()//2, 280))
        self.screen.blit(next_level, (SCREEN_WIDTH//2 - next_level.get_width()//2, 330))
        self.screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, 380))
        
    def draw_final_victory(self):
        self.screen.fill(BLACK)
        
        victory = self.font.render("TOUCHLAND SAVED!", True, GOLD)
        subtitle = self.small_font.render("You've completed all 100 levels!", True, WHITE)
        hero = self.small_font.render("The robots have been defeated!", True, GREEN)
        score = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
        
        self.screen.blit(victory, (SCREEN_WIDTH//2 - victory.get_width()//2, 200))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 280))
        self.screen.blit(hero, (SCREEN_WIDTH//2 - hero.get_width()//2, 320))
        self.screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, 370))
        
    def draw(self):
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "playing":
            self.screen.fill(BLACK)
            
            # Draw platforms
            for platform in self.platforms:
                pygame.draw.rect(self.screen, GRAY, platform)
                
            # Draw robots
            for robot in self.robots:
                robot.draw(self.screen)
                
            # Draw portal
            self.portal.draw(self.screen)
            
            # Draw player
            self.player.draw(self.screen)
            
            # Draw HUD
            self.draw_hud()
            
        elif self.game_state == "game_over":
            self.draw_game_over()
        elif self.game_state == "victory":
            self.draw_victory()
        elif self.game_state == "final_victory":
            self.draw_final_victory()
            
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()