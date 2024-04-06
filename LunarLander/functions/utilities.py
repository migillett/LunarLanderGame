from functions.data_structures import *


def text_offset(text_list: list[str], window_dimensions: tuple[int, int]) -> int:
    return int((window_dimensions[1] // 2) - int(len(text_list)//2 * 30))


def sort_scores(scores: list[ScoreEntry]) -> list[ScoreEntry]:
    return sorted(scores, key=lambda x: x.score, reverse=True)


def is_high_score(scores: list[ScoreEntry], user_score: ScoreEntry) -> bool:
    if user_score.score == 0:
        return False

    if len(scores) < 10:
        return True

    for score in scores:
        if user_score.score > score.score:
            return True
    return False
