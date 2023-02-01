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
    def __init__(self, id_: int, description: str, metadata: dict[int, AreaData], tree: QuadTree):
        self.id = id_
        self.description = description
        self.metadata = metadata
        self.tree = tree

    def jsonify(self, *, full: bool = False) -> dict:
        metadata = dict(map(lambda x: (x[0], x[1].jsonify()), self.metadata.items()))
        result = {
            'id': self.id,
            'description': self.description,
            'metadata': metadata
        }

        if full:
            result['tree'] = self.tree.saves()

        return result
