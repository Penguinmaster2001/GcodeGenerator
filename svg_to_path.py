import matplotlib.pyplot as plt
import numpy as np
from svgpathtools import svg2paths2

from gcode_types import GcodePoint


colors = ["red", "orange", "yellow", "green", "blue", "purple"]


def generate_path_from_svg(
    svg_path, steps: int, layers: int, settings: dict[str, float]
) -> list[GcodePoint]:
    paths = svg2paths2(svg_path)[0]

    if len(paths) <= 0:
        print("No paths in svg.")
        return []

    lengths = np.array([p.length() for p in paths], dtype=float)
    total = lengths.sum()
    if total == 0:
        return []

    points: list[GcodePoint] = []

    path_x: list[float] = []
    path_y: list[float] = []
    path_num: list[int] = []
    fig = plt.figure()
    ax = fig.add_subplot()

    # for p, path in enumerate(paths):
    #     for t in np.linspace(0.0, 1.0, int(steps / len(paths))):
    for p_idx, (path, L) in enumerate(zip([paths[0]], lengths)):
        # path_x: list[float] = []
        # path_y: list[float] = []
        print(p_idx)
        n = steps # max(2, int(steps * (L / total)))
        ts = np.linspace(0.0, 1.0, n)
        for t in ts:
            pt = path.point(t)
            path_x.append(pt.real)
            path_y.append(settings["bed_depth"] - pt.imag)
            path_num.append(p_idx)

        pt = path.point(0.0)
        path_x.append(pt.real)
        path_y.append(settings["bed_depth"] - pt.imag)
        path_num.append(p_idx)

        # ax.scatter(x, y, z)
        # ax.plot_surface(x, y, z)
        ax.plot(path_x, path_y, color=colors[p_idx], alpha=0.4)
        # ax.plot3D(x, y, z)

    ax.set_aspect("equal")
    plt.show()

    for layer in range(layers):
        last_p = path_num[0]
        for p_idx, (x, y, p) in enumerate(zip(path_x, path_y, path_num[1:-1])):
            points.append(GcodePoint(x, y, layer, p_idx > 0 and last_p == p))
            last_p = p

    print(len(points))
    return points
