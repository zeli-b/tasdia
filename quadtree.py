import json
from copy import copy
from typing import Union

from PIL import Image, ImageDraw


class Node:
    @staticmethod
    def structify(flattened) -> 'Node':
        return Node(flattened)

    def __init__(self, color):
        self.color = color

    def __eq__(self, other):
        if isinstance(other, Node):
            return all((self.color == other.color,))

        return False

    def __copy__(self):
        return Node(self.color)

    def to_image(self, width: int, height: int = -1, line_color=None):
        if height == -1:
            height = width
        result = Image.new('RGB', (width, height), color=self.color)
        draw = ImageDraw.Draw(result)
        if line_color:
            draw.rectangle((0, 0, width, height), outline=line_color, width=1)
        return result

    def flatten(self):
        return str(self.color)

    def to_quadtree(self) -> 'QuadTree':
        return QuadTree([copy(self) for _ in range(4)])


class QuadTree:
    @staticmethod
    def structify(flattened) -> 'QuadTree':
        children = list()
        for raw_child in flattened:
            children.append(structify(raw_child))
        return QuadTree(children)

    def __init__(self, children: list):
        self.children: list[Union[QuadTree, Node]] = children

    def to_image(self, width: int, height: int = -1, line_color=None):
        if height == -1:
            height = width
        half_width = width // 2
        half_height = height // 2
        result = Image.new('RGB', (width, height))
        for i in range(2):
            for j in range(2):
                image = self.children[2 * j + i].to_image(half_width, half_height, line_color)
                result.paste(image, (half_width * i, half_height * j))
        return result

    def flatten(self) -> list:
        return list(map(lambda x: x.flatten(), self.children))

    def fill(self, address: list, node: Node):
        address = copy(address)
        index = address.pop(0)

        if not len(address):
            self.children[index] = node
            return

        child = self.children[index]
        if not isinstance(child, QuadTree):
            self.children[index] = child.to_quadtree()
        self.children[index].fill(address, node)

        if self.children[index].is_having_same_children():
            self.children[index] = self.children[index].children[0]

    def is_having_same_children(self) -> bool:
        for i in range(3):
            if self.children[i] != self.children[3]:
                return False
        return True


def structify(flattened) -> Union[QuadTree, Node]:
    if isinstance(flattened, str):
        return Node.structify(flattened)
    else:
        return QuadTree.structify(flattened)


def load(filename: str) -> 'QuadTree':
    with open(filename, 'r') as file:
        return structify(json.load(file))


def get_address(x: float, y: float, depth: int) -> list:
    unit = 2 ** (-depth)
    x = int(x / unit)
    y = int(y / unit)

    result = list()
    for _ in range(depth):
        result.insert(0, 2 * (y & 0x1) + (x & 0x1))
        x >>= 1
        y >>= 1

    return result
