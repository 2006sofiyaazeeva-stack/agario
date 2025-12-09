import pygame
import random
import math
import json
import os

# --- Конфигурация ---
CONFIG = {
    "map_size":(1200, 800),
    "player": {"start_mass": 10, "color": (0, 128, 255)},
    "food": {"count": 100, "mass": 1, "color": (0, 255, 0)},
    "virus": {"count": 5, "mass": 50, "color": (128, 0, 128)},
    "colors": {"background": (240, 240, 240)},
}

# --- Базовый класс Blob ---
class Blob:
    def __init__(self, x, y, mass, color):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = max(5, int(math.sqrt(mass) * 2))
        self.color = color
        self.speed = 20 / self.radius  # Чем больше, тем медленнее

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        # Ограничение по границам экрана
        self.x = max(self.radius, min(CONFIG["map_size"][0] - self.radius, self.x))
        self.y = max(self.radius, min(CONFIG["map_size"][1] - self.radius, self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# --- Класс игрока ---
class Player(Blob):
    def __init__(self, x, y):
        super().__init__(x, y, CONFIG["player"]["start_mass"], CONFIG["player"]["color"])
        self.score = 0

    def eat(self, food):
        self.mass += food.mass
        self.radius = max(5, int(math.sqrt(self.mass) * 2))
        self.speed = 20 / self.radius
        self.score += 1

# --- Класс еды ---
class Food(Blob):
    def __init__(self, x, y):
        super().__init__(x, y, CONFIG["food"]["mass"], CONFIG["food"]["color"])

# --- Класс вируса ---
class Virus(Blob):
    def __init__(self, x, y):
        super().__init__(x, y, CONFIG["virus"]["mass"], CONFIG["virus"]["color"])

# --- Проверка столкновений ---
def check_collision(blob1, blob2):
    dx = blob1.x - blob2.x
    dy = blob1.y - blob2.y
    distance = math.sqrt(dx*dx + dy*dy)
    return distance < blob1.radius + blob2.radius

# --- Игровой движок ---
class Game:
    def __init__(self):
        self.player = Player(CONFIG["map_size"][0] // 2, CONFIG["map_size"][1] // 2)
        self.foods = [Food(random.randint(0, CONFIG["map_size"][0]),
                           random.randint(0, CONFIG["map_size"][1]))
                      for _ in range(CONFIG["food"]["count"])]
        self.viruses = [Virus(random.randint(0, CONFIG["map_size"][0]),
                             random.randint(0, CONFIG["map_size"][1]))
                       for _ in range(CONFIG["virus"]["count"])]

    def update(self):
        # Поедание еды
        for food in self.foods[:]:
            if check_collision(self.player, food):
                self.player.eat(food)
                self.foods.remove(food)
                self.foods.append(Food(random.randint(0, CONFIG["map_size"][0]),
                                      random.randint(0, CONFIG["map_size"][1])))
        # Столкновение с вирусами
        for virus in self.viruses:
            if check_collision(self.player, virus) and self.player.mass < virus.mass * 1.25:
                self.player.mass = max(1, self.player.mass // 2)
                self.player.radius = max(5, int(math.sqrt(self.player.mass) * 2))
                self.player.speed = 20 / self.player.radius

    def draw(self, surface):
        surface.fill(CONFIG["colors"]["background"])
        self.player.draw(surface)
        for food in self.foods:
            food.draw(surface)
        for virus in self.viruses:
            virus.draw(surface)
        # HUD: отображение счёта
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.player.score}", True, (0, 0, 0))
        surface.blit(score_text, (10, 10))

# --- Основная функция ---
def main():
    pygame.init()
    screen = pygame.display.set_mode(CONFIG["map_size"])
    pygame.display.set_caption("Agar.io Clone")
    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Управление
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        game.player.move(dx, dy)
        game.update()
        game.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
