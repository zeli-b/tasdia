from flask import Flask, render_template

from tasdia import Map

app = Flask(__name__)

maps: dict[int, Map] = {map_.id: map_ for map_ in (
    Map.load('example/sat_map.json'),
)}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/map')
def get_api_map():
    return {k: v.jsonify() for k, v in maps.items()}, 200


@app.route('/api/map/<int:map_id>')
def get_api_map_id(map_id: int):
    if map_id not in maps:
        return '지도 아이디에 해당하는 지도 없음', 404

    return maps[map_id].jsonify(), 200


@app.route('/api/map/<int:map_id>/area')
def get_api_map_id_area(map_id: int):
    if map_id not in maps:
        return '지도 아이디에 해당하는 지도 없음', 404

    return [layer.jsonify() for layer in maps[map_id].area_layers], 200


@app.route('/api/map/<int:map_id>/area/<int:area_id>')
def get_api_map_id_area_id(map_id: int, area_id: int):
    if map_id not in maps:
        return '지도 아이디에 해당하는 지도 없음', 404

    layer = maps[map_id].get_area_layer(area_id)
    if layer is None:
        return '영역 아이디에 해당하는 영역 없음', 404

    return layer.jsonify(), 200


@app.route('/api/map/<int:map_id>/area/<int:area_id>/data')
def get_api_map_id_area_id_data(map_id: int, area_id: int):
    if map_id not in maps:
        return '지도 아이디에 해당하는 지도 없음', 404

    layer = maps[map_id].get_area_layer(area_id)
    if layer is None:
        return '영역 아이디에 해당하는 영역 없음', 404

    return dict(map(lambda x: (x[0], x[1].jsonify()), layer.metadata.items()))


@app.route('/api/map/<int:map_id>/area/<int:area_id>/tree')
def get_api_map_id_area_id_tree(map_id: int, area_id: int):
    if map_id not in maps:
        return '지도 아이디에 해당하는 지도 없음', 404

    layer = maps[map_id].get_area_layer(area_id)
    if layer is None:
        return '영역 아이디에 해당하는 영역 없음', 404

    return str(layer.tree.saves()), 200


if __name__ == '__main__':
    app.run(debug=True)
