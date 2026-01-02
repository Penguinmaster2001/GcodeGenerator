import numpy as np
from svgpathtools import svg2paths2


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


def generate_path_from_svg(svg_path, steps: int, layers: int, settings: dict[str, float]):
    paths = svg2paths2(svg_path)[0]

    # path = paths[0]

    x: list[float] = []
    y: list[float] = []
    z: list[float] = []

    for path in paths:
        for t in np.linspace(0.0, 1.0, steps):
            pt = path.point(t)
            x.append(pt.real)
            y.append(settings["bed_depth"] - pt.imag)

        # pt = path.point(0.0)
        # x.append(pt.real)
        # y.append(pt.imag)

    z.extend(np.full(len(x), 0.2))
    
    return np.array(x), np.array(y), np.array(z)

    # print(path.point(0.0))
    # print(path.point(1.0))
    # print(path.point(100.0))

    # tvals = np.linspace(0, 1, 10)

    # pts = points_in_each_seg(paths[0], tvals)

    # print(
    #     ",".join([f"({p.real:.2f},{p.imag:.2f})" for sublist in pts for p in sublist])
    # )
