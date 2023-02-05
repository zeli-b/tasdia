from urllib.parse import parse_qs, parse_qsl

from flask import Flask, render_template, request

from implementation.quadtree import QuadTree
from tasdia import Map
from tasdia.layer import AreaData, AreaLayer
from tasdia.layer.area_layer import AreaDelta
from util import reveal_color

app = Flask(__name__)

maps: dict[int, Map] = {map_.id: map_ for map_ in (
    Map.load('example/sat_map.json'),
    Map.load('example/damegasique_map.json')
)}


def parse_data(request_) -> dict:
    if request_.content_type == 'application/json':
        return request_.get_json()

    data = request_.get_data(as_text=True)
    if not data:
        return dict()

    return dict(parse_qsl(data, strict_parsing=True))


@app.route('/')
def get_index():
    return render_template('index.html')


@app.route('/map')
def get_map():
    data = parse_qs(request.query_string.decode())
    map_id = data.get('map')

    if isinstance(map_id, list):
        try:
            map_id = int(map_id[0])
        except ValueError:
            return '올바르지 않은 지도 ID 형태', 400
    else:
        return '지도 아이디 주어지지 않음', 400

    if map_id not in maps:
        return '지도 아이디에 해당하는 지도 없음', 404

    return render_template('map.html', map=maps[map_id])


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


@app.route('/api/map/<int:map_id>/area/new', methods=['POST'])
def post_api_map_id_area_new(map_id: int):
    map_ = maps.get(map_id)
    if map_ is None:
        return '지도 아이디에 해당하는 지도 없음', 404

    data = parse_data(request)

    description = data.get('description')
    if description is None:
        return '설명 지정되지 않음', 400

    id_ = map_.get_new_area_id()
    area_layer = AreaLayer(id_, description, dict(), QuadTree(None), list())
    map_.add_area(area_layer)
    map_.save()

    return area_layer.jsonify(), 200


@app.route('/api/map/<int:map_id>/area/<int:area_id>')
def get_api_map_id_area_id(map_id: int, area_id: int):
    if map_id not in maps:
        return '지도 아이디에 해당하는 지도 없음', 404

    layer = maps[map_id].get_area_layer(area_id)
    if layer is None:
        return '영역 아이디에 해당하는 영역 없음', 404

    return layer.jsonify(), 200


@app.route('/api/map/<int:map_id>/area/<int:area_id>/new', methods=['POST'])
def post_api_map_id_area_id_new(map_id: int, area_id: int):
    map_ = maps.get(map_id)
    if map_ is None:
        return '지도 아이디에 해당하는 지도 없음', 404

    area = map_.get_area_layer(area_id)
    if area is None:
        return '영역 아이디에 해당하는 지도 없음', 404

    data = parse_data(request)

    time = data.get('time')
    if time is None:
        return '시점 지정되지 않음', 400
    try:
        time = float(time)
    except ValueError:
        return '올바르지 않은 시점 형태', 400

    delta = data.get('delta')
    if delta is None:
        return '변경사항 지정되지 않음', 400
    delta = QuadTree.loads(delta)

    area_delta = AreaDelta(time, delta)
    area.add_delta(area_delta)
    map_.save()

    return 'OK', 200


@app.route('/api/map/<int:map_id>/area/<int:area_id>/data')
def get_api_map_id_area_id_data(map_id: int, area_id: int):
    if map_id not in maps:
        return '지도 아이디에 해당하는 지도 없음', 404

    layer = maps[map_id].get_area_layer(area_id)
    if layer is None:
        return '영역 아이디에 해당하는 영역 없음', 404

    return dict(map(lambda x: (x[0], x[1].jsonify()), layer.metadata.items()))


@app.route('/api/map/<int:map_id>/area/<int:area_id>/data/new', methods=['POST'])
def post_api_map_id_area_id_data_new(map_id: int, area_id: int):
    map_ = maps.get(map_id)
    if map_ is None:
        return '지도 아이디에 해당하는 지도 없음', 404

    area_layer = map_.get_area_layer(area_id)
    if area_layer is None:
        return '영역 레이어 아이디에 해당하는 레이어 없음', 404

    data = parse_data(request)
    color = data.get('color')
    description = data.get('description')

    if not color:
        return '색 지정되지 않음', 400
    if not description:
        return '설명 지정되지 않음', 400
    try:
        color = reveal_color(color)
    except ValueError:
        return '색 형태 올바르지 않음 ("#RRGGBB" 형태로 주어져야 함)', 400

    id_ = area_layer.get_new_data_id()
    area_data = AreaData(id_, description, color)
    area_layer.add_data(area_data)
    map_.save()

    return area_data.jsonify(), 200


@app.route('/api/map/<int:map_id>/area/<int:area_id>/tree')
def get_api_map_id_area_id_tree(map_id: int, area_id: int):
    if map_id not in maps:
        return '지도 아이디에 해당하는 지도 없음', 404

    layer = maps[map_id].get_area_layer(area_id)
    if layer is None:
        return '영역 아이디에 해당하는 영역 없음', 404

    return str(layer.tree.saves()), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
