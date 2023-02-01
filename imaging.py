from math import log2

from PIL import Image

import quadtree


def image_to_quadtree(input_filename: str, output_filename: str):
    qt = quadtree.QuadTree(0)

    image = Image.open(input_filename)
    pixels = list(image.getdata())
    width, height = image.size
    pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
    unit = int(log2(width))

    for i in range(height):
        print(i, i/height*100)
        y = quadtree.path_int_to_pos(i, unit)
        for j in range(width):
            x = quadtree.path_int_to_pos(j, unit)

            color = pixels[i][j][0]
            color = 1 - round(color / 255)
            if color:
                qt.set(x, y, unit, color)

    qt.save(output_filename)
    print(qt)


def quadtree_to_image(input_filename: str, output_filename: str, size):
    qt = quadtree.QuadTree.load(input_filename)
    print(qt)

    qt.save_image(output_filename, size, palette={1: (0, 0, 0), 0: (255, 255, 255)})


if __name__ == '__main__':
    image_to_quadtree('out/sat_image.png', 'out/sat_quadtree.json')
    quadtree_to_image('out/sat_quadtree.json', 'out/sat_quadtree_visualize.png', 2048)
