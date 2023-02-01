def convert_color(color: tuple) -> str:
    """
    색상 순서쌍을 문자열로 변환한다.
    """
    return f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
