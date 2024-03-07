from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class DifficultySettings:
    # default settings = Easy
    difficulty_preset: int = 1
    difficulty_name: str = "Moon"
    gravity: float = 0.0253
    fuel_level: float = 100.0
    max_speed: float = 2.0
    score_multiplier: float = 1.0
    starting_velocity: float = 1.0
    starting_angular_velocity: float = 0.0

    def __init_subclass__(cls, difficulty_setting: int = 1) -> None:
        cls.difficulty_preset = difficulty_setting
        # if difficulty_setting == 2:  # mars?
        #     cls.difficulty_preset = 2

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
