from dataclasses import dataclass, asdict, field
from datetime import datetime
from random import randint


@dataclass
class DifficultySettings:
    # default settings = Easy
    difficulty_preset: int
    difficulty_name: str
    gravity: float
    max_speed: float
    score_multiplier: float
    starting_velocity: float
    starting_angular_velocity: float
    heat_coefficient: float

    def __init__(cls, difficulty_setting: int = 1) -> None:
        # default settings
        cls.difficulty_preset = difficulty_setting
        cls.max_speed = 1.5
        cls.starting_velocity = 1.0
        cls.starting_angular_velocity = 0.0
        cls.gravity = 0.0253

        if cls.difficulty_preset == 1:
            # Moon: less gravity, less heat
            cls.difficulty_name = "Moon"
            cls.heat_coefficient = 0.5
            cls.score_multiplier = 1.0

        elif cls.difficulty_preset == 2:
            # Moon: same as 1, but with a curveball for angular velocity and starting velocity
            cls.difficulty_name = "Curveball Moon"
            cls.starting_angular_velocity = float(randint(-5, 5))
            cls.starting_velocity = float(randint(0, 2))
            cls.heat_coefficient = 1.0
            cls.score_multiplier = 2.0

        print(f'Loaded difficulty: {cls.__dict__}')


class NameEntry:
    def __init__(self):
        # list of valid characters for a given name
        self.letters: list[str] = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G',
            'H', 'I', 'J', 'K', 'L', 'M', 'N',
            'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z']
        self.name: list[int] = [0, 0, 0]
        self.selector_index: int = 0

    def move_selector(self, move_direction: int = 1) -> None:
        self.selector_index = (
            self.selector_index + move_direction) % len(self.name)

    def move_character(self, move_direction: int = 1) -> None:
        self.name[self.selector_index] = (
            self.name[self.selector_index] + move_direction) % len(self.letters)

    def selector_text(self) -> str:
        return f"{' ' * self.selector_index}^{' ' * (2 - self.selector_index)}"

    def to_str(self) -> str:
        # returns a concat string of letters in name
        name = ''.join([self.letters[x] for x in self.name])
        return name


@dataclass
class ScoreEntry:
    name: str
    game_version: str
    flight_time: float
    fuel_remaining: float
    heat: float
    crashed: bool
    difficulty_settings: DifficultySettings
    score: int = 0
    timestamp: float = datetime.now().timestamp()
    achievements: list = field(default_factory=list)

    def calculate_score(cls) -> None:
        if cls.crashed:
            return

        if cls.fuel_remaining == 0:
            # nothing but fumes - land successfully with with no fuel remaining
            cls.score += 1000
            cls.achievements.append("Nothing but fumes")
        elif cls.fuel_remaining >= 90.0:
            # Fuel efficient
            cls.score += 600
            cls.achievements.append("Fuel efficient")

        if cls.flight_time <= 15.0:
            # No time for chit-chat - land successfully in less than n seconds
            cls.score += 600
            cls.achievements.append("No time for chit-chat")
        elif int(cls.flight_time) == 69:
            # huhuhu nice
            cls.score += 69
            cls.achievements.append("Nice")
        elif int(cls.flight_time) >= 120:
            # Dilly-dallying - land successfully after more than 120 seconds
            cls.score += 100
            cls.achievements.append("Dilly-dallying")

        if cls.heat >= 95.0:
            # coming in hot - land successfully with heat above 95%
            cls.score += 600
            cls.achievements.append("Coming in hot")
        elif cls.heat <= 2.5:
            # cool as a cucumber - land with less than 2.5% heat
            cls.score += 1000
            cls.achievements.append("Cool as a cucumber")

        # V1.0.3 - Adjust score to weight fuel efficiency more heavily
        cls.score += int((cls.fuel_remaining * 2 / cls.flight_time) * 100)  # noqa
        cls.score = int(
            cls.score * cls.difficulty_settings.score_multiplier)

    def as_dict(cls) -> dict:
        response = {}
        for key, value in asdict(cls).items():
            if isinstance(value, DifficultySettings):
                response[key] = value.__dict__
            else:
                response[key] = value
        return response


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    x_values = range(10, 180)
    y_values = []

    difficulty = DifficultySettings()

    for x in x_values:
        score = ScoreEntry(
            name="",
            game_version='test',
            flight_time=x,
            fuel_remaining=30,
            heat=50.0,
            crashed=False,
            difficulty_settings=difficulty)
        score.calculate_score()
        y_values.append(score.score)

    plt.plot(x_values, y_values)
    plt.xlabel('Flight Time (Seconds)')
    plt.ylabel('Score')
    plt.title('Correlation between Flight Time and Total Score')
    plt.show()
