from os import path
import json

from functions.lander import *
from functions.colors import *
from functions.data_structures import *
from functions.utilities import *

import pygame


class LunarLanderGame:
    def __init__(
            self,
            dimensions: tuple[int, int] = (720, 720),
            fps: int = 60,
            game_state: str = 'main_menu') -> None:

        self.version = '1.0.3'

        self.abs_path = path.dirname(path.abspath(__file__))
        self.audio_path = path.join(self.abs_path, 'assets', 'audio')

        pygame.init()
        pygame.display.set_caption(f'Lunar Lander | {self.version}')
        pygame.font.init()
        pygame.display.set_icon(pygame.image.load(
            path.join(self.abs_path, 'assets', 'lander', 'lander_default.png')))

        self.game_state: str | None = game_state
        self.start_time: datetime = datetime.now()
        self.flight_time: float = 0.0

        # game_loop_init (and difficulty) goes up by 1 every successful landing
        self.game_loop_int: int = 1

        # user interface settings
        self.background = black
        self.fps = fps
        self.dimensions = dimensions
        self.font = pygame.font.Font(
            path.join(self.abs_path, 'assets', 'VT323-Regular.ttf'), 24)
        self.canvas = pygame.display.set_mode(self.dimensions)

        # high score settings
        self.user_name = NameEntry()
        self.user_score: ScoreEntry | None = None
        self.scores_path = path.join(self.abs_path, 'high_scores.json')
        self.high_scores: list[ScoreEntry] = []

        self.difficulty: DifficultySettings | None = None

    def init_game(self) -> None:
        # load main theme music

        pygame.mixer.music.load(
            path.join(self.audio_path, 'main-theme.mp3'))
        pygame.mixer.music.play(-1)

        self.user_score = None
        self.difficulty = DifficultySettings(self.game_loop_int)
        self.start_time = datetime.now()

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
        if path.exists(self.scores_path):
            with open(self.scores_path, 'r') as f:
                self.high_scores: list[ScoreEntry] = [
                    ScoreEntry(**x) for x in json.load(f)]

    def write_high_scores(self) -> None:
        high_scores = sort_scores(self.high_scores)
        with open(self.scores_path, 'w') as f:
            json.dump([x.as_dict() for x in high_scores], f, indent=4)

    def calculate_flight_time(self) -> None:
        if not self.lander.landed:  # only update flight time if the lander hasn't landed
            self.flight_time = round(
                (datetime.now() - self.start_time).total_seconds(), 2)

    def blit_menu_text(self, text_list: list[str]) -> None:
        start_y = text_offset(text_list, self.dimensions)
        for line in text_list:
            text_render = self.font.render(line, True, white)
            text_rect = text_render.get_rect(
                center=(self.dimensions[0] // 2, start_y))
            start_y += text_render.get_height()
            self.canvas.blit(text_render, text_rect)

    def main_menu(self) -> None:
        # TODO - Fix this
        self.canvas.fill(self.background)
        menu_text = [
            'LUNAR LANDER',
            f'Version: {self.version}',
            '',
            'Press "T" to view high scores',
            'Press any button to Continue',
            '',
            'Press "Q" to Quit']

        self.blit_menu_text(menu_text)

    def high_score_menu(self) -> None:
        menu_text = [
            'NEW HIGH SCORE!',
            '',
            f'Score: {self.user_score.score}',
            'Type your name:',
            self.user_name.to_str(),
        ]
        self.blit_menu_text(menu_text)

    def show_high_scores(self) -> None:
        self.high_scores = sort_scores(self.high_scores)
        high_score_text = ['HIGH SCORES:']
        if len(self.high_scores) > 0:
            high_score_text.extend([
                f'{x.name}: {x.score:>8,}' for x in self.high_scores
            ])

        high_score_text.extend(['', 'Press Space to Continue'])

        self.blit_menu_text(high_score_text)

    def render_overheat_warning(self) -> None:
        warning_text = ''
        if not self.lander.landed:
            if self.lander.thruster_on_cooldown():
                warning_text = 'MANDATORY THRUSTER COOLDOWN'
            elif self.lander.heat >= (self.lander.max_heat * 0.8):
                warning_text = 'WARNING: HIGH HEAT!'

        warning_render = self.font.render(warning_text, True, red)
        warning_rect = warning_render.get_rect(
            center=(self.dimensions[0] // 2, self.dimensions[1] // 2))

        self.canvas.blit(warning_render, warning_rect)

    def render_hud(self, x_pos: int, y_pos: int, spacing: int = 20) -> None:
        self.render_overheat_warning()

        if self.user_score is not None:
            self.display_score(self.user_score)

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

        # COOLDOWN TIMER
        if self.lander.thruster_on_cooldown():
            timer = self.lander.cooldown_period - (
                datetime.now() - self.lander.overheat_timestamp)
            cooldown_timer = self.font.render(
                f'Thruster Cooldown: {round(timer.total_seconds(), 2)}', True, red)
            self.canvas.blit(cooldown_timer, (x_pos, y_pos + spacing))

    def render_graphics(self) -> None:
        ground_start = self.dimensions[1] - 25

        # draw the ground
        pygame.draw.rect(
            self.canvas, white,
            (0, ground_start, self.dimensions[0], 25))

        # draw the lander
        lander_sprite, x_pos, y_pos = self.lander.update()
        self.canvas.blit(lander_sprite, (x_pos, y_pos))

        if self.lander.landed and not self.lander.crashed:
            astronauts_sprite = pygame.image.load(
                path.join(self.abs_path, 'assets', 'astronauts.png'))

            scale_factor = 50 / astronauts_sprite.get_width()
            astronauts_sprite = pygame.transform.scale(
                astronauts_sprite, (
                    int(astronauts_sprite.get_width() * scale_factor),
                    int(astronauts_sprite.get_height() * scale_factor)
                )
            )

            self.canvas.blit(
                astronauts_sprite, (
                    x_pos - 50,
                    ground_start - astronauts_sprite.get_height()
                )
            )

    def audio_landed(self) -> None:
        if not self.lander.crashed:
            audio_path = path.join(
                self.audio_path, 'victory', 'VictorySmall.wav')
        else:
            audio_path = path.join(
                self.audio_path, 'explosions', 'Explosion3.wav')

        landing_audio = pygame.mixer.Sound(audio_path)
        pygame.mixer.music.stop()
        pygame.mixer.Sound.play(landing_audio)

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

        score_text.extend([
            '',
            'Press "P" to take a Screenshot',
            'Press Space to Continue',
            'Press "Q" to Quit',
        ])

        self.blit_menu_text(score_text)

    def handle_landing(self) -> None:
        if self.lander.landed and self.user_score is None:
            self.user_score: ScoreEntry = ScoreEntry(
                name=NameEntry(),
                game_version=self.version,
                flight_time=self.flight_time,
                fuel_remaining=round(self.lander.fuel_remaining, 2),
                heat=round(self.lander.heat, 2),
                difficulty_settings=self.difficulty,
                crashed=self.lander.crashed)

            self.user_score.calculate_score()

            self.audio_landed()

    def handle_keyboard_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = None

        keys = pygame.key.get_pressed()

        # restart
        if keys[pygame.K_r]:
            self.init_game()
        # quit
        if keys[pygame.K_q]:
            # quit
            self.game_state = None

        if self.game_state == 'main_menu' and any(keys):
            if keys[pygame.K_t]:
                self.game_state = 'show_scores'
            else:
                self.game_state = 'run'

        elif self.game_state == 'high_score' and self.user_score is not None:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.user_name.move_selector(1)
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.user_name.move_selector(-1)
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                self.user_name.move_character(-1)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.user_name.move_character(1)
            elif keys[pygame.K_RETURN]:
                self.game_state = 'run'
                self.user_score.name = self.user_name.to_str()
                self.high_scores.append(self.user_score)
                self.init_game()
            pygame.time.wait(85)

        elif self.game_state == 'show_scores':
            if keys[pygame.K_SPACE]:
                self.game_state = 'run'

        elif self.game_state == 'run':
            # include controls for both WASD and Arrow Keys
            if keys[pygame.K_UP] or keys[pygame.K_w]:  # fire main thruster
                self.lander.fire_thruster()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # pitch left
                self.lander.fire_rcs(0.25)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # pitch right
                self.lander.fire_rcs(-0.25)

            # If landed successfully
            if self.user_score is not None and keys[pygame.K_SPACE]:
                if is_high_score(self.high_scores, self.user_score):
                    self.game_state = 'high_score'
                else:
                    # TODO - disabling for now till I figure out additive difficulty
                    # self.game_loop_int += 1
                    self.init_game()  # reset the score if not in high scores

            # take screenshot
            if keys[pygame.K_p]:
                filename = f'LunarLander_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
                pygame.image.save(
                    self.canvas,
                    path.join(self.abs_path, filename))

    def run(self) -> None:
        self.load_high_scores()

        # only init when loading game from start (for testing)
        if self.game_state == 'main_menu':
            self.init_game()

        while self.game_state is not None:

            self.canvas.fill(self.background)

            if self.game_state == "main_menu":
                self.main_menu()

            elif self.game_state == "high_score":
                self.high_score_menu()

            elif self.game_state == 'show_scores':
                self.show_high_scores()

            else:
                self.handle_landing()
                self.calculate_flight_time()
                self.render_graphics()
                self.render_hud(x_pos=10, y_pos=10)

            self.handle_keyboard_events()

            pygame.display.flip()

            pygame.time.Clock().tick(self.fps)

        self.write_high_scores()


if __name__ == "__main__":
    lander = LunarLanderGame(
        dimensions=(720, 720),
        fps=60)

    lander.run()
