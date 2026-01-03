import numpy as np
from svgpathtools import svg2paths2

from gcode_types import GcodePoint


def generate_path_from_svg(
    svg_path, steps: int, layers: int, settings: dict[str, float]
) -> list[GcodePoint]:
    paths = svg2paths2(svg_path)[0]

    if len(paths) <= 0:
        print("No paths in svg.")
        return []

    points: list[GcodePoint] = []

    path_x: list[float] = []
    path_y: list[float] = []
    path_num: list[int] = []

    for p, path in enumerate(paths):
        for t in np.linspace(0.0, 1.0, int(steps / len(paths))):
            pt = path.point(t)
            path_x.append(pt.real)
            path_y.append(settings["bed_depth"] - pt.imag)
            path_num.append(p)

        pt = path.point(0.0)
        path_x.append(pt.real)
        path_y.append(settings["bed_depth"] - pt.imag)
        path_num.append(p)

    for layer in range(layers):
        last_p = path_num[0]
        for x, y, p in zip(path_x, path_y, path_num[1:-1]):
            points.append(GcodePoint(x, y, layer, last_p == p))
            last_p = p

    print(len(points))
    return points
