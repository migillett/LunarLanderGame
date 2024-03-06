from datetime import datetime
import pygame


class PlayerLander:
    gravity: float
    x_pos: int
    y_pos: int
    thurster_strength: float
    max_fuel: float
    fuel_remaining: float
    max_velocity: float

    x_vel: float = 0.0
    y_vel: float = 0.0
    lives: int = 3
    landed: bool = False
    crashed: bool = False

    def __init__(
            self, x_pos: int, y_pos: int,
            strength: float, fuel_level: float,
            max_velocity: float, image_path: str,
            gravity: float = 0.0253) -> None:
        self.gravity = gravity  # lunar gravity is 0.0253 m/s^2
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.thurster_strength = strength
        self.max_fuel = fuel_level
        self.fuel_remaining = fuel_level
        self.max_velocity = max_velocity

        self.sprite: pygame.image = self.load_sprite(image_path, 50)

        self.t1 = datetime.now()

    def fire_thrusters(self) -> bool:
        if self.fuel_remaining > 0:
            self.fuel_remaining -= self.thurster_strength
            return True
        return False

    def load_sprite(self, image_path: str, max_height: int) -> pygame.image:
        sprite = pygame.image.load(image_path).convert()
        sprite_width, sprite_height = sprite.get_size()
        scale_factor = max_height / sprite_width

        sprite = pygame.transform.scale(
            sprite, (int(sprite_width * scale_factor), int(sprite_height * scale_factor)))
        return sprite

    def thrust_left(self) -> None:
        if self.fire_thrusters():
            self.x_vel -= self.thurster_strength

    def thrust_right(self) -> None:
        if self.fire_thrusters():
            self.x_vel += self.thurster_strength

    def thrust_down(self) -> None:
        if self.fire_thrusters():
            self.y_vel += self.thurster_strength

    def thrust_up(self) -> None:
        if self.fire_thrusters():
            self.y_vel -= self.thurster_strength

    def attempt_landing(self) -> None:
        self.landed = True
        self.crashed = self.max_velocity <= (self.y_vel + self.x_vel)

    def calculate_score(self) -> float:
        if self.crashed:
            print('CRASHED!')
            return 0.0

        flight_time = round((datetime.now() - self.t1).total_seconds(), 2)
        score = int((self.fuel_remaining / flight_time) * 100)
        print(f'Total flight time: {flight_time} seconds')
        print(f'Remaining Fuel: {round(self.fuel_remaining, 2)}')
        print(f'Successful Landing! Score: {score}')
        return score

    def update(self, delay_interval: float, window_size: tuple[int, int]) -> None:
        # window_size dimensions are in (x, y)

        sprite_width, sprite_height = self.sprite.get_size()

        x_min = 0 - sprite_width
        x_max = window_size[0] + sprite_width

        # if ship is on the boundary bottom, stop all movement (landed)
        if self.y_pos >= window_size[1] - sprite_height:
            if not self.landed:
                self.attempt_landing()

            # self.y_pos = window_size[1] - sprite_height
            self.y_vel = 0
            self.x_vel = 0
            self.fuel_remaining = 0
            return

        # check if sprite is outside of boundary X fields
        if self.x_pos < x_min:
            self.x_pos = x_max - 1
        elif self.x_pos > x_max:
            self.x_pos = x_min + 1

        self.y_vel += (self.gravity / delay_interval)

        self.y_pos += self.y_vel
        self.x_pos += self.x_vel
