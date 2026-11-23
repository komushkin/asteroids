"""Движение и столкновения игровых объектов."""

import random

import pygame

import settings as s


def direction(angle):
    """Вернуть единичный вектор по направлению носа корабля."""
    return pygame.Vector2(0, -1).rotate(angle)


def distance(first, second):
    """Найти кратчайшее расстояние между точками на замкнутом поле."""
    # Учитываем соседний образ объекта за противоположным краем экрана.
    dx = abs(first.x - second.x) % s.WIDTH
    dy = abs(first.y - second.y) % s.HEIGHT
    return pygame.Vector2(min(dx, s.WIDTH - dx),
                          min(dy, s.HEIGHT - dy)).length()


class Body:
    """Хранить положение, скорость, угол и радиус объекта."""

    def __init__(self, pos, velocity, radius, angle=0, spin=0):
        """Задать начальные параметры объекта."""
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.radius = radius
        self.angle = angle
        self.spin = spin

    def move(self, dt):
        """Переместить объект с сохранением скорости при переходе края."""
        self.pos += self.velocity * dt
        self.pos.x %= s.WIDTH
        self.pos.y %= s.HEIGHT
        self.angle = (self.angle + self.spin * dt) % 360

    def touches(self, other):
        """Проверить пересечение кругов с учётом границ поля."""
        return distance(self.pos, other.pos) <= self.radius + other.radius


class Ship(Body):
    """Корабль с поворотом, тягой и сопротивлением среды."""

    def __init__(self):
        """Создать неподвижный корабль в центре поля."""
        super().__init__((s.WIDTH / 2, s.HEIGHT / 2), (0, 0),
                         s.SHIP_RADIUS)
        self.thrust = False

    def update(self, dt, left, right, thrust):
        """Обновить направление, тягу и положение корабля."""
        self.spin = (int(right) - int(left)) * s.SHIP_TURN
        self.angle = (self.angle + self.spin * dt) % 360
        self.thrust = thrust
        if thrust:
            self.velocity += direction(self.angle) * s.SHIP_THRUST * dt
            if self.velocity.length() > s.SHIP_MAX_SPEED:
                self.velocity.scale_to_length(s.SHIP_MAX_SPEED)
        else:
            # Степень dt делает торможение независимым от частоты кадров.
            self.velocity *= s.SHIP_DRAG ** dt
            if self.velocity.length() < s.SHIP_STOP:
                self.velocity.update(0, 0)
        self.pos += self.velocity * dt
        self.pos.x %= s.WIDTH
        self.pos.y %= s.HEIGHT


class Rocket(Body):
    """Ракета с постоянной скоростью и ограниченным временем жизни."""

    def __init__(self, ship):
        """Выпустить ракету из носа корабля."""
        forward = direction(ship.angle)
        pos = ship.pos + forward * (s.SHIP_RADIUS + s.SHOT_RADIUS)
        pos.x %= s.WIDTH
        pos.y %= s.HEIGHT
        super().__init__(pos, forward * s.SHOT_SPEED,
                         s.SHOT_RADIUS, ship.angle)
        self.life = s.SHOT_LIFE

    def update(self, dt):
        """Переместить ракету и уменьшить оставшееся время жизни."""
        self.move(dt)
        self.life -= dt


class Rock(Body):
    """Астероид со случайной линейной и угловой скоростью."""

    def __init__(self, pos):
        """Создать астероид в заданной точке."""
        velocity = direction(random.uniform(0, 360))
        velocity *= random.uniform(s.ROCK_MIN_SPEED, s.ROCK_MAX_SPEED)
        super().__init__(pos, velocity, s.ROCK_RADIUS,
                         random.uniform(0, 360),
                         random.uniform(-s.ROCK_TURN, s.ROCK_TURN))
