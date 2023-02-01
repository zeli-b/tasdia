def convert_color(color: tuple) -> str:
    """
    색상 순서쌍을 문자열로 변환한다.
    """
    return f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'


def reveal_color(color: str) -> tuple:
    """
    색상 문자열을 순서쌍으로 변환한다.
    """
    assert color[0] == '#'

    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    return r, g, b
