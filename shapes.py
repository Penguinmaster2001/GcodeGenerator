#! /bin/python


import re
import sys
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import numpy as np
from numpy.typing import NDArray

import svg_to_path

mplstyle.use(["dark_background", "ggplot", "fast"])


settings = {
    "bed_width": 200.0,
    "bed_depth": 200.0,
    "flow_rate": 0.50,
    "first_layer_height": 0.2,
    "layer_height": 0.1,
}


def display(x, y, z):
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    # ax.scatter(x, y, z)
    # ax.plot_surface(x, y, z)
    ax.plot(x, y, z)
    # ax.plot3D(x, y, z)

    ax.set_aspect("equal")
    plt.show()


def curve():
    def r1(theta, height):
        return 1.5 + (1.2 * np.cos(3.0 * theta))

    def r2(theta, height):
        return (
            (2.0 + (1.1 * (np.sin(3.0 * theta + 0.1 * height) ** 3.0))) ** 2.0
        ) / 5.0

    def r3(theta, height):
        return 2.0 * (1.0 + (((2.0 * height / 20.0) - 1.0) * np.cos(theta)))

    return polar(200, 200, 8.0, 200, 200, r3)


def polar(
    steps: int, layers: int, scale: float, width: float, depth: float, radius_func
) -> tuple[NDArray, NDArray, NDArray]:
    theta = np.linspace(0, 2 * np.pi, steps)

    x: list[float] = []
    y: list[float] = []
    z: list[float] = []

    print(f"Height: {layers * settings['layer_height']}")

    for h in np.linspace(
        settings["first_layer_height"],
        settings["first_layer_height"] + (layers * settings["layer_height"]),
        layers,
        endpoint=False,
    ):
        x.extend((scale * radius_func(theta, h) * np.cos(theta)) + (0.5 * width))
        y.extend((scale * radius_func(theta, h) * np.sin(theta)) + (0.5 * depth))
        z.extend(np.full(steps, h))

    return np.array(x), np.array(y), np.array(z)


pattern = re.compile(
    r"^(?:G0|G1)\s*"
    r"(?P<x>X(-?\d+(?:\.\d+)?)\s*)?"
    r"(?P<y>Y(-?\d+(?:\.\d+)?)\s*)?"
    r"(?P<z>Z(-?\d+(?:\.\d+)?)\s*)?"
    r"(?P<e>E(-?\d+(?:\.\d+)?)\s*)?"
    r"$"
)


def match_xyz(line: str):
    m = pattern.fullmatch(line.strip())
    if m is None:
        return None  # no match

    def extract(key):
        val = m.group(key)  # e.g. "X12.34" or None
        if val is None:
            return None
        # remove the leading letter and convert to float if possible
        num = val[1:]
        if num == "":
            return None
        try:
            return float(num)
        except ValueError:
            return None

    return [extract("x"), extract("y"), extract("z"), extract("e")]


def display_gcode_file(path):
    x = [0.0]
    y = [0.0]
    z = [0.0]

    ave_ratio = 0.0
    num_ratio = 0

    with open(path) as f:
        for line in f.readlines():
            m = match_xyz(line)
            if m is not None:
                val = m[0]
                if val is None:
                    val = x[-1]
                x.append(val)

                val = m[1]
                if val is None:
                    val = y[-1]
                y.append(val)

                val = m[2]
                if val is None:
                    val = z[-1]
                z.append(val)

                val = m[3]
                if val is not None and val > 0.0:
                    dx = x[-1] - x[-2]
                    dy = y[-1] - y[-2]

                    length = np.sqrt((dx * dx) + (dy * dy))
                    if length > 0.001:
                        ave_ratio += val / length
                        num_ratio += 1

    print(len(x))
    if num_ratio > 0:
        print(ave_ratio / num_ratio)

    display(x, y, z)


def display_curve(_):
    x, y, z = curve()
    display(x, y, z)


def generate_gcode(path):
    x, y, z = curve()

    text = ""
    with open("Fragments/starter.gcode", "r") as f:
        text += f.read()
    text += "\n\n\n;START\n"

    lx: float = x[0]
    ly: float = y[0]
    lz: float = z[0]
    for cx, cy, cz in zip(x, y, z):
        if cx < 0.0:
            cx = 0
        elif cx > settings["bed_width"]:
            cx = 200.0

        if cy < 0.0:
            cy = 0
        elif cy > settings["bed_depth"]:
            cy = 200.0

        if cz < 0.0:
            cz = 0
        elif cz > 200.0:
            cz = 200.0

        extrude: float = 0.0
        vals = []
        if not np.isclose(cx, lx, atol=0.001):
            vals.append(f"X{cx:.3f}")
            extrude += (cx - lx) ** 2.0

        if not np.isclose(cy, ly, atol=0.001):
            vals.append(f"Y{cy:.3f}")
            extrude += (cy - ly) ** 2.0

        if not np.isclose(cz, lz, atol=0.001):
            vals.append(f"Z{cz:.3f}")
            extrude += (cz - lz) ** 2.0

        extrude = settings["flow_rate"] * np.sqrt(extrude)
        # If no extrusion, ignore
        if not np.isclose(extrude, 0.0, atol=0.001):
            vals.append(f"E{extrude:.3f}")

            text += f"G1 {' '.join(vals)}\n"

            lx = cx
            ly = cy
            lz = cz

    with open("Fragments/finisher.gcode", "r") as f:
        text += "\n;END\n\n\n"
        text += f.read()

    with open(path, "w") as f:
        f.write(text)


def display_svg(path):
    x, y, z = svg_to_path.generate_path_from_svg(path, 200, 200, settings)
    display(x, y, z)


commands: dict[str, tuple[Any, int]] = {
    "disp": (display_gcode_file, 1),
    "disp-curve": (display_curve, 1),
    "gen": (generate_gcode, 1),
    "disp-svg": (display_svg, 1),
}


if len(sys.argv) <= 2:
    print(f"Usage: {sys.argv[0]} <command> <file>")
    exit(1)

command_name = sys.argv[1]
file = sys.argv[2]

command = commands.get(command_name)
if command is None:
    print(f'command unknown "{command_name}"')
    exit(2)

command[0](file)
