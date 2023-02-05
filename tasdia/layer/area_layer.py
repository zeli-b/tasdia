from implementation.quadtree import QuadTree
from tasdia.layer import Layer
from util import convert_color, reveal_color


class AreaData:
    """
    ``AreaData``는 영역 레이어에 나타난 자료들에 대한 세부적인 정보를 제공한다.
    영역 레이어 ``tree``의 각각 영역은 서로 구분되는 정수만을 가지고 있는데,
    ``AreaData``가 해당 정수를 두고 무슨 의미를 가지는지 나타내는 역할을 하는 것이다.
    """

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


class AreaDelta:
    @staticmethod
    def loads(data: dict) -> 'AreaDelta':
        time = data.get('time')
        delta = QuadTree.loads(data.get('delta'))
        return AreaDelta(time, delta)

    def __init__(self, time: float, delta: QuadTree):
        self.time = time
        self.delta = delta

    def jsonify(self):
        delta = self.delta.saves()

        return {
            'time': self.time,
            'delta': delta
        }


class AreaLayer(Layer):
    @staticmethod
    def loads(data: dict) -> 'AreaLayer':
        id_ = data.get('id')
        description = data.get('description')
        metadata = dict(map(lambda x: (x[0], AreaData.loads(x[1])), data.get('metadata').items()))
        tree = QuadTree.loads(data.get('tree'))
        deltas = list(map(AreaDelta.loads, data.get('deltas')))
        return AreaLayer(id_, description, metadata, tree, deltas)

    def __init__(self, id_: int, description: str, metadata: dict[int, AreaData],
                 tree: QuadTree, deltas: list[AreaDelta]):
        self.id = id_
        self.description = description
        self.metadata = metadata
        self.tree = tree
        self.deltas = deltas

    def jsonify(self, *, full: bool = False) -> dict:
        metadata = dict(map(lambda x: (x[0], x[1].jsonify()), self.metadata.items()))
        result = {
            'id': self.id,
            'description': self.description,
            'metadata': metadata
        }

        if full:
            result['tree'] = self.tree.saves()
            result['deltas'] = list(map(AreaDelta.jsonify, self.deltas))

        return result

    def get_new_data_id(self) -> int:
        try:
            return max(map(lambda x: x.id, self.metadata.values())) + 1
        except ValueError:
            return 0

    def add_data(self, area_data: AreaData) -> 'AreaLayer':
        if area_data.id in self.metadata:
            raise ValueError('이미 존재하는 AreaData ID')

        self.metadata[area_data.id] = area_data
        return self
