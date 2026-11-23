"""Изображения, тайловые ленты и отрисовка игрового поля."""

import math
import random

import pygame

import settings as s


def draw_wrapped(screen, image, pos):
    """Нарисовать объект и его видимые части за границами экрана."""
    for dx in (-s.WIDTH, 0, s.WIDTH):
        for dy in (-s.HEIGHT, 0, s.HEIGHT):
            rect = image.get_rect(center=(round(pos.x + dx),
                                          round(pos.y + dy)))
            if rect.colliderect(screen.get_rect()):
                screen.blit(image, rect)


class Graphics:
    """Создать изображения один раз и использовать их при отрисовке."""

    def __init__(self):
        """Подготовить изображения корабля, астероида, взрыва и фоны."""
        self.ship_sheet = self.make_ship_sheet()
        self.rock = self.make_rock()
        self.explosion_sheet = self.make_explosion_sheet()
        self.rocket = pygame.Surface((10, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(self.rocket, (255, 223, 125), (2, 0, 6, 18))
        self.background = pygame.Surface((s.WIDTH, s.HEIGHT))
        self.background.fill(s.BACKGROUND)
        rng = random.Random(7)
        for _ in range(s.STAR_COUNT):
            point = (rng.randrange(s.WIDTH), rng.randrange(s.HEIGHT))
            pygame.draw.circle(self.background, (112, 132, 160), point, 1)
        self.clouds = pygame.Surface((s.WIDTH, s.HEIGHT), pygame.SRCALPHA)
        for _ in range(14):
            point = (rng.randrange(s.WIDTH), rng.randrange(s.HEIGHT))
            self.clouds.blit(self.rock, self.rock.get_rect(center=point))
        self.clouds.set_alpha(s.BG_ALPHA)
        self.offset = 0
        self.font = pygame.font.Font(None, s.FONT_SIZE)
        self.title_font = pygame.font.Font(None, s.TITLE_SIZE)
        self.splash = pygame.Rect(0, 0, s.SPLASH_WIDTH, s.SPLASH_HEIGHT)
        self.splash.center = (s.WIDTH // 2, s.HEIGHT // 2)

    def make_ship_sheet(self):
        """Создать ленту из двух кадров: корабль без тяги и с двигателем."""
        size = s.SHIP_TILE
        sheet = pygame.Surface((size * 2, size), pygame.SRCALPHA)
        for frame in range(2):
            x = frame * size + size // 2
            y = size // 2
            if frame:
                pygame.draw.polygon(sheet, (255, 141, 49),
                                    [(x - 7, y + 13), (x, y + 30),
                                     (x + 7, y + 13)])
            pygame.draw.polygon(sheet, (193, 220, 242),
                                [(x, y - 24), (x - 18, y + 19),
                                 (x, y + 11), (x + 18, y + 19)])
            pygame.draw.polygon(sheet, (47, 113, 164),
                                [(x, y - 12), (x - 6, y + 5),
                                 (x + 6, y + 5)])
        return sheet

    def make_rock(self):
        """Создать изображение астероида с неровным контуром."""
        size = s.SHIP_TILE
        image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        rng = random.Random(3)
        points = []
        for index in range(12):
            angle = index * math.tau / 12
            radius = rng.uniform(s.ROCK_RADIUS - 5, s.ROCK_RADIUS + 2)
            points.append((center + math.cos(angle) * radius,
                           center + math.sin(angle) * radius))
        pygame.draw.polygon(image, (113, 111, 111), points)
        pygame.draw.polygon(image, (163, 155, 143), points, 2)
        pygame.draw.circle(image, (80, 81, 85), (24, 22), 6)
        pygame.draw.circle(image, (89, 88, 89), (42, 38), 8)
        return image

    def make_explosion_sheet(self):
        """Создать горизонтальную тайловую ленту из кадров взрыва."""
        size = s.EXPLOSION_TILE
        sheet = pygame.Surface((size * s.EXPLOSION_FRAMES, size),
                               pygame.SRCALPHA)
        for index in range(s.EXPLOSION_FRAMES):
            progress = index / (s.EXPLOSION_FRAMES - 1)
            center = (index * size + size // 2, size // 2)
            radius = max(1, int(4 + progress * (size // 2 - 6)))
            alpha = int(255 * (1 - progress))
            pygame.draw.circle(sheet, (255, 94, 28, alpha), center, radius)
            pygame.draw.circle(sheet, (255, 199, 66, alpha), center,
                               max(1, radius * 2 // 3))
            pygame.draw.circle(sheet, (255, 248, 190, alpha), center,
                               max(1, radius // 3))
        return sheet

    def draw_background(self, screen, dt):
        """Показать неподвижные звёзды и движущийся прозрачный слой."""
        screen.blit(self.background, (0, 0))
        self.offset = (self.offset + s.BG_SPEED * dt) % s.WIDTH
        screen.blit(self.clouds, (-int(self.offset), 0))
        screen.blit(self.clouds, (s.WIDTH - int(self.offset), 0))

    def draw_ship(self, screen, ship):
        """Выбрать кадр двигателя и повернуть изображение корабля."""
        size = s.SHIP_TILE
        tile = (int(ship.thrust) * size, 0, size, size)
        image = self.ship_sheet.subsurface(tile)
        image = pygame.transform.rotate(image, -ship.angle)
        draw_wrapped(screen, image, ship.pos)

    def draw_rock(self, screen, rock):
        """Нарисовать астероид под его текущим углом."""
        image = pygame.transform.rotate(self.rock, -rock.angle)
        draw_wrapped(screen, image, rock.pos)

    def draw_rocket(self, screen, rocket):
        """Нарисовать ракету по направлению её движения."""
        image = pygame.transform.rotate(self.rocket, -rocket.angle)
        draw_wrapped(screen, image, rocket.pos)

    def draw_explosion(self, screen, pos, age):
        """Выбрать кадр тайловой ленты по времени от начала взрыва."""
        index = int(age * s.EXPLOSION_FPS)
        if index < s.EXPLOSION_FRAMES:
            size = s.EXPLOSION_TILE
            image = self.explosion_sheet.subsurface(index * size, 0,
                                                    size, size)
            draw_wrapped(screen, image, pos)

    def draw_overlay(self, screen, lives, score, active):
        """Показать счёт, жизни и при необходимости заставку."""
        text = self.font.render(f'Lives: {lives}    Score: {score}',
                                True, s.TEXT_COLOR)
        screen.blit(text, (22, 18))
        if not active:
            pygame.draw.rect(screen, (25, 42, 64), self.splash,
                             border_radius=14)
            pygame.draw.rect(screen, (105, 161, 198), self.splash, 2,
                             border_radius=14)
            title = self.title_font.render('ASTEROIDS', True, s.TEXT_COLOR)
            hint = self.font.render('Click here to start',
                                    True, s.TEXT_COLOR)
            screen.blit(title, title.get_rect(
                center=(self.splash.centerx, self.splash.centery - 28)))
            screen.blit(hint, hint.get_rect(
                center=(self.splash.centerx, self.splash.centery + 35)))
