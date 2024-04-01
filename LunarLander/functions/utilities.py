from functions.data_structures import *


def text_offset(text_list: list[str], window_dimensions: tuple[int, int]) -> int:
    return int((window_dimensions[1] // 2) - int(len(text_list)//2 * 30))


def sort_scores(scores: list[ScoreEntry]) -> list[ScoreEntry]:
    sorted_scores = sorted(scores, key=lambda x: x.score, reverse=True)
    if len(sorted_scores) > 10:
        sorted_scores = sorted_scores[:10]
    return sorted_scores
