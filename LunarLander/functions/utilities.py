def text_offset(text_list: list[str], window_dimensions: tuple[int, int]) -> int:
    return int((window_dimensions[1] // 2) - int(len(text_list)//2 * 30))
