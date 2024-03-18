from os import path
import json

from functions.lander import *
from functions.colors import *
from functions.data_structures import *

import pygame


class LunarLanderGame:
    def __init__(
            self, difficulty: DifficultySettings,
            dimensions: tuple[int, int] = (720, 720),
            fps: int = 60,
            enable_scores: bool = False) -> None:

        pygame.init()
        pygame.display.set_caption('Lunar Lander')
        pygame.font.init()

        self.start_time: datetime = datetime.now()
        self.flight_time: float = 0.0

        self.abs_path = path.dirname(path.abspath(__file__))

        self.game_loop = True

        # user interface settings
        self.background = black
        self.fps = fps
        self.dimensions = dimensions
        self.font = pygame.font.Font(
            path.join(self.abs_path, 'assets', 'VT323-Regular.ttf'), 24)
        self.canvas = pygame.display.set_mode(self.dimensions)

        # high score settings
        self.enable_scores: bool = enable_scores
        self.user_score: ScoreEntry | None = None
        self.scores_path = path.join(self.abs_path, 'high_scores.json')
        self.high_scores: list[ScoreEntry] = []

        self.difficulty = difficulty

    def start_game(self) -> None:
        self.start_time = datetime.now()
        self.user_score = None
        self.lander: PlayerLander = PlayerLander(
            x_pos=int(1),
            y_pos=int(self.dimensions[1] / 4),
            angle=90.0,
            angular_velocity=self.difficulty.starting_angular_velocity,
            strength=0.25,
            max_velocity=self.difficulty.max_speed,
            abs_path=self.abs_path,
            heat_coefficient=self.difficulty.heat_coefficient,
            window_dimensions=self.dimensions,
            gravity=(self.difficulty.gravity/int(1000 / self.fps)))
        self.lander.x_vel = self.difficulty.starting_velocity

    def load_high_scores(self) -> None:
        if self.enable_scores and path.exists(self.scores_path):
            with open(self.scores_path, 'r') as f:
                self.high_scores: list[ScoreEntry] = json.load(f)

    def write_high_scores(self) -> None:
        if self.enable_scores:
            high_scores = sorted(
                self.high_scores, key=lambda x: x['score'], reverse=True)
            if len(high_scores) > 10:
                high_scores = high_scores[:10]
            with open(self.scores_path, 'w') as f:
                json.dump(high_scores, f, indent=4)

    def calculate_flight_time(self) -> None:
        if not self.lander.landed:  # only update flight time if the lander hasn't landed
            self.flight_time = round(
                (datetime.now() - self.start_time).total_seconds(), 2)

    def generate_text(self, x_pos: int, y_pos: int, spacing: int = 20) -> None:
        combined_velocity = abs(self.lander.x_vel) + abs(self.lander.y_vel)
        velocity_color = red if combined_velocity > self.lander.max_velocity else white  # noqa

        # X VELOCITY
        x_vel_text = f'X velocity: {round(self.lander.x_vel, 2)}'
        x_vel_render = self.font.render(x_vel_text, True, velocity_color)
        self.canvas.blit(x_vel_render, (x_pos, y_pos))

        y_pos += spacing

        # Y VELOCITY
        y_vel_text = f'Y velocity: {round(self.lander.y_vel, 2)}'
        y_vel_render = self.font.render(y_vel_text, True, velocity_color)
        self.canvas.blit(y_vel_render, (x_pos, y_pos))

        y_pos += spacing

        # ANGLE VELOCITY
        ang_vel_text = f'Rotation Velocity: {self.lander.rotation_velocity}'
        ang_vel_render = self.font.render(ang_vel_text, True, white)
        self.canvas.blit(ang_vel_render, (x_pos, y_pos))

        y_pos += spacing

        # ANGLE OF SPACECRAFT
        current_angle = round((self.lander.angle + 90) % 360, 2)
        angle_text = f'Current Angle: {current_angle}'
        angle_color = white if current_angle <= 10 or current_angle >= 350 else red
        angle_render = self.font.render(angle_text, True, angle_color)
        self.canvas.blit(angle_render, (x_pos, y_pos))

        y_pos += spacing

        # FLIGHT TIME
        flight_time_text = f'Flight Time: {round(self.flight_time, 2)}'
        flight_time_render = self.font.render(flight_time_text, True, white)
        self.canvas.blit(flight_time_render, (x_pos, y_pos))

        y_pos += spacing

        # FUEL BAR
        fuel_bar_length = 100
        fuel_bar_height = 15

        fuel_render = self.font.render('Fuel:', True, white)
        self.canvas.blit(fuel_render, (x_pos, y_pos))

        fill = int((self.lander.fuel_remaining / self.lander.max_fuel) * fuel_bar_length)  # noqa
        outline_rect = pygame.Rect(
            x_pos + 50, y_pos + 6, fuel_bar_length, fuel_bar_height)
        fill_rect = pygame.Rect(
            x_pos + 50, y_pos + 6, fill, fuel_bar_height)
        pygame.draw.rect(self.canvas, white, fill_rect)
        pygame.draw.rect(self.canvas, white, outline_rect, 2)

        y_pos += spacing

        # HEAT BAR
        heat_bar_length = 100
        heat_bar_height = 15

        heat_color = red if self.lander.heat > 80.0 else white
        heat_render = self.font.render('Heat:', True, heat_color)
        self.canvas.blit(heat_render, (x_pos, y_pos))

        heat_fill = int((self.lander.heat / self.lander.max_heat) * heat_bar_length)  # noqa
        outline_rect = pygame.Rect(
            x_pos + 50, y_pos + 6, heat_bar_length, heat_bar_height)
        heat_fill_rect = pygame.Rect(
            x_pos + 50, y_pos + 6, heat_fill, heat_bar_height)
        pygame.draw.rect(self.canvas, heat_color, heat_fill_rect)
        pygame.draw.rect(self.canvas, heat_color, outline_rect, 2)

        if self.user_score is not None:
            self.display_score(self.user_score)

    def generate_graphics(self) -> None:
        self.canvas.fill(self.background)

        # draw the ground
        pygame.draw.rect(
            self.canvas, white,
            (0, self.dimensions[1] - 25, self.dimensions[0], 25))

        # draw the lander
        lander_sprite, x_pos, y_pos = self.lander.update()
        self.canvas.blit(lander_sprite, (x_pos, y_pos))

    def display_score(self, score: ScoreEntry) -> None:
        if self.lander.crashed:
            score_text = [
                'YOU CRASHED!',
                'Better luck next time.'
            ]

        else:
            score_text = [
                'THE EAGLE HAS LANDED!',
                f'Total Flight Time: {score.flight_time}',
                f'Remaining Fuel: {score.fuel_remaining}'
            ]

            if len(score.achievements) > 0:
                score_text.append(
                    f'Achievements: {", ".join(score.achievements)}',
                )

            score_text.append(f'Final Score: {score.score}')

        score_text.extend(
            ['', 'Press "R" to play again', 'Press "Q" to quit']
        )

        current_y = (self.dimensions[1] // 2) - 100

        for line in score_text:
            text_surface = self.font.render(line, True, white)
            text_rect = text_surface.get_rect(
                center=(self.dimensions[0] // 2, current_y))
            self.canvas.blit(text_surface, text_rect)
            current_y += text_surface.get_height()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_loop = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and not self.lander.landed:  # fire main thruster
            self.lander.fire_thruster()
        if keys[pygame.K_LEFT] and not self.lander.landed:  # pitch left
            self.lander.fire_rcs(0.25)
        if keys[pygame.K_RIGHT] and not self.lander.landed:  # pitch right
            self.lander.fire_rcs(-0.25)

        # restart
        if keys[pygame.K_r]:
            self.start_game()

        # quit
        if keys[pygame.K_q]:
            # quit
            self.game_loop = False

    def run(self) -> None:
        self.load_high_scores()

        self.start_game()

        while self.game_loop:

            if self.lander.landed and self.user_score is None:
                self.user_score: ScoreEntry = ScoreEntry(
                    name='Player 1',
                    flight_time=self.flight_time,
                    fuel_remaining=round(self.lander.fuel_remaining, 2),
                    heat=round(self.lander.heat, 2),
                    difficulty_settings=self.difficulty,
                    crashed=self.lander.crashed)

                self.user_score.calculate_score()

                self.high_scores.append(self.user_score.as_dict())

            self.calculate_flight_time()
            self.handle_events()
            self.generate_graphics()
            self.generate_text(x_pos=10, y_pos=10)

            pygame.display.flip()

            pygame.time.Clock().tick(self.fps)

        self.write_high_scores()


if __name__ == "__main__":
    settings = DifficultySettings(difficulty_setting=1)

    lander = LunarLanderGame(
        difficulty=settings,
        dimensions=(720, 720),
        fps=60,
        enable_scores=False)

    lander.run()
