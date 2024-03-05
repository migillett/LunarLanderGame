from os import path
import json

from functions.data_structures import *
from functions.lander import PlayerLander
from functions.colors import *

import pygame


class LunarLanderGame:
    def __init__(self, dimensions: tuple[int, int] = (720, 720), fps: int = 60) -> None:
        pygame.init()
        pygame.display.set_caption('Lunar Lander')
        pygame.font.init()

        self.game_loop = True

        self.background = black
        self.delay = int(1000 / fps)
        self.dimensions = dimensions

        self.scores_path = path.join(path.dirname(
            path.abspath(__file__)), 'high_scores.json')
        self.high_scores: list[ScoreEntry] = []

        self.font = pygame.font.SysFont('Terminal', 24)

        self.canvas = pygame.display.set_mode(self.dimensions)

        self.lander: PlayerLander = PlayerLander(
            x_pos=int(dimensions[0] / 2),
            y_pos=int(dimensions[1] / 4),
            fuel_level=50.0,
            strength=0.25,
            max_velocity=3.00)

    def load_high_scores(self) -> None:
        if path.exists(self.scores_path):
            with open(self.scores_path, 'r') as f:
                self.high_scores: list[ScoreEntry] = json.load(f)

    def write_high_scores(self) -> None:
        high_scores = sorted(self.high_scores, key=lambda x: x['score'])
        if len(high_scores) > 10:
            high_scores = high_scores[:10]
        with open(self.scores_path, 'w') as f:
            json.dump(high_scores, f)

    def generate_text(self, x_pos: int, y_pos: int, spacing: int = 20) -> None:
        x_vel_text = f'X velocity: {round(self.lander.x_vel, 2)}'
        x_vel_render = self.font.render(x_vel_text, True, white)
        self.canvas.blit(x_vel_render, (x_pos, y_pos))

        y_vel_text = f'Y velocity: {round(self.lander.y_vel, 2)}'
        y_vel_render = self.font.render(y_vel_text, True, white)
        self.canvas.blit(y_vel_render, (x_pos, y_pos + (spacing * 1)))

    def draw_fuel_gauge(self, x_pos: int, y_pos: int) -> None:
        fuel_bar_length = 100
        fuel_bar_height = 15

        fuel_render = self.font.render('Fuel:', True, white)
        self.canvas.blit(fuel_render, (x_pos, y_pos))

        fill = int((self.lander.fuel_remaining / self.lander.max_fuel) * fuel_bar_length)  # noqa
        outline_rect = pygame.Rect(
            x_pos + 50, y_pos, fuel_bar_length, fuel_bar_height)
        fill_rect = pygame.Rect(
            x_pos + 50, y_pos, fill, fuel_bar_height)
        pygame.draw.rect(self.canvas, white, fill_rect)
        pygame.draw.rect(self.canvas, white, outline_rect, 2)

    def generate_graphics(self) -> None:
        self.canvas.fill(self.background)
        self.lander.update(
            delay_interval=self.delay,
            boundaries=(self.dimensions[0], self.dimensions[1] - 20))
        pygame.draw.rect(self.canvas, white, (self.lander.x_pos, self.lander.y_pos, 10, 10))  # noqa

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_loop = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.lander.thrust_left()
        if keys[pygame.K_RIGHT]:
            self.lander.thrust_right()
        if keys[pygame.K_DOWN]:
            self.lander.thrust_down()
        if keys[pygame.K_UP]:
            self.lander.thrust_up()

        if keys[pygame.K_q]:
            self.game_loop = False

    def handle_landings(self) -> None:
        if self.lander.landed:
            score: ScoreEntry = {
                'name': 'Player',
                'score': self.lander.calculate_score()}
            self.high_scores.append(score)
            pygame.time.delay(5000)
            self.game_loop = False

    def run(self) -> None:
        self.load_high_scores()

        while self.game_loop:
            pygame.time.delay(self.delay)  # 10 ms

            self.handle_events()
            self.generate_graphics()
            self.generate_text(x_pos=10, y_pos=10)
            self.draw_fuel_gauge(x_pos=10, y_pos=50)

            self.handle_landings()

            pygame.display.update()

        self.write_high_scores()


if __name__ == "__main__":
    lander = LunarLanderGame()
    lander.run()
