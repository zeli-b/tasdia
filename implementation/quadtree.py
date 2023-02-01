from copy import copy
from json import dump, load
from typing import Iterator, Optional

from PIL import Image
from PIL.ImageDraw import Draw


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
        self.parent = None

    def __repr__(self):
        return f'<QuadTree value={self.value}, children={self.children}>'

    def __copy__(self):
        result = QuadTree(self.value)
        result.parent = self.parent

        if self.is_divided():
            children = list()
            for child in self.children:
                clone = copy(child)
                clone.parent = result
                children.append(clone)
            result.children = tuple(children)

        return result

    def __str__(self):
        return self.print_tree()

    def set_value(self, value):
        self.value = value
        return self

    def is_identical_with(self, other: 'QuadTree') -> bool:
        if self.value != other.value:
            return False

        if (divided := self.is_divided()) != other.is_divided():
            return False

        if divided:
            for i in range(4):
                if not self.children[i].is_identical_with(other.children[i]):
                    return False

        return True

    def divide(self):
        """
        ``self``에 ``self``와 같은 ``value``를 가진 자식 사분트리를 가지게 한다.

        반대 연산은 ``self.combine``
        """
        self.children = tuple(QuadTree(self.value) for _ in range(4))
        for child in self.children:
            child.parent = self
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

    def get(self, x_pos: int, y_pos: int, unit: int):
        """
        트리 면 속 특정 좌표에 할당된 트리를 출력한다.
        """
        x_path = pos_to_path(x_pos, unit)
        y_path = pos_to_path(y_pos, unit)

        now = self
        while x_path or y_path:
            x = x_path.pop(0) if x_path else 0
            y = y_path.pop(0) if y_path else 0
            index = y*2 + x

            if not now.children:
                now.divide()

            now = now.children[index]

        return now

    def set(self, x_pos: int, y_pos: int, unit: int, value):
        tree = self.get(x_pos, y_pos, unit)
        tree.set_value(value)
        tree.parent.simplify_upward()
        return tree

    def path_int_set(self, x_path: int, y_path: int, unit: int, value):
        x_pos = path_int_to_pos(x_path, unit)
        y_pos = path_int_to_pos(y_path, unit)
        return self.set(x_pos, y_pos, unit, value)

    def simplify_upward(self):
        """
        ``self``부터 최상위 트리까지를 순회하며 child가 가지고 있는 값이 모두 같다면 combine한다.

        이 메소드가 실행될 때에는 ``self``를 제외하고 그 어떤 부분에서도 자식이 모두 같은 값을 가지고 있지만 divide되어있는 트리가 없음을 상정한다.

        ``self``가 병합해야 하는 트리의 자식이라면 ``self.parent``에 이 함수를 적용해야 한다.
        """
        if not self.is_divided():
            return

        value = self.children[0].value
        for i in range(1, 4):
            if self.children[i].value != value:
                return

        self.combine(value)

        if self.parent is not None:
            self.parent.simplify_upward()

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

    def saves(self) -> tuple:
        """
        트리를 JSON 형식으로 반환합니다.
        """
        if not self.is_divided():
            return self.value,

        result = [self.value]
        for child in self.children:
            result.append(child.saves())
        result = tuple(result)
        return result

    def save(self, filename='out/output.json'):
        """
        트리를 파일로 저장합니다.
        """
        with open(filename, 'w', encoding='utf-8') as file:
            dump(self.saves(), file)

    def save_image(self, filename: str, size: int, *, palette: Optional[dict] = None):
        image = Image.new('RGB', (size, size))
        draw = Draw(image)
        image = self.draw_image(image, draw, 0, 0, palette)

        image.save(filename)

    def draw_image(self, image: Image, draw: Draw, x: int, y: int, palette: Optional[dict] = None, depth: int = 0):
        dimension = image.width // 2 ** depth
        if not self.is_divided():
            color = self.value if palette is None else palette.get(self.value, (0, 255, 0))
            print(x, y, dimension, color)
            draw.rectangle(((x, y), (x+dimension, y+dimension)), color, (0, 255, 0))
            return image

        dimension //= 2
        for i, child in enumerate(self.children):
            iy, ix = divmod(i, 2)
            child.draw_image(image, draw, x + ix * dimension, y + iy * dimension, palette, depth + 1)
        return image

    @staticmethod
    def loads(data: tuple):
        """
        JSON 형식의 트리를 ``QuadTree``로 변환하여 반환합니다.
        """
        result = QuadTree(data[0])
        if len(data) <= 1:
            return result

        children = list()
        for i in range(1, 5):
            children.append(QuadTree.loads(data[i]))
        result.children = tuple(children)

        return result

    @staticmethod
    def load(filename='out/input.json'):
        """
        파일에 저장되어있는 트리를 반환합니다.
        """
        with open(filename, 'r', encoding='utf-8') as file:
            data = load(file)
        return QuadTree.loads(data)

    def apply(self, delta: 'QuadTree') -> 'QuadTree':
        """
        사분트리에 사분트리 차이를 적용한 결과를 출력한다.

        ``self``의 내용을 바꾸지 않고 복사본을 만들어 출력한다.
        """
        result = copy(self)
        if delta.value is not None:
            result.value = delta.value
            result.children = tuple()

        if not delta.is_divided():
            return result

        if not result.is_divided():
            result.divide()

        children = list()
        for i in range(4):
            children.append(result.children[i].apply(delta.children[i]))
        result.children = tuple(children)
        result.simplify_upward()
        return result

    def trace(self, delta: 'QuadTree', *, clone: bool = False) -> 'QuadTree':
        """
        사분트리에 사분트리 차이를 추적한 결과를 출력한다.
        """

        if not clone:
            delta = copy(delta)

        if delta.value is not None:
            delta = copy(self)
            return delta

        if delta.is_divided():
            if originally_combined := not self.is_divided():
                self.divide()

            children = list()
            for i in range(4):
                children.append(self.children[i].trace(delta.children[i], clone=True))
            delta.children = tuple(children)

            if originally_combined:
                self.combine()

        return delta


def _main():
    qt = QuadTree(0)

    qt.path_int_set(0, 0, 1, 1)
    qt.path_int_set(1, 0, 1, 2)
    qt.path_int_set(0, 1, 1, 3)
    qt.path_int_set(1, 1, 1, 4)

    qt.path_int_set(0, 0, 2, 5)
    qt.path_int_set(1, 0, 2, 6)
    qt.path_int_set(0, 1, 2, 7)
    qt.path_int_set(1, 1, 2, 8)

    print(qt)

    qtd = QuadTree(None)
    qtd.path_int_set(2, 3, 2, 1)
    qtd.path_int_set(0, 0, 1, 2)
    print(qtd)

    delta = qt.trace(qtd)
    print(delta)

    result = qt.apply(delta)
    print(result)

    assert qt.is_identical_with(result)


if __name__ == '__main__':
    _main()
