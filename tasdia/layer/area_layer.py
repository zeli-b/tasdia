from implementation.quadtree import QuadTree
from tasdia.layer import Layer
from util import convert_color, reveal_color


class AreaData:
    @staticmethod
    def loads(data: dict) -> 'AreaData':
        id_ = data.get('id')
        description = data.get('description')
        color = reveal_color(data.get('color'))
        return AreaData(id_, description, color)

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
    @staticmethod
    def loads(data: dict) -> 'AreaLayer':
        id_ = data.get('id')
        description = data.get('description')
        metadata = dict(map(lambda x: (x[0], AreaData.loads(x[1])), data.get('metadata').items()))
        tree = QuadTree.loads(data.get('tree'))
        return AreaLayer(id_, description, metadata, tree)

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
