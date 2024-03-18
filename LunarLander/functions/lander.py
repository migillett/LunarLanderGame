import pygame
import math
from os import path

from functions.data_structures import *


class PlayerLander(pygame.sprite.Sprite):
    gravity: float
    x_pos: float
    y_pos: float
    angle: float
    thruster_strength: float
    max_velocity: float
    delay_interval: float
    window_dimensions: tuple[int, int]

    fuel_remaining: float = 100.0
    max_fuel: float = 100.0
    x_vel: float = 0.0
    y_vel: float = 0.0
    rotation_velocity: float = 0.0
    mass: float = 10.0
    lives: int = 3
    landed: bool = False
    crashed: bool = False
    heat: float = 0.0
    max_heat: float = 100.0

    def __init__(
            self, x_pos: int, y_pos: int, angle: float,
            angular_velocity: float,
            strength: float, heat_coefficient: float,
            max_velocity: float, abs_path: str,
            window_dimensions: tuple[int, int],
            gravity: float) -> None:
        super().__init__()

        self.gravity = gravity  # lunar gravity is 0.0253 m/s^2. Divide that by the FPS
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.angle = angle - 90.0
        self.rotation_velocity = angular_velocity
        self.thruster_strength = strength
        self.max_velocity = max_velocity
        self.window_dimensions = window_dimensions

        self.thruster_state: bool = False

        self.sprite_default: pygame.image = self.load_sprite(
            path.join(abs_path, 'assets', 'lander', 'lander_default.png'),
            50)
        self.sprite_thruster: pygame.image = self.load_sprite(
            path.join(abs_path, 'assets', 'lander', 'lander_thruster.png'),
            50)

        self.heat_coefficient = heat_coefficient

    def load_sprite(self, image_path: str, max_height: int) -> pygame.image:
        sprite = pygame.image.load(image_path)

        sprite_width, sprite_height = sprite.get_size()
        scale_factor = max_height / sprite_height
        sprite = pygame.transform.scale(
            sprite, (int(sprite_width * scale_factor), int(sprite_height * scale_factor)))

        sprite = pygame.transform.rotate(sprite, 90.0)
        return sprite

    def fire_rcs(self, rcs_force: float) -> None:
        if self.fuel_remaining > 0 and self.heat < self.max_heat:
            self.fuel_remaining -= self.thruster_strength
            self.rotation_velocity += rcs_force
            self.heat += self.heat_coefficient

    def fire_thruster(self) -> None:
        if self.fuel_remaining > 0 and self.heat < self.max_heat:
            self.fuel_remaining -= self.thruster_strength
            angle_radians = math.radians(self.angle)
            force_x = self.thruster_strength * math.cos(angle_radians)
            force_y = self.thruster_strength * math.sin(angle_radians)
            self.x_vel -= force_x / self.mass
            self.y_vel += force_y / self.mass
            self.heat += self.heat_coefficient

    def attempt_landing(self) -> None:
        self.landed = True
        self.rotation_velocity = 0
        # must not be more than 10 degrees off true vertical (which is 270, idk why)
        valid_landing_angle = self.angle > 260 and self.angle < 280
        self.crashed = self.max_velocity <= (
            self.y_vel + self.x_vel) or not valid_landing_angle

    def update(self) -> tuple[pygame.Surface, float, float]:
        self.angle = (self.angle + self.rotation_velocity) % 360
        sprite_copy = pygame.transform.rotate(self.sprite_default, self.angle)

        sprite_width, sprite_height = sprite_copy.get_size()

        x_min = 0 - sprite_width
        x_max = self.window_dimensions[0] + sprite_width

        # if ship is on the boundary bottom, stop all movement (landed)
        if self.y_pos >= self.window_dimensions[1] - sprite_height and not self.landed:
            self.attempt_landing()

        elif not self.landed:
            # check if sprite is outside of boundary X fields
            if self.x_pos < x_min:
                self.x_pos = x_max - 1
            elif self.x_pos > x_max:
                self.x_pos = x_min + 1

            heat_reduce = self.heat - (self.heat_coefficient / 10)
            self.heat = heat_reduce if heat_reduce > 0 else 0

            self.y_vel += self.gravity

            self.y_pos += self.y_vel
            self.x_pos += self.x_vel

        return (
            sprite_copy,
            self.x_pos - int(sprite_width / 2),
            self.y_pos - int(sprite_height / 2)
        )
