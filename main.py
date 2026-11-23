"""Запуск игры «Астероиды» и обработка игровых событий."""

import random

import pygame

import settings as s
from graphics import Graphics
from sprites import Rock, Rocket, Ship, distance


class Game:
    """Управлять окном, объектами, столкновениями и состоянием партии."""

    def __init__(self):
        """Открыть окно и показать заставку с начальными счётчиками."""
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((s.WIDTH, s.HEIGHT))
        pygame.display.set_caption('Астероиды')
        self.clock = pygame.time.Clock()
        self.graphics = Graphics()
        self.running = True
        self.active = False
        self.lives = s.START_LIVES
        self.score = 0
        self.ship = None
        self.rocks = []
        self.rockets = []
        self.explosions = []
        self.spawn_timer = 0
        self.shot_timer = 0

    def start(self):
        """Начать новую партию с пустым полем и кораблём в центре."""
        self.active = True
        self.lives = s.START_LIVES
        self.score = 0
        self.ship = Ship()
        self.rocks.clear()
        self.rockets.clear()
        self.explosions.clear()
        self.spawn_timer = s.ROCK_DELAY
        self.shot_timer = 0

    def handle_event(self, event):
        """Обработать закрытие окна и щелчок внутри заставки."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.active:
                if self.graphics.splash.collidepoint(event.pos):
                    self.start()

    def spawn_rock(self):
        """Выбрать случайную точку появления на расстоянии от корабля."""
        for _ in range(30):
            pos = pygame.Vector2(random.uniform(0, s.WIDTH),
                                 random.uniform(0, s.HEIGHT))
            if distance(pos, self.ship.pos) >= s.SPAWN_DISTANCE:
                self.rocks.append(Rock(pos))
                return

    def shoot(self):
        """Выпустить ракету, если закончилась пауза между выстрелами."""
        if self.shot_timer <= 0:
            self.rockets.append(Rocket(self.ship))
            self.shot_timer = s.SHOT_DELAY

    def hit_ship(self, rock):
        """Убрать астероид и отнять жизнь либо завершить игру."""
        self.rocks.remove(rock)
        self.explosions.append([rock.pos.copy(), 0.0])
        # Проверяем жизни до уменьшения: это прямо указано в задании.
        if self.lives == 0:
            self.active = False
            self.ship = None
            self.rocks.clear()
            self.rockets.clear()
            self.explosions.clear()
        else:
            self.lives -= 1
            self.ship = Ship()

    def check_collisions(self):
        """Проверить ракеты и корабль; астероиды друг друга не касаются."""
        for rocket in self.rockets[:]:
            for rock in self.rocks[:]:
                if rocket.touches(rock):
                    self.rockets.remove(rocket)
                    self.rocks.remove(rock)
                    self.explosions.append([rock.pos.copy(), 0.0])
                    self.score += 1
                    break
        for rock in self.rocks[:]:
            if self.ship.touches(rock):
                self.hit_ship(rock)
                break

    def update(self, dt, keys):
        """Обновить физику, время жизни объектов и столкновения."""
        if not self.active:
            return
        self.ship.update(dt, keys[pygame.K_LEFT], keys[pygame.K_RIGHT],
                         keys[pygame.K_UP])
        self.shot_timer -= dt
        if keys[pygame.K_SPACE]:
            self.shoot()
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            if len(self.rocks) < s.ROCK_LIMIT:
                self.spawn_rock()
            self.spawn_timer += s.ROCK_DELAY
        for rock in self.rocks:
            rock.move(dt)
        for rocket in self.rockets:
            rocket.update(dt)
        self.rockets = [rocket for rocket in self.rockets if rocket.life > 0]
        for explosion in self.explosions:
            explosion[1] += dt
        duration = s.EXPLOSION_FRAMES / s.EXPLOSION_FPS
        self.explosions = [item for item in self.explosions
                           if item[1] < duration]
        self.check_collisions()

    def draw(self, dt):
        """Нарисовать фон, игровые объекты, счётчики и заставку."""
        self.graphics.draw_background(self.screen, dt)
        if self.active:
            for rock in self.rocks:
                self.graphics.draw_rock(self.screen, rock)
            for rocket in self.rockets:
                self.graphics.draw_rocket(self.screen, rocket)
            self.graphics.draw_ship(self.screen, self.ship)
            for pos, age in self.explosions:
                self.graphics.draw_explosion(self.screen, pos, age)
        self.graphics.draw_overlay(self.screen, self.lives,
                                   self.score, self.active)
        pygame.display.flip()

    def run(self):
        """Выполнять цикл игры до закрытия окна."""
        try:
            while self.running:
                dt = min(self.clock.tick(s.FPS) / 1000, s.MAX_DT)
                for event in pygame.event.get():
                    self.handle_event(event)
                if self.running:
                    self.update(dt, pygame.key.get_pressed())
                    self.draw(dt)
        finally:
            pygame.quit()


if __name__ == '__main__':
    Game().run()
