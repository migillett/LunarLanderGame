import pygame
import math

from functions.data_structures import *


class PlayerLander(pygame.sprite.Sprite):
    gravity: float
    x_pos: float
    y_pos: float
    angle: float
    thruster_strength: float
    max_fuel: float
    fuel_remaining: float
    max_velocity: float
    delay_interval: float
    window_dimensions: tuple[int, int]

    x_vel: float = 0.0
    y_vel: float = 0.0
    rotation_velocity: float = 0.0
    mass: float = 10.0
    lives: int = 3
    landed: bool = False
    crashed: bool = False

    def __init__(
            self, x_pos: int, y_pos: int, angle: float,
            strength: float, fuel_level: float,
            max_velocity: float, image_path: str,
            window_dimensions: tuple[int, int],
            gravity: float) -> None:
        super().__init__()

        self.gravity = gravity  # lunar gravity is 0.0253 m/s^2. Divide that by the FPS
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.angle = angle
        self.thruster_strength = strength
        self.max_fuel = fuel_level
        self.fuel_remaining = fuel_level
        self.max_velocity = max_velocity
        self.window_dimensions = window_dimensions

        self.original_sprite: pygame.image = self.load_sprite(image_path, 50)
        self.sprite = self.original_sprite.copy()
        self.rect = self.original_sprite.get_rect(center=(x_pos, y_pos))

    def load_sprite(self, image_path: str, max_height: int) -> pygame.image:
        sprite = pygame.image.load(image_path)
        sprite_width, sprite_height = sprite.get_size()
        scale_factor = max_height / sprite_height

        sprite = pygame.transform.scale(
            sprite, (int(sprite_width * scale_factor), int(sprite_height * scale_factor)))
        sprite = pygame.transform.rotate(sprite, 90.0)
        return sprite

    def fire_rcs(self, rcs_force: float) -> None:
        if self.fuel_remaining > 0:
            self.fuel_remaining -= self.thruster_strength
            self.rotation_velocity += rcs_force

    def fire_thruster(self) -> None:
        if self.fuel_remaining > 0:
            self.fuel_remaining -= self.thruster_strength
            angle_radians = math.radians(self.angle)
            force_x = self.thruster_strength * math.cos(angle_radians)
            force_y = self.thruster_strength * math.sin(angle_radians)
            self.x_vel -= force_x / self.mass
            self.y_vel += force_y / self.mass

    def attempt_landing(self) -> None:
        self.landed = True
        # must not be more than 10 degrees off true vertical (which is 270, idk why)
        valid_landing_angle = self.angle > 260 and self.angle < 280
        self.crashed = self.max_velocity <= (
            self.y_vel + self.x_vel) or not valid_landing_angle

    def update(self) -> None:
        # window_dimensions dimensions are in (x, y)

        sprite_width, sprite_height = self.sprite.get_size()

        x_min = 0 - sprite_width
        x_max = self.window_dimensions[0] + sprite_width

        # if ship is on the boundary bottom, stop all movement (landed)
        if self.y_pos >= self.window_dimensions[1] - sprite_height:
            if not self.landed:
                self.attempt_landing()

            # self.y_pos = window_dimensions[1] - sprite_height
            self.y_vel = 0
            self.x_vel = 0
            return

        # check if sprite is outside of boundary X fields
        if self.x_pos < x_min:
            self.x_pos = x_max - 1
        elif self.x_pos > x_max:
            self.x_pos = x_min + 1

        self.y_vel += self.gravity

        self.y_pos += self.y_vel
        self.x_pos += self.x_vel
        self.angle = (self.angle + self.rotation_velocity) % 360

        self.image = pygame.transform.rotate(
            self.original_sprite, self.angle)

        self.rect.center = (self.x_pos, self.y_pos)
