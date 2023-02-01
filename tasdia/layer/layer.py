class Layer:
    def jsonify(self) -> dict:
        raise NotImplementedError

    @staticmethod
    def loads(data: dict):
        raise NotImplementedError
