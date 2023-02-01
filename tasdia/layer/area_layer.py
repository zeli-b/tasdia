from quadtree import QuadTree
from tasdia.layer import Layer
from util import convert_color


class AreaData:
    def __init__(self, id_: int, description: str, color: tuple):
        self.id = id_
        self.description = description
        self.color = color

    def jsonify(self):
        return {
            'id': self.id,
            'description': self.description,
            'color': convert_color(self.color)
        }


class AreaLayer(Layer):
    def __init__(self, id_: int, description: str, metadata: list[AreaData], tree: QuadTree):
        self.id = id_
        self.description = description
        self.metadata = metadata
        self.tree = tree

    def jsonify(self) -> dict:
        metadata = list(map(AreaData.jsonify, self.metadata))
        return {
            'id': self.id,
            'description': self.description,
            'metadata': metadata,
            'tree': self.tree.saves()
        }
