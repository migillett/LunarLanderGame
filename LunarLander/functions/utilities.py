from functions.data_structures import *


def text_offset(text_list: list[str], window_dimensions: tuple[int, int]) -> int:
    return int((window_dimensions[1] // 2) - int(len(text_list)//2 * 30))


def parse_version_number(version: str) -> list[int, int, int] | None:
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f'ERROR: unable to parse version: {version}')
    return parts


def sort_scores(scores: list[ScoreEntry], version: str | None = None) -> list[ScoreEntry]:
    scores = sorted(scores, key=lambda x: x.score, reverse=True)
    if version is None:
        return scores

    current_version = parse_version_number(version)
    # filter scores based on what version the game currently (major and minor version, not patch)
    valid_scores = []
    for score in scores:
        score_version = parse_version_number(score.game_version)
        if score_version[0] == current_version[0] and score_version[1] == current_version[1]:
            valid_scores.append(score)

    return valid_scores


def is_high_score(scores: list[ScoreEntry], user_score: ScoreEntry) -> bool:
    if user_score.score == 0:
        return False

    scores = sorted(scores, key=lambda x: x.score, reverse=True)
    if len(scores) < 10:
        return True

    for score in scores[:10]:
        if user_score.score > score.score:
            return True
    return False
