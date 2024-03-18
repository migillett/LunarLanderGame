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
        cls.max_speed = 2.0
        cls.starting_velocity = 1.0
        cls.starting_angular_velocity = 0.0

        if cls.difficulty_preset == 1:
            # Moon: less gravity, less heat
            cls.difficulty_name = "Moon"
            cls.gravity = 0.0253
            cls.heat_coefficient = 1.0
            cls.score_multiplier = 1.0

        elif cls.difficulty_preset == 2:
            # Moon: same as 1, but with a curveball for angular velocity and starting velocity
            cls.difficulty_name = "Curveball Moon"
            cls.gravity = 0.0253
            cls.starting_angular_velocity = float(randint(-5, 5))
            cls.starting_velocity = float(randint(0, 2))
            cls.heat_coefficient = 2.0
            cls.score_multiplier = 2.0

        # elif cls.difficulty_preset == 3:
        #     # Earth: standard gravity, even hotter
        #     cls.difficulty_name = "Earth"
        #     cls.gravity = 9.81
        #     cls.heat_coefficient = 4.0
        #     cls.score_multiplier = 4.0

        # elif difficulty_setting == 3:  # earth?
        #     cls.difficulty_preset = 3

        # elif difficulty_setting == 4: # ???
        #     cls.difficulty_preset = 4

        # elif difficulty_setting == 69:  # for testing
        #     cls.difficulty_preset = 69
        #     cls.max_speed = 99999999999


@dataclass
class ScoreEntry:
    name: str
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

        if cls.flight_time <= 30.0:
            # No time for chit-chat - land successfully in less than 30 seconds
            cls.score += 600
            cls.achievements.append("No time for chit-chat")
        elif int(cls.flight_time) == 69:
            # huhu, nice
            cls.score += 69
            cls.achievements.append("Nice")

        if cls.heat >= 95.0:
            # coming in hot - land successfully with heat above 95%
            cls.score += 600
            cls.achievements.append("Coming in hot")
        elif cls.heat <= 1.0:
            # cool as a cucumber - land with less than 1% heat
            cls.score += 1000
            cls.achievements.append("Cool as a cucumber")

        cls.score += int((cls.fuel_remaining / cls.flight_time) * 100)  # noqa
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
    difficulty = DifficultySettings()

    score = ScoreEntry(
        name="Player 1",
        flight_time=30.0,
        fuel_remaining=0.0,
        crashed=False,
        difficulty_settings=difficulty)
    score.calculate_score()
    print(score.as_dict())
