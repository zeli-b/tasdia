from json import dump

from tasdia.layer import Layer


class Map:
    def __init__(self, id_: int, description: str, layers: list[Layer]):
        self.id = id_
        self.description = description
        self.layers = layers

    def jsonify(self, *, full: bool = False):
        layers = list(map(lambda x: x.jsonify(full=full), self.layers))
        return {
            'id': self.id,
            'description': self.description,
            'layers': layers
        }

    def save(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as file:
            dump(self.jsonify(full=True), file)
