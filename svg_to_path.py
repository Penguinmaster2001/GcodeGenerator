import numpy as np
from svgpathtools import svg2paths2

from gcode_types import GcodePoint


def points_in_each_seg(path, tvals):
    """Compute seg.point(t) for each seg in path and each t in tvals."""
    A = np.array(
        [
            [-1, 3, -3, 1],  # transforms cubic bez to standard poly
            [3, -6, 3, 0],
            [-3, 3, 0, 0],
            [1, 0, 0, 0],
        ]
    )
    B = [seg.bpoints() for seg in path]
    return np.dot(B, np.dot(A, np.power(tvals, [[3], [2], [1], [0]])))


def generate_path_from_svg(
    svg_path, steps: int, layers: int, settings: dict[str, float]
) -> list[GcodePoint]:
    paths = svg2paths2(svg_path)[0]

    if len(paths) <= 0:
        print("No paths in svg.")
        return []

    points: list[GcodePoint] = []

    # path = paths[0]

    path_x: list[float] = []
    path_y: list[float] = []
    path_num: list[int] = []

    for p, path in enumerate(paths):
        for t in np.linspace(0.0, 1.0, int(steps / len(paths))):
            pt = path.point(t)
            path_x.append(pt.real)
            path_y.append(settings["bed_depth"] - pt.imag)
            path_num.append(p)

        # pt = path.point(0.0)
        # x.append(pt.real)
        # y.append(pt.imag)

    for layer in range(layers):
        last_p = path_num[0]
        for x, y, p in zip(path_x, path_y, path_num[1:-1]):
            points.append(GcodePoint(x, y, layer, last_p == p))
            last_p = p

    print(len(points))
    return points

    # print(path.point(0.0))
    # print(path.point(1.0))
    # print(path.point(100.0))

    # tvals = np.linspace(0, 1, 10)

    # pts = points_in_each_seg(paths[0], tvals)

    # print(
    #     ",".join([f"({p.real:.2f},{p.imag:.2f})" for sublist in pts for p in sublist])
    # )
