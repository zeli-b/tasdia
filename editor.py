from os import mkdir
from os.path import isdir, isfile, join

from flask import Flask, send_file

from const import colors
from quadtree import QuadTree, Node

app = Flask(__name__)

tree = QuadTree([
    Node(colors.SHTELO_VANILLA),
    Node(colors.SHTELO_DOWNY),
    Node(colors.SHTELO_BLACK),
    QuadTree([
        Node(colors.SHTELO_VANILLA),
        QuadTree([
            Node(colors.SHTELO_WHITE),
            Node(colors.SHTELO_WHITE),
            Node(colors.SHTELO_BLACK),
            Node(colors.SHTELO_VANILLA)
        ]),
        Node(colors.SHTELO_DOWNY),
        Node(colors.SHTELO_VANILLA)
    ])
])


@app.route('/image', defaults={'multiplier': 32})
@app.route('/image/<int:multiplier>')
def get_image(multiplier: int):
    size = 2 ** tree.get_depth() * multiplier
    filename = join('out', f'{tree.version}_{size}.png')

    isdir('out') or mkdir('out')
    if not isfile(filename):
        tree.to_image(size).save(filename)
    return send_file(filename, mimetype='image/png')


if __name__ == '__main__':
    if isdir('out'):
        from shutil import rmtree
        rmtree('out')
    app.run(debug=True)
