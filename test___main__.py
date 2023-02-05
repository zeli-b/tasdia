from requests import post, JSONDecodeError


def test_new_area():
    print()

    map_id = 0

    data = {'description': '영토'}

    r = post(f'http://localhost:5000/api/map/{map_id}/area/new', data=data)
    try:
        j = r.json()
    except JSONDecodeError:
        print(r.text)
    else:
        print(j)


def test_new_area_data():
    print()

    map_id = 0
    area_id = 1

    data = {'color': '#fdde59', 'description': '자소크 철학단'}

    r = post(f'http://localhost:5000/api/map/{map_id}/area/{area_id}/data/new', data=data)
    try:
        j = r.json()
    except JSONDecodeError:
        print(r.text)
    else:
        print(j)
