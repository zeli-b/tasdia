from tasdia.layer import Layer


class Map:
    def __init__(self, id_: int, description: str, layers: list[Layer]):
        self.id = id_
        self.description = description
        self.layers = layers

    def jsonify(self):
        layers = list(map(lambda x: x.jsonify(), self.layers))

        return {
            'id': self.id,
            'description': self.description,
            'layers': layers
        }
