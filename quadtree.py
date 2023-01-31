from copy import copy
from math import inf
from typing import Iterator


def path_to_pos(path: list[int]) -> int:
    """
    0과 1로 이루어진 path list를 position 값으로 변환하여 출력한다.
    """
    pos = 0
    while path:
        pos <<= 1
        pos += int(path.pop())
    return pos


def pos_to_path(number: int, length: int = 1) -> list:
    """
    position 값을 path list로 변환하여 출력한다.
    """
    path = list()
    while number:
        path.append(number & 1)
        number >>= 1

    while len(path) < length:
        path.append(0)
    return path


def pos_to_path_int(pos: int, unit: int) -> int:
    """
    position 값을 path int로 변환하여 출력한다.
    """
    return int(format(pos, f'0{unit}b')[::-1], 2)


def path_int_to_pos(path_int: int, unit: int) -> int:
    """
    path int을 position 값으로 변환하여 출력한다.
    """
    return int((format(path_int, 'b')[::-1] + '0'*unit)[:unit], 2)


def range_pos(start_pos: int, end_pos: int, unit: int) -> Iterator[int]:
    """
    ``start_pos``부터 ``end_pos``까지를 순회하는 iterator를 반환한다.
    """
    start_path = pos_to_path_int(start_pos, unit)
    end_path = pos_to_path_int(end_pos, unit)

    return map(lambda x: path_int_to_pos(x, unit), range(start_path, end_path))


def get_position_by_family_path(family_path):
    """
    ``family_path``의 position 값을 반환한다.
    """
    if family_path is None:
        return None

    x_path = list(map(lambda x: x[0], family_path))
    y_path = list(map(lambda x: x[1], family_path))

    x_pos = path_to_pos(x_path)
    y_pos = path_to_pos(y_path)

    return x_pos, y_pos


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
        """
        ``self``에 ``self``와 같은 ``value``를 가진 자식 사분트리를 가지게 한다.

        반대 연산은 ``self.combine``
        """
        self.children = tuple(copy(self) for _ in range(4))
        return self

    def combine(self, with_=None):
        """
        ``self``에 children이 할당되어있는 것을 없앤다.

        반대 연산은 ``self.divide``
        """
        self.children = tuple()
        if with_ is not None:
            self.value = with_
        return self

    def is_divided(self):
        """
        ``self``가 나누어져있는 트리인지 확인한다.
        """
        return len(self.children) == 4

    def get_depth(self) -> int:
        """
        ``self``로부터 더 이상 자식을 가지지 않기 위해서는 몇 세대를 거듭해야하는지 나타낸다.
        만약 ``self``가 자식을 가지고 있지 않다면 0을 반환한다.
        """
        if not self.is_divided():
            return 0

        return max(map(lambda child: child.get_depth(), self.children))+1

    def print_tree(self, *, indent_level: int = 0, x_path: tuple = tuple(), y_path: tuple = tuple()) -> str:
        """
        트리의 내용을 확인하기 편리하도록 문자열로 정리된 트리를 출력한다.
        """
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

    def get(self, x_pos: int, y_pos: int, unit: int = inf):
        """
        트리 면 속 특정 좌표에 할당된 트리를 출력한다.
        """
        x_path = pos_to_path(x_pos)
        y_path = pos_to_path(y_pos)

        now = self
        i = 0
        while x_path or y_path:
            if i >= unit:
                break

            x = x_path.pop(0) if x_path else 0
            y = y_path.pop(0) if y_path else 0
            index = y*2 + x

            if not now.children:
                return now

            now = now.children[index]
            i += 1

        return now

    def set(self, x_pos: int, y_pos: int, unit: int, value):
        tree = self.get(x_pos, y_pos, unit)
        tree.combine(value)
        return tree

    def get_family_path(self, tree: 'QuadTree'):
        """
        ``self``에서 ``tree``까지 이어지는 가족 계보를 반환한다.

        만약 ``self``의 자식중에 ``tree``가 없다면 None을 반환한다.
        """
        try:
            index = self.children.index(tree)
        except ValueError:
            for i, child in enumerate(self.children):
                position = child.get_family_path(tree)
                if position:
                    y, x = divmod(i, 2)
                    return ((x, y),) + position
        else:
            y, x = divmod(index, 2)
            return (x, y),

    def get_position(self, tree: 'QuadTree'):
        """
        ``self``에 대한 ``tree``의 position 값을 반환한다.

        만약 ``self``의 자식중에 ``tree``가 없다면 None을 반환한다.
        """
        path = self.get_family_path(tree)
        return get_position_by_family_path(path)


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

    subtree = qt.set(2, 0, 2, 9)
    print(qt)

    print(qt.get_family_path(subtree))
    print(qt.get_position(subtree))


if __name__ == '__main__':
    _main()
