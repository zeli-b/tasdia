from json import dump, load
from typing import Optional

from tasdia.layer import AreaLayer


class Map:
    def __init__(self, id_: int, description: str, area_layers: list[AreaLayer], save_path: Optional[str]):
        self.id = id_
        self.description = description
        self.area_layers = area_layers
        self.save_path = save_path

    def get_area_layer(self, id_: int) -> AreaLayer:
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

    def get_new_area_id(self) -> int:
        return max(map(lambda x: x.id, self.area_layers)) + 1

    def add_area(self, area_layer: AreaLayer) -> 'Map':
        self.area_layers.append(area_layer)
        return self

    def save(self, filename: Optional[str] = None):
        if filename is None:
            filename = self.save_path
        if self.save_path is None:
            raise ValueError('저장 위치가 지정되지 않음')
        with open(filename, 'w', encoding='utf-8') as file:
            dump(self.jsonify(full=True), file, indent=1, ensure_ascii=False)

    @staticmethod
    def load(filename: str) -> 'Map':
        with open(filename, 'r', encoding='utf-8') as file:
            data = load(file)
        return Map.loads(data, filename)

    @staticmethod
    def loads(data: dict, save_path: Optional[str] = None) -> 'Map':
        id_ = data.get('id')
        description = data.get('description')
        area_layers = list(map(AreaLayer.loads, data.get('area_layers')))
        return Map(id_, description, area_layers, save_path)
