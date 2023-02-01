from json import dump, load

from tasdia.layer import AreaLayer


class Map:
    def __init__(self, id_: int, description: str, area_layers: list[AreaLayer]):
        self.id = id_
        self.description = description
        self.area_layers = area_layers

    def get_area_layer(self, id_: int):
        for layer in self.area_layers:
            if id_ == layer.id:
                return layer

    def jsonify(self, *, full: bool = False):
        area_layers = list(map(lambda x: x.jsonify(full=full), self.area_layers))
        return {
            'id': self.id,
            'description': self.description,
            'area_layers': area_layers
        }

    def save(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as file:
            dump(self.jsonify(full=True), file, indent=1, ensure_ascii=False)

    @staticmethod
    def load(filename: str) -> 'Map':
        with open(filename, 'r', encoding='utf-8') as file:
            data = load(file)
        return Map.loads(data)

    @staticmethod
    def loads(data: dict) -> 'Map':
        id_ = data.get('id')
        description = data.get('description')
        area_layers = list(map(AreaLayer.loads, data.get('area_layers')))
        return Map(id_, description, area_layers)
