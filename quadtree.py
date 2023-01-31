from copy import copy
from typing import Iterator


def path_to_pos(path: list[int]):
    pos = 0
    while path:
        pos <<= 1
        pos += int(path.pop())
    return pos


def pos_to_path(number: int):
    path = list()
    while number:
        path.append(number & 1)
        number >>= 1

    if not path:
        path.append(0)
    return path


def pos_to_path_int(pos: int, unit: int):
    return int(format(pos, f'0{unit}b')[::-1], 2)


def path_int_to_pos(path_int: int, unit: int):
    return int((format(path_int, 'b')[::-1] + '0'*unit)[:unit], 2)


def range_pos(start_pos: int, end_pos: int, unit: int) -> Iterator[int]:
    start_path = pos_to_path_int(start_pos, unit)
    end_path = pos_to_path_int(end_pos, unit)

    return map(lambda x: path_int_to_pos(x, unit), range(start_path, end_path))


class QuadTree:
    def __init__(self, value):
        self.value = value

        self.children: tuple[QuadTree] = tuple()

    def __repr__(self):
        return f'<QuadTree value={self.value}, children={self.children}>'

    def __copy__(self):
        return QuadTree(self.value)

    def __str__(self):
        return self.print_tree()

    def set_value(self, value):
        self.value = value
        return self

    def divide(self):
        self.children = tuple(copy(self) for _ in range(4))
        return self

    def has_child(self):
        return len(self.children) == 4

    def get_depth(self) -> int:
        if not self.has_child():
            return 0

        return max(map(lambda child: child.get_depth(), self.children))+1

    def print_tree(self, *, indent_level: int = 0, x_path: tuple = tuple(), y_path: tuple = tuple()):
        result = ''
        if indent_level == 0:
            result += '=== Tree ===\n'

        indent_gap = f"{'  ' * (indent_level - 1)}{'- ' if indent_level > 0 else ''}"

        x_pos = path_to_pos(list(x_path))
        y_pos = path_to_pos(list(y_path))
        line = f"{indent_gap}{self.value} ({x_pos}, {y_pos})"
        result += line + '\n'

        for i, child in enumerate(self.children):
            y, x = divmod(i, 2)
            result += child.print_tree(
                indent_level=indent_level + 1,
                x_path=x_path + (x,),
                y_path=y_path + (y,)
            )

        return result

    def get(self, x_pos: int, y_pos: int):
        x_path = pos_to_path(x_pos)
        y_path = pos_to_path(y_pos)

        now = self
        while x_path or y_path:
            x = x_path.pop(0) if x_path else 0
            y = y_path.pop(0) if y_path else 0
            index = y*2 + x

            if not now.children:
                return now

            now = now.children[index]

        return now


def _main():
    qt = QuadTree(0)
    print(qt.get_depth())

    qt.divide()
    qt.children[0].set_value(1)
    qt.children[1].set_value(2)
    qt.children[2].set_value(3)
    qt.children[3].set_value(4)

    qt.children[0].divide()
    qt.children[0].children[0].set_value(5)
    qt.children[0].children[1].set_value(6)
    qt.children[0].children[2].set_value(7)
    qt.children[0].children[3].set_value(8)

    print(qt.get_depth())
    print(qt)

    print('qt(2, 0) =', qt.get(2, 1).value)


if __name__ == '__main__':
    _main()
